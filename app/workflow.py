import re
from typing import Any

from .rag import retrieve


class MockImageProvider:
    def generate(self, prompt: str) -> dict[str, Any]:
        return {
            "provider": "mock",
            "status": "completed",
            "image_url": "https://placehold.co/1024x1024/png?text=BrandPilot+Preview",
            "prompt": prompt,
        }


def make_plan(brand: dict, brief: dict, rules: list[dict]) -> dict:
    return {
        "campaign_name": f"{brief['product']} — {brief['platform']} launch",
        "core_message": f"{brief['product']} for {brief['audience']}",
        "content_pillars": ["Product value", "Daily ritual", "Brand story"],
        "brand_constraints_used": [rule["text"] for rule in rules if rule["score"] > 0][:4],
        "assets": [
            {"format": "social_post", "platform": brief["platform"], "purpose": "awareness"},
            {"format": "social_post", "platform": brief["platform"], "purpose": "engagement"},
            {"format": "social_post", "platform": brief["platform"], "purpose": "conversion"},
        ],
    }


def create_copy(brand: dict, brief: dict, plan: dict) -> list[dict]:
    tone = ", ".join(brand["tone_of_voice"])
    return [
        {
            "caption": f"Meet {brief['product']}: a {tone.lower()} choice for {brief['audience']}. Discover your next everyday ritual.",
            "hashtags": [f"#{brand['name'].replace(' ', '')}", f"#{brief['platform']}", "#BrandStory"],
        },
        {
            "caption": f"A better moment starts with {brief['product']}. Made for the way {brief['audience']} live, work and create.",
            "hashtags": [f"#{brand['name'].replace(' ', '')}", "#MadeForToday", "#NewLaunch"],
        },
        {
            "caption": f"Your next campaign moment is here. Explore {brief['product']} and make it part of your routine.",
            "hashtags": [f"#{brand['name'].replace(' ', '')}", "#ExploreMore", "#Marketing"],
        },
    ]


def visual_prompt(brand: dict, brief: dict, index: int) -> str:
    colors = ", ".join(brand["primary_colors"])
    return (
        f"Marketing visual {index + 1} for {brand['name']}. Product: {brief['product']}. "
        f"Audience: {brief['audience']}. Platform: {brief['platform']}. "
        f"Use approved brand colors {colors}. Style should be modern, clean and on-brand. "
        "Do not add unapproved logos, fake claims or competitor branding."
    )


def evaluate(brand: dict, assets: list[dict]) -> dict:
    forbidden = [word.lower() for word in brand["forbidden_words"]]
    checks = []
    for asset in assets:
        caption = asset["caption"].lower()
        matches = [word for word in forbidden if word and word in caption]
        checks.append({
            "name": "forbidden_words",
            "passed": not matches,
            "score": 1.0 if not matches else 0.0,
            "details": f"Found: {matches}" if matches else "No forbidden words found",
        })
    passed = all(check["passed"] for check in checks)
    return {"passed": passed, "overall_score": 1.0 if passed else 0.0, "checks": checks}


def run_workflow(brand: dict, brief: dict, guideline_text: str) -> dict:
    chunks = [guideline_text]
    rules = retrieve(f"{brief['objective']} {brief['product']} {brief['platform']}", chunks)
    plan = make_plan(brand, brief, rules)
    copy_assets = create_copy(brand, brief, plan)
    provider = MockImageProvider()
    assets = []
    for index, copy in enumerate(copy_assets):
        prompt = visual_prompt(brand, brief, index)
        assets.append({**copy, "visual_prompt": prompt, "image": provider.generate(prompt)})
    evaluation = evaluate(brand, assets)
    return {"plan": plan, "assets": assets, "evaluation": evaluation, "status": "approved" if evaluation["passed"] else "needs_revision"}
