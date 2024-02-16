from typing import List

import openai

from models import Character, EventRepository
from analyzer import Analysis, generate_analysis
from utils import get_prompt
    
system_message = get_prompt("system_messages/event_extractor.txt")
user_prompt = get_prompt("user_prompts/event_extractor.txt")

def extract_events(client: openai.OpenAI, chunks: List[str]) -> EventRepository:
    cur_state = EventRepository()
    num_iterations = len(chunks)
    print(F"Number of Chunks: {num_iterations}")
    for i, inp in enumerate(chunks):
        print(f"Performing extraction on: {i+1} of  {num_iterations}")
        analysis: Analysis =  generate_analysis(client=client, chunk=inp)
        events = [event for event in analysis.events]
        characters = [Character for character in analysis.characters]
        locations = [location for location in analysis.locations]

        analysis_insert = """chain_of_thought: {chain_of_thought}
        Analysis: {analysis}
        Events: {events}
        characters: {characters}
        Locations: {locations}""".format(chain_of_thought=analysis.chain_of_thought, analysis=analysis.analysis, events=events, characters=characters, locations=locations)

        new_updates = client.chat.completions.create(
            model = "gpt-4-turbo-preview",
            temperature=0.7,
            response_model=EventRepository,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": (
                        f"""Extract any new events and characters from the following:
                        # Part {i}/{num_iterations} of the book:
                        
                        {inp}""" + analysis_insert + user_prompt
                    ),
                },
                {
                    "role": "user",
                    "content": f"""Here is the current state of the repository:
                    {cur_state.model_dump_json(indent=2)}"""
                }
            ]
        )
        cur_state = cur_state.update(new_updates)
        print(f"""
        
        {cur_state}
        
        
        """)
    return cur_state
