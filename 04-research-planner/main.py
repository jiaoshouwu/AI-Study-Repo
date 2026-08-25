import os 
from openai import OpenAI

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")

def create_plan(topic: str) -> list[str]:

    if len(topic.strip()) < 5:
        raise ValueError("Research topic must be at least 5 characters long.")

    prompt = f"""
You are a research planner. 
Break the following toipic into exactly 
3 independent research questions. 

Do not answer them. 

Return exactly: 

Q1: ...
Q2: ...
Q3: ...

Topic: {topic}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    questions = []

    for line in response.output_text.splitlines():
        line = line.strip()

        if line.startswith(("Q1:", "Q2:", "Q3:")):
            questions.append(
                line.split(":", 1)[1].strip()
            )


    if len(questions) != 3:
            raise RuntimeError("Planner must return exactly 3 questions.")

    return questions


def research_question(question: str, trace: list) -> str:
    prompt = f"""
Research the question below: 

Return: 
- 3 concise factual findinds
- 1 short takeaway
- useful source citations

Prefer primary or authoritative sources.

Question: 
{question}
"""

    response = client.responses.create(
        model=MODEL,
        tools = [
            {
                "type": "web_search",
            }
        ],
        input=prompt,
    )

    trace.append({
        "question": question,
        "action": "web_search",
    })


    return response.output_text


def collect_evidence(questions: list[str],) -> list[dict]:

    evidence = []

    for index, question in enumerate(questions,start=1):

        print(f"\n--- Research {index} ---")

        print(f"Question: {question}")

        trace = []
        result = research_question(question, trace)
        print(trace)

        print(result)

        evidence.append({
            "question": question,
            "result": result
        })

    return evidence

def synthesize(topic: str, evidence: list[dict]) -> str:

    evidence_text = ""

    for item in evidence:

        evidence_text += (
            "\n\n QUESTION: \n"
            + item["question"]
            + "\nEVIDENCE:\n"
            + item["result"]
        )

    prompt = f"""
You are a research writer

Topic: {topic}

Write a concise report using ONLY the evidence below. 

Requirements:
- Maximum 6 bullet points 
- Finish with one conclusion
- Donot invent facts
- Preserve useful citation 
- Mention conflicts if sources disagree

Evidence:
{evidence_text}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )
    return response.output_text



def run_research(topic: str) -> str:
    
    print("\n === Planning ====\n")

    questions = create_plan(topic)

    for index, question in enumerate(questions,start=1):

        print(f"Q{index}: {question}")

    print("\n === Research ====\n")

    evidence = collect_evidence(questions)

    print ("\n === Synthesis ====\n")

    return synthesize(topic, evidence)
        


if __name__ == "__main__":



    '''
    print(research_question("what is an AI agent"))
    questions = create_plan("AI agents in software engineering")

    for q in questions:
        print(q)

    '''

    topic = input (" Research topic: ")
    report = run_research(topic)

    print("\n === Report ====\n")

    print(report)

