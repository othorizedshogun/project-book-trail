from pydantic import BaseModel
from typing import List

import openai

from models import Analysis
from utils import get_prompt

system_message = get_prompt("system_messages/analyzer.txt")
user_prompt = get_prompt("user_prompts/analyzer.txt")

def generate_analysis(client: openai.OpenAI, chunk) -> Analysis:
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        temperature=0.7,
        response_model=Analysis,
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": (
                    f"{chunk}\n\n" + user_prompt
                )
            }
        ]
    )
