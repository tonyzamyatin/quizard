import json
import os
import zipfile
from typing import List

from backend.src.flashcard.flashcard import Flashcard


class FlashcardDeck:
    def __init__(self, flashcards: List[Flashcard]):
        self.flashcards = flashcards

    def __str__(self):
        return json.dumps(self, indent=4, default=vars)

    def save_as_csv(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            for flashcard in self.flashcards:
                f.write(flashcard.as_csv())
                f.write('\n')

    # TODO: Test and save the user generated apkg packages somewhere (e.g. SQL database)
    def sava_as_apkg(self, filename: str, media_files: List[str] = None):   # or use genanki package (but its third party and potentially not safe for commercial use )
        with zipfile.ZipFile(filename, 'w') as zipf:
            media_files = media_files or []
            with zipfile.ZipFile(filename, 'w') as zipf:
                # Add media files to 'collection.media' folder inside the zip
                for media_file in media_files:
                    zipf.write(media_file, os.path.join('collection.media', os.path.basename(media_file)))
            # Create a collection.anki2 file in the root of the archive with deck configuration
                collection_data = {
                    "note_models": [],
                    "notes": []
                }
                for flashcard in self.flashcards:
                    note_model = {
                        "name": "Basic",
                        "fields": [
                            {"name": "Front"},
                            {"name": "Back"}
                        ],
                        "templates": [
                            {
                                "name": "Card 1",
                                "qfmt": "{{Front}}",
                                "afmt": "{{FrontSide}}<hr id=\"answer\">{{Back}}"
                            }
                        ]
                    }
                    collection_data["note_models"].append(note_model)
                    note = {
                        "deckName": "My Deck",
                        "modelName": "Basic",
                        "fields": {
                            "Front": flashcard.frontside,
                            "Back": flashcard.backside
                        },
                        "tags": []
                    }
                    collection_data["notes"].append(note)
                # Write the JSON data to collection.anki2 file
                zipf.writestr('collection.anki2', json.dumps(collection_data))
