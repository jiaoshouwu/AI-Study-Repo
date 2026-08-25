import os 
import json
from openai import OpenAI

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")

MAX_EXTRA_SEARCHES = 3


def evidence_to_text(
    evidence: list[dict],
) -> str:

    parts = []

    for item in evidence:
        parts.append(
            "QUESTION: \n"
            + item["question"]
            + "\n\nEVIDENCE:\n"
            + item["result"]           
        )

    return "\n\n---\n\n".join(parts)

def evaluate_evidence(
    topic: str,
    evidence: list[dict],
) -> str:

    evidence_text = evidence_to_text(evidence)

    prompt = f"""
You are a research critic.

Original research topic: 
{topic}

Review the collected evidence below. 

Decide wether the evidence is sufficient to 
write a useful and well-supported answer 
to the orginal research topic.

Return ONLY valid JSON:

{{
    "sufficient": true,
    "gap":"",
    "next_query":""
}}

if evidence is NOT sufficient:
{{
    "sufficient": false,
    "gap": "What important information is missing",
    "next_query": "One specific web search question"
}}

Rules:

- Do not perform research yourself. 
- Judge only the supplied evidence. 
- next_query must target the most important gap.
- If sufficient is true, next_query must be empty.

Evidence:
{evidence_text}
"""
    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    text = response.output_text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        
        text = text.rsplit("```", 1)[0].strip()

    return json.loads(text)




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


def research_question(question: str, trace: list | None = None) -> str:
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

    if trace is not None:
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
        #print(trace)

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

    print("\n === Initial Research ====\n")

    trace = []

    trace.append(
        {
            "stage": "initial_research",
            "questions": len(questions)
        }
    )

    evidence = collect_evidence(questions)

    searched_questions = {
        item["question"].strip().lower()
        for item in evidence
    }    

    extra_searches = 0

    while True:
        print("\n === Evidence Evaluation ====\n")

        assessment = evaluate_evidence(topic, evidence)

        print("Sufficient:", assessment["sufficient"])

        trace.append(
            {
                "stage":"evaluation",
                "sufficient": assessment["sufficient"],
                "gap": assessment["gap"],
            }
        )
        

        print("Gap:", assessment["gap"])

        if assessment["sufficient"]:
            break

        if extra_searches >= MAX_EXTRA_SEARCHES:
            print("\n === Maximum extra searches reached. Stopping research. ====\n")

            break
    
        next_query = assessment["next_query"].strip()

        if not next_query:
            raise RuntimeError("Critic reported a gap but provided no query.")
        
        print("\n === Additional Research ====\n")

        print("Next query:", next_query)
        
        normalized_query = (
            next_query.strip().lower()
        )

        if normalized_query in \
                searched_questions:

            print(
                "Duplicate research query "
                "detected. Stopping."
            )

            break

        searched_questions.add(
            normalized_query
        )


        result = research_question(next_query)

        trace.append(
            {
                "stage": "extra_search",
                "query": next_query
            }
        )

        evidence.append({
            "question": next_query,
            "result": result
        })

        extra_searches += 1


    print("\n === Research Trace ===")
    for item in trace:
        print(item)

    print ("\n === Synthesis ====\n")
    return synthesize(topic, evidence)
        

if __name__ == "__main__weak_evidence":
    weak_evidence = [
        {
            "question": "What is an AI agent?",
            "result": (
                "An AI agent can use models "
                "and tools"
            ),
        }
    ]

    assessment = evaluate_evidence(
        (
            "compare AI agens and chatbots"
            "in architecture, cost, security"
            "and practical use cases"
        ),
        weak_evidence,
    )

    print("assessment: ", assessment)


    


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

