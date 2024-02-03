from backend.src.app.app import FlashcardApp
from celery import shared_task
from celery.utils.log import get_task_logger

# Ensure that tasks are called only after celery_app has been configured in app.py

# TODO: Setup uniform logging across the whole system (w/o redundancies)
logger = get_task_logger(__name__)


# TODO: Implement robust error handling to manage retries, failures, and unexpected conditions.

@shared_task(bind=True, ignore_result=False)
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
