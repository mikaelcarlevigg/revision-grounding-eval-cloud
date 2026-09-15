import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data")
MODEL_NAME = "./all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_embeddings():
    with open(DATA_DIR / "embeddings_light.json", encoding="utf-8") as f:
        return json.load(f)


def load_status():
    with open(DATA_DIR / "revision-status.json", encoding="utf-8") as f:
        return json.load(f)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def top_k(query_vector, sections, k=5):
    scored = [(dot(query_vector, s["embedding"]), s) for s in sections]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


def search(query_text, revision_date, k=5):
    model = get_model()
    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()

    all_sections = load_embeddings()
    status = load_status()

    revision_sections = [s for s in all_sections if s["revision_date"] == revision_date]
    best_matches = top_k(query_vector, revision_sections, k)

    results = []
    for score, section in best_matches:
        sec_id = section["identifier"]
        rev_status = status.get(sec_id, {}).get("status", "unknown")
        results.append({
            "identifier": sec_id,
            "heading": section["heading"],
            "body": section["body"],
            "score": score,
            "revision_status": rev_status,
            "revision_gate_flag": rev_status == "changed",
        })
    return results


def compare_revisions(query_text, k=5, revision_dates=("2017-01-01", "2021-04-21")):
    return {rd: search(query_text, rd, k) for rd in revision_dates}