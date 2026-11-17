"""
Pipeline Utilities
==================
Shared helpers used by all pipeline nodes.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(temperature: float = 0.1) -> ChatGoogleGenerativeAI:
    """
    Returns a Gemini 2.0 Flash LLM instance.

    temperature guide:
      0.1 — for classification, chunking, writing (precision > creativity)
      0.3 — for enrichment and critique (need some generativity)
      0.2 — for synthesis (balanced)
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=temperature,
    )
