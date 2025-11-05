# agents/spark_pro.py
# Requer: pip install agno openai python-dotenv
# Uso: python scripts/generate_pack.py --tema "Seu tema aqui"
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
except Exception as e:
    # Fallback para não quebrar apenas na leitura do arquivo
    Agent = object
    OpenAIChat = object

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "spark_pro_system.md")

@dataclass
class SparkInputs:
    tema: str
    foco: Optional[str] = None

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def build_agent():
    system_text = load_prompt()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAIChat(id=model)
    agent = Agent(
        name="Spark Pro",
        model=client,
        instructions=system_text,
        markdown=True,
        # model=OpenAIChat(id=os.getenv("OPENAI_MODEL_FAST", "gpt-4o-mini")),
    )
    return agent

def render(tema: str, foco: Optional[str] = None) -> str:
    agent = build_agent()
    user = f"Tema: {tema}\nFoco: {foco or 'geral'}"
    result = agent.run(user)
    if isinstance(result, str):
        return result
    for attr in ("text", "content", "output", "response_text"):
        if hasattr(result, attr):
            v = getattr(result, attr)
            if isinstance(v, str):
                return v
    return str(result)

if __name__ == "__main__":
    print(render("Como criar um agente multimodal de IA em 1 noite (com Agno)", "YouTube Short + LinkedIn"))
