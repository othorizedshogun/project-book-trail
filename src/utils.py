import pathlib
from llama_index import SimpleDirectoryReader


MAX_LENGTH = 3

class Chunk:
    def __init__(self, pages: list):
        self.pages = pages
    def load_chunk(self):
        pages = self.pages
        chunk = ""
        for page in pages:
            chunk += "\n\n{\npage: " + f"{page.metadata["page_label"]}" + ", \ncontent: '" + f"{page.text}" + "}"
        return chunk
    def return_chunk(self):
        return self.load_chunk()

def import_book(path):
    root = pathlib.Path(__file__).parent.parents[0]
    file_path = root / path
    book =  SimpleDirectoryReader(file_path).load_data()
    return book

def decompose_if_needed(book):
    if len(book) < MAX_LENGTH:
        # Just return actual book text to perform extraction on.
        return Chunk(book).return_chunk()
    
    # split up the book into chunks 
    chunks = []
    chunk_starts = [start for start in range(0, len(book), MAX_LENGTH)]
    for i in chunk_starts[:-1]:
        pages = []
        for j in range(i, i+MAX_LENGTH):
            pages.append(book[j])
        chunks.append(Chunk(pages).return_chunk())

    # append the last chunk
    pages = []
    for i in range(chunk_starts[-1], len(book)):
        pages.append(book[i])
    chunks.append(Chunk(pages).return_chunk())

    return chunks

def get_prompt(file_name: str):

    # assume the prompt are in the demo root for demo purposes
    root = pathlib.Path(__file__).parent.parents[0]
    prompt_file_path = root / f"prompts/{file_name}"
 

    # Check if the file exists before trying to read it
    if prompt_file_path.exists() and prompt_file_path.is_file():
        # Open and read the file
        with open(prompt_file_path, 'r') as f:
            content = f.read()
        return content
    else:
        raise ValueError(f"The file {prompt_file_path} does not exist.")
    
