from backend.src.app.app import FlashcardApp
from backend.src.rest.celery_config import celery
# Ensure that generate_flashcards_task is called only after celery has been configured in app.py


# TODO: Implement robust error handling to manage retries, failures, and unexpected conditions.

@celery.task(bind=True)
def generate_flashcards_task(self, client, config, model_name, lang, mode, input_text):
    def update_progress(processed, total):
        # Update the task's state to a custom 'PROGRESS' state with additional info
        self.update_state(state='PROGRESS', meta={'processed': processed, 'total': total})
    # Instantiate FlashcardApp with the necessary parameters
    flashcard_app = FlashcardApp(client=client,
                                 config=config,
                                 model_name=model_name,
                                 lang=lang,
                                 mode=mode)

    # Pass update_progress() to run() as a call back function
    flashcards = flashcard_app.run(input_text, update_progress).flashcards
    flashcards_as_dict = [{'id': card.id, 'type': card.type, 'frontSide': card.frontside, 'backSide': card.backside} for card in flashcards]
    return flashcards_as_dict
