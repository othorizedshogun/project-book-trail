from openai import OpenAI
from llama_index import SimpleDirectoryReader
from datetime import datetime

import instructor
import os

from event_extractor import extract_events
from utils import import_book, decompose_if_needed

client = instructor.patch(OpenAI())

if __name__ == "__main__":
    book = import_book("data/jd_salinger/pdf")
    print("Creating Chunks...")
    chunks = decompose_if_needed(book)

    print("Extracting events...")
    events = extract_events(client=client, chunks=chunks)

    # create log file with event repository
    response_folder = "response"
    if not os.path.exists(response_folder):
        os.makedirs(response_folder)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    response_file_path = f"response/response_{timestamp}.txt"

    with open(response_file_path, "w") as file:
        file.write(events.model_dump_json(indent=2))

    print(f"Events saved to: {response_file_path}")

