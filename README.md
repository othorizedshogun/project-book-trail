# project: book trail
[![wakatime](https://wakatime.com/badge/user/018c9913-55f8-4cc2-9082-b8ae476fb207/project/018da38b-0797-4a08-bae6-caf7c25bf14b.svg)](https://wakatime.com/badge/user/018c9913-55f8-4cc2-9082-b8ae476fb207/project/018da38b-0797-4a08-bae6-caf7c25bf14b)

<!-- ## **Introduction** -->
This project aims to deliver an application that analyzes characters in a novel, recognizing their interactions, traits, and development. This document explains how we plan to achieve this. In simple terms, novels, specifically fiction, tell stories through various events. These events rely on character actions, interactions, and settings. By extracting this information, we can present and understand characters better.

## **Comprehensive Task Roadmap Serving as a Workflow Overview**
1. ~~Extracting and decomposing/chunking pdf~~
2. ~~Extracting Events~~
3. Generating and expanding character data using context mapped from event participation.
4. Answering the questions: character information, interactions, and development.


## **Other Information**
### **Data Structures (WIP)**
| Structure        | Attributes                                                                                                             |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Event Repository | events: list(event), allCharactersInBook: list(character), allLocationsInBook: list(location)                          |
| Event            | id: int, name: str, startPage: int, eventType: str, summary: str, characters: list(int), locations: list(location)     |
| Character        | id: int, name: str, gender: str, alias: list(str)                                                                      |
| Location         | id: int, name: str                                                                 |

