import pathlib
from llama_index import SimpleDirectoryReader

class Chunk:
    def __init__(self, pages: list):
        self.pages = pages
    def load_chunk(self):
        pages = self.pages
        chunk = ""
        for page in pages:
            chunk += "\n\n{\npage: " + f"{page.metadata["page_label"]}" + ", \ncontent: '" + f"{page.text}" + "'\n}"
        return chunk
    def return_chunk(self):
        return self.load_chunk()

def import_book(path):
    root = pathlib.Path(__file__).parent.parents[0]
    file_path = root / path
    book =  SimpleDirectoryReader(file_path).load_data()
    return book

def remove_pages(book, start_page, end_page):
    pages_to_delete = []

    if start_page is None:
        start_page = 0

    if end_page is None:
        end_page = len(book) - 1

    for i in list(range(0, start_page-1)) + list(range(end_page, len(book))):
        if 0 <= i < len(book):
            pages_to_delete.append(book[i].metadata["page_label"])

    for num in pages_to_delete:
        for i, page in enumerate(book):
            if page.metadata["page_label"] == num:
                book.pop(i)
                break


def decompose_if_needed(book):

    total_length = 0
    for page in book:
        page_length = len(page.text)
        total_length += page_length 
    average_length = total_length/len(book)

    if average_length < 2048:
        MAX_LENGTH = 6
    else:
        MAX_LENGTH=3


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
    
