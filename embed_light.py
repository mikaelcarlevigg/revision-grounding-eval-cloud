import json
import glob
from pathlib import Path
from sentence_transformers import SentenceTransformer

MODEL_NAME = "./all-MiniLM-L6-v2"
OUTPUT_FILE = Path("data/embeddings_light.json")


def load_sections(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    model = SentenceTransformer(MODEL_NAME)
    all_sections = []

    section_files = sorted(glob.glob("data/sections-*.json"))
    if not section_files:
        print("Hittade inga filer som matchar data/sections-*.json")
        return

    for path in section_files:
        print(f"Läser {path}")
        sections = load_sections(path)
        texts = [s["body"] for s in sections]
        vectors = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        for section, vector in zip(sections, vectors):
            section["embedding"] = vector.tolist()
            all_sections.append(section)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_sections, f, ensure_ascii=False)

    print(f"Klart: {len(all_sections)} sektioner embeddade, sparade i {OUTPUT_FILE}")


if __name__ == "__main__":
    main()