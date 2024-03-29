# project: book trail
<!-- [![wakatime](https://wakatime.com/badge/user/018c9913-55f8-4cc2-9082-b8ae476fb207/project/018da38b-0797-4a08-bae6-caf7c25bf14b.svg)](https://wakatime.com/badge/user/018c9913-55f8-4cc2-9082-b8ae476fb207/project/018da38b-0797-4a08-bae6-caf7c25bf14b) -->

<!-- ## **Introduction** -->
This project aims to deliver an application that analyzes characters in a novel, recognizing their interactions, traits, and development. This document explains how we plan to achieve this. In simple terms, novels, specifically fiction, tell stories through various events. These events rely on character actions, interactions, and settings. By extracting this information, we can present and understand characters better.

## **Comprehensive Task Roadmap Serving as a Workflow Overview**
1. ~~Extracting and decomposing/chunking pdf~~
2. ~~Extracting Events~~
3. ~~Generating and expanding character data using context mapped from event participation.~~
4. ~~Asking the questions: character information, phyical description, arc, etc.~~

### **Detail**
The process involves recursively extracting an event repository from the book. This repository comprises a comprehensive list of characters and locations, accompanied by crucial events shaping the narrative. Characters fall into two categories: assigned and unassigned. Assigned characters are directly linked to key events, enabling straightforward information retrieval. Unassigned characters, however, did not actively participate in these events, making their information gathering more complex. For unassigned characters, a search of their mentions generated during event extraction is used as context under the asssumption that they do not posses significant enough impact on the narrative.

## Setup
* Create an environment, clone this repository and install requiremnets
```bash
git clone https://github.com/othorizedshogun/project-book-trail.git
pip install -r requirements.txt
```
Important!: OPEN_AI_KEY varible must be present in environment.
* Run program using file path to the pdf book
```bash
python src/main.py -f <file_path>
```
* file_path should be directory: "name_of_book/". And it should contain the pdf document.
* Optional: You might want to specify new boundaries to the book, indicating the your prefferred start and/or end incase there are other contents in the book (acknowledgements, dedication, table of contents)
```
python script.py -f <file_path> -s <start_page> -e <end_page>
```

FYI: Prone to rate limit errors from larger books.


## **Other Information**
### **Data Structures (WIP)**
| Structure             | Attributes                                                                                                             |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Event Repository      | events: list(event), allCharactersInBook: list(character), allLocationsInBook: list(location)                          |
| Event                 | id: int, name: str, startPage: int, eventType: str, summary: str, characters: list(int), locations: list(location)     |
| Character             | id: int, name: str, gender: str, alias: list(str), mentions: list(int)                                                 |
| Location              | id: int, name: str                                                                                                     |
| Information           | info: str, citation: str                                                                                               |
| Character Information | id: int, name: str, gender: str, alias: list(str), physicalDescription: list(information) personalityTraits: list(information), backstory: list(information), characterarc: list(information), symbolismsAndThemes: list(information), impactOnThePlot: list(information)        |