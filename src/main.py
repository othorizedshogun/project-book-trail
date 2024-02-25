from openai import OpenAI
# from llama_index import ve
from datetime import datetime

import instructor
import openai
import os
import sys
import time
import argparse

from event_extractor import extract_events
from character_informant import get_assigned_character_information, get_unassigned_character_information
from utils import import_book, decompose_if_needed, remove_pages

client = instructor.patch(OpenAI())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="python script.py <file_path> <start_page> <end_page>")

    parser.add_argument("-f", "--File_path", help = "File Path")
    parser.add_argument("-s", "--Start_page", help = "Start Page")
    parser.add_argument("-e", "--End_page", help = "End Page")

    args = parser.parse_args()

    start_page = args.Start_page
    end_page = args.End_page

    book_path = args.File_path
    if args.Start_page != None:
        start_page = int(args.Start_page)
    if args.End_page != None:
        end_page = int(args.End_page)

    start_time = time.time()

    book = import_book(path=book_path)
    remove_pages(book, start_page, end_page)

    print(f"{len(book)} pages")
    print("Creating Chunks...")
    chunks = decompose_if_needed(book)

    print("Extracting events...")
    event_repository = extract_events(client=client, chunks=chunks, path=book_path)

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
        get_assigned_character_information(client=client,  character_id=character_id, event_repository=event_repository, novel=book, events_by_character=events_by_character, path=book_path)
    for character_id in unassigned_characters:
        get_unassigned_character_information(client=client, character_id=character_id, event_repository=event_repository, novel=book, path=book_path)
        
