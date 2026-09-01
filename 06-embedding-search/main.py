import math
import os
from pathlib import Path

from openai import OpenAI

client = OpenAI()

EMBED_MODEL = os.getenv(
    "OPENAI_EMBED_MODEL",
    "text-embedding-3-small",
)

ROOT = Path(__file__).resolve().parent.parent

SOURCE_DIRS = [
    "01-minimal-agent",
    "02-tool-calling",
    "03-Agent-loop",
    "04-research-planner",
    "05-research-loop",
]


def load_chunks() -> list[dict]:

    chunks = []
    for directory in SOURCE_DIRS:
        path = ROOT / directory / "README.md"

        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")

        paragraphs = text.split("\n\n")

        for index, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()

            if len(paragraph) < 30:
                continue

            chunks.append(
                {
                    "source": str(path.relative_to(ROOT)),
                    "chunk_id": index,
                    "text": paragraph,
                }
            )

    return chunks


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)

    return [item.embedding for item in response.data]


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:

    dot_product = sum(x * y for x, y in zip(a, b, strict=False))

    norm_a = math.sqrt(sum(x * x for x in a))

    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def build_index() -> list[dict]:
    chunks = load_chunks()

    texts = [chunk["text"] for chunk in chunks]

    print(f"Embedding {len(texts)} chunks")

    vectors = embed_texts(texts)

    for chunk, vector in zip(
        chunks,
        vectors,
        strict=False,
    ):
        chunk["embedding"] = vector

    return chunks


def semantic_search(
    query: str,
    index: list[dict],
    top_k: int = 3,
) -> list[dict]:

    query_vector = embed_texts([query])[0]

    results = []

    for chunk in index:
        score = cosine_similarity(query_vector, chunk["embedding"])

        results.append(
            {
                "score": score,
                "source": chunk["source"],
                "text": chunk["text"],
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]


def keyword_search(query: str, chunks: list[dict]) -> list[dict]:

    query_words = set(query.lower().split())

    results = []

    for chunk in chunks:
        text_words = set(chunk["text"].lower().split())

        score = len(query_words & text_words)

        results.append(
            {
                "score": score,
                "source": chunk["source"],
                "text": chunk["text"],
            }
        )

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )[:3]


if __name__ == "__main__":
    print("Building semantic index...")

    index = build_index()

    print(f"Indexed {len(index)} chunks")

    query = input("\nQuestion: ")

    results = semantic_search(
        query,
        index,
        top_k=3,
    )
    """
    results = keyword_search(
        query,
        index,
    )
    """
    print("\n=== Top Results ===")

    for rank, result in enumerate(results, start=1):
        print(f"\n#{rank}")

        print(f"Score: {result['score']:.4f}")

        print(f"Source: {result['source']}")

        print(result["text"])


"""
vectors = embed_texts(
    [
        "AI agents can use tools.",
        "Bananas are yellow.",
    ]
)

print(
    len(vectors)
)

print(
    len(vectors[0])
)

print(
    vectors[0][:5]
)


chunks = load_chunks()

print(f"Loaded {len(chunks)} chunks")


for chunk in chunks[:5]:
    print(chunk)
"""
