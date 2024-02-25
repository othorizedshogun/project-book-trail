from pydantic import BaseModel, Field
from typing import List, Optional
from typing_extensions import Literal
from collections import defaultdict


class Analysis(BaseModel):
    chain_of_thought: str
    analysis: str
    events: List[str]
    characters: List[str]
    locations: List[str]

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
        description="Names, Titles, pronouns used in refernce to or that describe the character, Should include additional aliases from the perspective of the main character"
    )
    mentions: List[int] = Field(
        ...,
        description="List of pages where character was mentioned or referenced"
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
    endPage: int = Field(
        ...,
        description="The page the event ends."
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
            events=update_and_deduplicate_items(self.events, other.events),
            allCharactersInBook=update_and_deduplicate_items(self.allCharactersInBook, other.allCharactersInBook),
            allLocationsInBook=update_and_deduplicate_items(self.allLocationsInBook, other.allLocationsInBook)
        )
    
    def get_events_by_character(self) -> dict[int, List[Event]]:
        """Return a dictionary mapping character IDs to a list of events they are associated with."""
        character_events_mapping = defaultdict(list)

        for event in self.events:
            for character_id in event.characters:
                character_events_mapping[character_id].append(event)
        
        return dict(character_events_mapping)
    
    def get_repository_with_last_two_events(self) -> "EventRepository":
        """Return a new repository with everything in the current repository but only with the last four events."""
        return EventRepository(events=self.events[-2:], allCharactersInBook=self.allCharactersInBook, allLocationsInBook=self.allLocationsInBook)


def update_and_deduplicate_items(existing_list: List[Event]|List[Character]|List[Location], new_list: List[Event]|List[Character]|List[Location]) -> List[Event]|List[Character]|List[Location]:
    updated_list = existing_list.copy()

    for new_item in new_list:
        existing_item_index = next((i for i, item in enumerate(updated_list) if item.id == new_item.id), None)

        if existing_item_index is not None:
            if type(new_item) == Character:
                updated_list[existing_item_index].name = new_item.name
                updated_list[existing_item_index].aliases = list(set(updated_list[existing_item_index].aliases + new_item.aliases))
                updated_list[existing_item_index].mentions = list(set(updated_list[existing_item_index].mentions + new_item.mentions))
            else:
                updated_list[existing_item_index] = new_item
        else:
            updated_list.append(new_item)

    updated_list = list({item.id: item for item in updated_list}.values())

    return updated_list

class Information(BaseModel):
    info: Optional[str] = Field(
        ...,
        default_factory=str,
        description="Prose-like form containng the information"
    )
    citations: Optional[List[str]] = Field(
        ...,
        default_factory=list,
        description="List of short excerpts from the text backing the information."
    )

class CharacterInformation(BaseModel):
    id: Optional[int] = Field(
        ...,
        description="Unique identifier for the event, used for deduplication, design a scheme that allows for multiple events",
        default_factory=int
    )
    name: Optional[str] = Field(
        ...,
        description="For sake of precision and deduplication, should be the actual name of the characters, if not provided, should be 'Not Available'",
        default_factory=str
    )
    gender: Optional[Literal["Male", "Female", "N/A"]] = Field(..., default_factory=str)
    aliases: Optional[List[str]] = Field(
        ...,
        description="Names, titles, pronouns used in refernce to or that describe the character",
        default_factory=list
    )
    physicalDescription: Optional[List[Information]] = Field(
        ...,
        default_factory=list,
        description="List of physical appearance, distinctive features, charactersitics or qualifiers as described"
    )
    personalityTraits: Optional[List[Information]] = Field(
        ...,
        default_factory=list,
        description="List of main personality traits, how they generally behave in different situations"
    )
    backstory: Optional[List[Information]] = Field(
        ...,
        default_factory=list,
        description="List of known information on the character's past, significant events that shaped who they are"
    )
    characterArc: Optional[List[Information]] = Field(
        ...,
        default_factory=list,
        description="List of evolution of the character throughout the story, key moments that define their character devleopment"
    )
    symbolismsAndThemes: Optional[List[Information]] = Field(
        ...,
        default_factory=list,
        description="List of symbolic elements or themes that represent the character in the story, deeper layers to the character that may not be immediately apparent"
    )
    impactOnThePlot: Optional[List[Information]] = Field(
        ...,
        default_factory=list,
        description="List of influence of the character on the overall progression of the plot, specific actions or consequences that have significant consequences"
    )

    def update(self, other: "CharacterInformation") -> "CharacterInformation":
        return CharacterInformation(
            name=other.name,
            gender=other.gender,
            aliases=self.aliases,
            pyhsical_description=other.physicalDescription,
            personalityTraits=other.personalityTraits,
            backstory=other.backstory,
            characterArc=other.characterArc,
            symbolismsAndThemes=other.symbolismsAndThemes,
            impactOnThePlot=other.impactOnThePlot
        )
