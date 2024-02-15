from pydantic import BaseModel, Field
from typing import List, Iterable, Optional
from typing_extensions import Literal

import openai

from analyzer import Analysis, generate_analysis
from utils import get_prompt

class Character(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the event, used for deduplication, design a scheme that allows for multiple events"
    )
    name: str = Field(
        ...,
        description="For sake of precision and deduplication, should be the actual name of the characters, if not provided, should be 'Not Available'"
    )
    gender: Literal["Male", "Female", "N/A"]
    aliases: List[str] = Field(
        ...,
        description="Names, TItles, Promouns usd in refernce to or that describe the character"
    )

class Location(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the event, used for deduplication, design a scheme that allows for multiple events"
    )
    name: str

class Event(BaseModel):
    id: int
    name: str
    startPage: int = Field(
        ...,
        description="The page the event begins"
    )
    eventType: Literal["Narrative Development", "Character Interaction", "Action Sequences", "Plot Dynamics", "Climax and Resolution", "Humor and Tone", "Conflict and Resolution", "Character Development", "Contextual Flashback or Information"]
    summary: str
    characters: List[int] = Field(
        ...,
        description="List of the character IDs of characters participating in or with a connection to the event"
    )
    locations: List[int] = Field(
        ...,
        description="List of the location IDs of locations in relation to an event"
    )

class EventRepository(BaseModel):
    events: Optional[List[Event]] = Field(..., default_factory=list)
    allCharactersInBook: List[Character] = Field(
        ...,
        default_factory=list,
        description="Updated list of characters in the book"
    )
    allLocationsInBook: List[Location] = Field(
        ...,
        default_factory=list,
        description="Updated list of locations in the book"
    )

    def update(self, other: "EventRepository") -> "EventRepository":
        """Updates the current repository with the other repository, deduplicating events and unassigned characters."""
        return EventRepository(
            events=self.events+other.events,
            allCharactersInBook=self.allCharactersInBook+other.allCharactersInBook,
            allLocationsInBook=self.allLocationsInBook+other.allLocationsInBook
        )
    
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
