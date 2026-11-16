
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

client = Groq(api_key=api_key) if api_key else None


def generate_diagnosis(incident, recommendations):
    if client is None:
        raise RuntimeError("GROQ_API_KEY is missing.")

    runbooks_context = "\n\n".join(
        [
            f"Source: {item['source']}\n"
            f"Content:\n{item['content']}"
            for item in recommendations
        ]
    )

    prompt = f"""
You are an experienced Site Reliability Engineer (SRE).

Analyze this IT incident using the incident information
and the operational runbooks provided.

INCIDENT:
{incident}

OPERATIONAL RUNBOOKS:
{runbooks_context}

Return a structured diagnosis containing:
1. Summary
2. Probable causes
3. Technical analysis
4. Recommended investigation steps
5. Recommended remediation actions
6. Severity assessment

Rules:
- Use the provided evidence.
- Do not invent facts.
- Clearly distinguish confirmed facts from hypotheses.
- Do not execute remediation.
- Keep recommendations safe and actionable.
- Return the result in French.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are an IT incident diagnosis assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=2000,
    )

    return response.choices[0].message.content
