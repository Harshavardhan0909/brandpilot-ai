from typing import Any
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .database import connect, init_db, new_id, now
from .workflow import run_workflow

app = FastAPI(title="BrandPilot AI", version="0.1.0")


class BrandCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10)
    industry: str
    target_audience: str
    tone_of_voice: list[str] = ["friendly", "modern"]
    primary_colors: list[str] = ["#111827"]
    forbidden_words: list[str] = []
    preferred_words: list[str] = []


class CampaignCreate(BaseModel):
    brand_id: str
    objective: str = Field(min_length=5)
    product: str = Field(min_length=2)
    audience: str = Field(min_length=2)
    platform: str = "Instagram"


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "brandpilot-api"}


@app.post("/brands")
def create_brand(payload: BrandCreate):
    brand_id = new_id("brand")
    with connect() as db:
        db.execute(
            "INSERT INTO brands VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (brand_id, payload.name, payload.description, payload.industry,
             payload.target_audience, json.dumps(payload.tone_of_voice),
             json.dumps(payload.primary_colors), json.dumps(payload.forbidden_words),
             json.dumps(payload.preferred_words), now()),
        )
    return {"id": brand_id, **payload.model_dump()}


@app.get("/brands/{brand_id}")
def get_brand(brand_id: str):
    with connect() as db:
        row = db.execute("SELECT * FROM brands WHERE id = ?", (brand_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Brand not found")
    return dict(row)


@app.post("/brands/{brand_id}/guidelines")
def add_guidelines(brand_id: str, content: str):
    with connect() as db:
        if not db.execute("SELECT id FROM brands WHERE id = ?", (brand_id,)).fetchone():
            raise HTTPException(404, "Brand not found")
        guideline_id = new_id("guide")
        db.execute("INSERT INTO guidelines VALUES (?, ?, ?, ?, ?)", (guideline_id, brand_id, "inline-text", content, now()))
    return {"id": guideline_id, "brand_id": brand_id, "characters": len(content)}


@app.post("/campaigns")
def create_campaign(payload: CampaignCreate):
    campaign_id = new_id("campaign")
    with connect() as db:
        if not db.execute("SELECT id FROM brands WHERE id = ?", (payload.brand_id,)).fetchone():
            raise HTTPException(404, "Brand not found")
        db.execute(
            "INSERT INTO campaigns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (campaign_id, payload.brand_id, payload.objective, payload.product,
             payload.audience, payload.platform, "draft", None, now()),
        )
    return {"id": campaign_id, "status": "draft", **payload.model_dump()}


def row_to_brand(row: Any) -> dict:
    result = dict(row)
    for key in ["tone_of_voice", "primary_colors", "forbidden_words", "preferred_words"]:
        result[key] = json.loads(result[key])
    return result


@app.post("/campaigns/{campaign_id}/run")
def run_campaign(campaign_id: str):
    with connect() as db:
        campaign = db.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
        if not campaign:
            raise HTTPException(404, "Campaign not found")
        brand_row = db.execute("SELECT * FROM brands WHERE id = ?", (campaign["brand_id"],)).fetchone()
        guide = db.execute("SELECT content FROM guidelines WHERE brand_id = ? ORDER BY created_at DESC LIMIT 1", (campaign["brand_id"],)).fetchone()
    brand = row_to_brand(brand_row)
    brief = {"objective": campaign["objective"], "product": campaign["product"], "audience": campaign["audience"], "platform": campaign["platform"]}
    result = run_workflow(brand, brief, guide["content"] if guide else "No guideline document uploaded yet.")
    with connect() as db:
        db.execute("UPDATE campaigns SET status = ?, result_json = ? WHERE id = ?", (result["status"], json.dumps(result), campaign_id))
    return {"campaign_id": campaign_id, **result}


@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str):
    with connect() as db:
        row = db.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Campaign not found")
    result = dict(row)
    result["result"] = json.loads(result.pop("result_json")) if result["result_json"] else None
    return result
