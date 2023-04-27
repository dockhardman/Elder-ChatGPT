from dataclasses import dataclass
from typing import Dict, List, Text


@dataclass
class OpenAIChatUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class OpenAIRecord:
    """OpenAI Record Schema"""

    id: Text
    object: Text
    created: int
    model: Text
    usage: OpenAIChatUsage
    choices: List[Dict]
    time_cost: float
