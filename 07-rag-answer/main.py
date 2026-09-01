import math
import os
from pathlib import Path

from openai import OpenAI

client = OpenAI()

EMBED_MODEL = os.getenv(
    "OPENAI_EMBED_MODEL",
    "text-embedding-3-small",
)

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
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

        sections = text.split("\n##")

        for index, section in enumerate(sections):
            section = section.strip()

            if index > 0:
                section = "## " + section

            # Do not index learning questions
            if section.lower().startswith("## question for"):
                continue

            if len(section) < 30:
                continue

            chunks.append(
                {
                    "source": str(path.relative_to(ROOT)),
                    "chunk_id": index,
                    "text": section,
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

    diverse_results = []

    seen_sources = set()

    for result in results:
        source = result["source"]

        if source in seen_sources:
            continue

        diverse_results.append(result)

        seen_sources.add(source)

        if len(diverse_results) >= top_k:
            break

    return diverse_results


def build_context(
    results: list[dict],
) -> str:
    parts = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        parts.append(
            f"""
SOURCE {index}

File:
{result["source"]}

Content:
{result["text"]}
""".strip()
        )

    return "\n\n---\n\n".join(parts)


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


def answer_with_rag(
    question: str,
    results: list[dict],
) -> str:

    context = build_context(results)

    prompt = f"""
  You are answering questions about my AI agent learning project

  Use ONLY the supplied CONTEXT.

  Rules:
  1. Do not use outside knowledge.
  2. Do not invent facts.
  3. If the context does not contain enough information to answer,
  reply exactly:
     I don't have enough information in the retrieved notes.
  4. Keep the answer concise.
  5. End with a source section.
  6. Only cite files that actually support the answer.

  Question:
  {question}

   Context:
   {context}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text


def ask_knowledge_base(
    question: str,
    index: list[dict],
) -> str:

    results = semantic_search(
        question,
        index,
        top_k=5,
    )

    print("\n=== Retrieved Context ===")

    for result in results:
        print(f"\nScore: {result['score']:.4f}")

        print(f"\nSource: {result['source']}")

        print("\nChunk: ")
        print(result["text"][:500])
    return answer_with_rag(question, results)


if __name__ == "__main__":
    print("Building knowledge  index...")

    index = build_index()

    print(f"Indexed {len(index)} chunks")

    query = input("\nQuestion: ")

    answer = ask_knowledge_base(query, index)

    print("\n=== Answer === \n")

    print(answer)
