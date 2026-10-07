from app.rag import retrieve, split_text
from app.workflow import evaluate


def test_split_text_rejects_invalid_overlap():
    try:
        split_text("hello", chunk_size=10, overlap=10)
        assert False
    except ValueError:
        assert True


def test_retrieve_returns_matching_document_first():
    result = retrieve("approved colors", ["Use approved colors: brown and cream.", "Unrelated launch text."])
    assert result[0]["score"] > result[1]["score"]


def test_evaluator_detects_forbidden_words():
    brand = {"forbidden_words": ["cure"]}
    assets = [{"caption": "This product can cure anything"}]
    result = evaluate(brand, assets)
    assert result["passed"] is False
