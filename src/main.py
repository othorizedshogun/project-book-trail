from openai import OpenAI
# from llama_index import ve
from datetime import datetime

import instructor
import openai
import os
import sys
import time

from event_extractor import extract_events
from character_information import get_assigned_character_information, get_unassigned_character_information
from utils import import_book, decompose_if_needed

client = instructor.patch(OpenAI())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    
    book_path = sys.argv[1]

    start_time = time.time()

    book = import_book(path=book_path)
    print(f"{len(book)} pages")
    print("Creating Chunks...")
    chunks = decompose_if_needed(book)

    # Vector database

    print("Extracting events...")
    event_repository = extract_events(client=client, chunks=chunks)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Took {execution_time:.5f} seconds to extract events from {len(book)} pages")

    events_by_character = event_repository.get_events_by_character()
    assigned_characters = [i for i in events_by_character.keys()]
    unassigned_characters = [character.id for character in event_repository.allCharactersInBook if not character.id in assigned_characters]

    # create folder to store character information in json
    character_info_folder = "character_info"
    if not os.path.exists(character_info_folder):
        os.makedirs(character_info_folder)

    for character_id in assigned_characters:
        get_assigned_character_information(client=client,  character_id=character_id, event_repository=event_repository, novel=book, events_by_character=events_by_character)
    for character in unassigned_characters:
        get_unassigned_character_information(client=client, character_id=character_id, )
        
