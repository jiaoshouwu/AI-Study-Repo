import math
import os

import hashlib
import json

from pathlib import Path
from openai  import OpenAI

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

APP_DIR = Path(__file__).resolve().parent
CACHE_DIR = APP_DIR / "cache"
INDEX_FILE = CACHE_DIR / "index.json"



SOURCE_DIRS = [
    "01-minimal-agent",
    "02-tool-calling",
    "03-Agent-loop",
    "04-research-planner",
    "05-research-loop",
    "06-embedding-search",
    "07-rag-answer",
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

            #Do not index learning questions
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


def chunks_signature(chunks: list[dict]) -> str:

    hasher = hashlib.sha256()

    for chunk in chunks:
        hasher.update(
            chunk["source"].encode("utf-8")
        )
        hasher.update(
            str(chunk["chunk_id"]).encode("utf-8")
        )
        hasher.update(
            chunk["text"].encode("utf-8")
        )

    return hasher.hexdigest()




def embed_texts(texts: list[str],) -> list[list[float]]:
    response = client.embeddings.create(
        model = EMBED_MODEL,
        input = texts
    )

    return [
        item.embedding for item in response.data
    ]


def cosine_similarity(
    a: list[float],
    b: list[float], 
) -> float:

    dot_product = sum(
        x * y 
        for x,y in zip(a,b)
    )

    norm_a = math.sqrt(
        sum(x * x for x in a)
    )

    norm_b = math.sqrt(
        sum(y * y for y in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return (
        dot_product / (norm_a * norm_b)
    )

def build_index(chunks: list[dict]) -> list[dict]:

    texts = [
        chunk["text"] 
        for chunk in chunks
    ]

    print(f"Embedding {len(texts)} chunks")

    vectors = embed_texts(texts)

    for chunk, vector in zip(
        chunks, 
        vectors,
    ):
        chunk["embedding"] = vector

    return chunks

def save_index(
    index: list[dict],
    signature: str,
) -> None:

    CACHE_DIR.mkdir(
        parents = True,
        exist_ok = True,
    )

    payload = {
        "embed_model": EMBED_MODEL,
        "source_signature": signature,
        "index": index,
    }

    INDEX_FILE.write_text(
        json.dumps(
            payload, 
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Saved index to"
          f"{INDEX_FILE}"
    )


def load_cached_index(signature: str) -> list[dict] | None:

    if not INDEX_FILE.exists():
        print(
            f"No persistent index found at {INDEX_FILE}"
        )
        return None

    try: 
        payload = json.loads(
            INDEX_FILE.read_text(
                encoding="utf-8"
            )
        )
    except (
        json.JSONDecodeError, 
        OSError,
    ):
        print("Index cache is invalid.\n")
        return None

    if payload.get("embed_model") != EMBED_MODEL:
        print(
            "Embedding model changed\n"
        )
        return None

    if payload.get("source_signature") != signature:
        print(
            "Source files changed\n"
        )
        return None

    index = payload.get("index")

    if not isinstance(index, list):
        print(
            "Index cache is invalid (is not a list)\n"
        )
        return None

    print(
        f"Loaded {len(index)} chunks"
        f"from persistent index"
    )

    return index


def load_or_build_index() -> list[dict]:

    chunks = load_chunks()

    signature = chunks_signature(chunks)

    cached_index = load_cached_index(signature)

    if cached_index is not None:
        return cached_index

    print("Building new index...\n")

    index = build_index(chunks)

    save_index(index, signature)

    return index


def semantic_search(
        query: str,
        index: list[dict],
        top_k: int = 3,
) -> list[dict]:

    query_vector = embed_texts([query])[0]

    results = []

    for chunk in index:

        score = cosine_similarity(
            query_vector,
            chunk["embedding"]
        )

        results.append(
            {
                "score": score,
                "source": chunk["source"],
                "text": chunk["text"],
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse = True,
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
        start = 1, 
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

def keyword_search(
    query: str,
    chunks: list[dict]
) -> list[dict]:

    query_words = set(
        query.lower().split()
    )

    results = []

    for chunk in chunks:

        text_words = set(
            chunk["text"].lower().split()
        )

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
        key=lambda item:item["score"], 
        reverse=True,
    )[:3]


def answer_with_rag(
    question: str,
    results: list[dict],
) -> str: 

    context = build_context(
        results
    )

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
        model = MODEL,
        input = prompt,
    )

    return response.output_text


def ask_knowledge_base(
    question: str,
    index:list[dict],
) -> str:

    results = semantic_search(
        question,
        index,
        top_k = 5,
    )

    print("\n=== Retrieved Context ===")

    for result in results:

        print(f"\nScore: "
              f"{result['score']:.4f}")

        print(f"\nSource: "
              f"{result['source']}")

        print("\nChunk: ")
        print(
            result["text"][:500]
        )
    return answer_with_rag(question, results)

if __name__ == "__main__":

    print(
        "Building knowledge  index..."
    )

    #index = build_index()

    index = load_or_build_index()

    print(f"Indexed {len(index)} chunks")


    query = input(
        "\nQuestion: "
    )

    answer = ask_knowledge_base(
        query,
        index
    )

    print("\n=== Answer === \n")

    print(answer)

