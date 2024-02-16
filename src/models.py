from pydantic import BaseModel, Field
from typing import List, Optional
from typing_extensions import Literal


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
            events=update_and_deduplicate_items(self.events, other.events),
            allCharactersInBook=update_and_deduplicate_items(self.allCharactersInBook, other.allCharactersInBook),
            allLocationsInBook=update_and_deduplicate_items(self.allLocationsInBook, other.allLocationsInBook)
        )


def update_and_deduplicate_items(existing_list: List[Event]|List[Character]|List[Location], new_list: List[Event]|List[Character]|List[Location]) -> List[Event]|List[Character]|List[Location]:
    updated_list = existing_list.copy()

    # Update existing items with new information
    for new_item in new_list:
        existing_item_index = next((i for i, item in enumerate(updated_list) if item.id == new_item.id), None)

        if existing_item_index is not None:
            # If the item with the same id already exists, update the information
            if type(new_item) == Character:
                updated_list[existing_item_index].gender = new_item.gender
                updated_list[existing_item_index].aliases = list(set(updated_list[existing_item_index].aliases + new_item.aliases))
            else:
                updated_list[existing_item_index] = new_item
        else:
            # If the item with the same id does not exist, add the new character
            updated_list.append(new_item)

    # Deduplicate based on id
    updated_list = list({item.id: item for item in updated_list}.values())

    return updated_list

