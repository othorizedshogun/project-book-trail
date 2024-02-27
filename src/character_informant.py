import pathlib
from typing import List

import openai

from models import EventRepository, Character, CharacterInformation
from utils import get_prompt

def get_character_by_id(character_id: int, event_repository: EventRepository) -> Character:
    for character in event_repository.allCharactersInBook:
        if character.id == character_id:
            return character
    return None

def get_other_characters(character_id: int, event_repository: EventRepository) -> List[Character]:
    other_characters = []
    for character in event_repository.allCharactersInBook:
        if character!= character_id:
            other_characters.append(character)
    return other_characters

system_message = get_prompt("system_messages/character_researcher.txt")
user_prompt = get_prompt("user_prompts/character_researcher.txt")

def get_assigned_character_information(client: openai.OpenAI, character_id: int, event_repository: EventRepository, novel, events_by_character, path) -> CharacterInformation:
    root = pathlib.Path(path)
    character = get_character_by_id(character_id, event_repository)
    cur_state = CharacterInformation(
        id=character.id,
        name=character.name,
        gender=character.gender,
        aliases=character.aliases,
    )
    other_characters = get_other_characters(character_id, event_repository)

    character_events = events_by_character[character_id]
    num_iterations = len(character_events)

    print(f"Generating information on {character.name}...")
    print(f"Number of events: {num_iterations}")

    for i, event in enumerate(character_events):
        num_pages = len(list(range(event.startPage, event.endPage+1)))
        print(f"Generating information on {character.name} from : {i+1} of {num_iterations}...")
        event_insert = f"Event: {event}\n"
        print(f"There are {num_pages} page(s) in this event.")
    
        pages = ["\n\n{\npage: " + f"{novel[page-1].metadata["page_label"]}" + ", \ncontent: '" + f"{novel[page-1].text}" + "'\n}" for page in range(event.startPage, event.endPage+1)]
        pages_insert = ""
        for page in pages:
            pages_insert += page + "\n\n"

        new_updates = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            response_model=CharacterInformation,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": (
                        f"""Given this new data, rewrite information on the {character.name}:
                        # Event {i}/{num_iterations} {character.name} participated in:
                        """ + event_insert + pages_insert
                    )
                },
                {
                    "role": "user",
                    "content": f"""Here is the current information on the character {character.name}:
                    {cur_state.model_dump_json(indent=2)}
                    
                    List of the other characters in the book:
                    {other_characters}"""
                },
            ]
        )
        cur_state = cur_state.update(new_updates)
        print(f"\n{cur_state}\n\n")
        
        character_info_file_path = root/f"character_info/{"_".join((character.name).split())}.json"
        with open(character_info_file_path, "w") as file:
            file.write(cur_state.model_dump_json(indent=2))
        print(f"Information on {cur_state.name} saved to: {character_info_file_path}")

    return cur_state

def get_unassigned_character_information(client: openai.OpenAI, character_id: int, novel, event_repository, path):
    root = pathlib.Path(path)
    character = get_character_by_id(character_id, event_repository)
    cur_state = CharacterInformation(
        id=character.id,
        name=character.name,
        gender=character.gender,
        aliases=character.aliases,
    )
    other_characters = get_other_characters(character_id, event_repository)

    pages = list(set(character.mentions))
    num_iterations = len(pages)

    print(f"Generating information on {character.name}...")
    print(f"Number of pages: {num_iterations}")

    system_message = get_prompt("system_messages/nu_character_researcher.txt")

    for i, page in enumerate(pages):
        print(f"Generating information on {character.name} from : {i+1} of {num_iterations}...")
    
        page_insert = "\n\n{\npage: " + f"{novel[page-1].metadata["page_label"]}" + ", \ncontent: '" + f"{novel[page-1].text}" + "'\n}"

        new_updates = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            response_model=CharacterInformation,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": (
                        f"""Given this new page, extract and rewrite information on {character.name}:
                        # Page {i}/{num_iterations}:
                        """ + page_insert
                    )
                },
                {
                    "role": "user",
                    "content": f"""Here is the current information on the character {character.name}:
                    {cur_state.model_dump_json(indent=2)}
                    
                    List of the other characters in the book:
                    {other_characters}"""
                },
            ]
        )
        cur_state = cur_state.update(new_updates)
        print(f"\n{cur_state}\n\n")
        
        character_info_file_path = root/f"character_info/{"_".join((character.name).split())}.json"
        with open(character_info_file_path, "w") as file:
            file.write(cur_state.model_dump_json(indent=2))
        print(f"Information on {cur_state.name} saved to: {character_info_file_path}")

    return cur_state

