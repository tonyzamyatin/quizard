// TODO: Better logging
// TODO: Add doc strings




import {GenerationSteps} from "../enums/GenerationSteps";
import {GeneratorTask, GeneratorTaskInfo} from "../dto/generator";
import {sendRequest} from "./utils/requestUtils";
import {ErrorDetails} from "../dto/errorDetails";

// Define corresponding backend values
const backendLanguageOptions = { English: 'en', German: 'de' };
const backendModeOptions = { Practice: 'practice', Test: 'test', Cloze: 'cloze' };
const backendExportOptions = { CSV: 'csv', Anki: 'apkg' };

// API Endpoint
const endpoint = '/flashcards/generator';


export async function startFlashcardGeneratorTask(generatorTaskDto: GeneratorTask): Promise<string> {
    console.group('Flashcard Generation Request');
    console.info(`Endpoint: ${endpoint}`);
    console.info('Method: POST');
    console.info('Payload:', generatorTaskDto);
    console.groupEnd();
    const taskId = await sendRequest<string>(endpoint, 'POST', generatorTaskDto);
    if (!taskId) {
        console.warn('Response missing taskId:');
        throw new Error('taskId is missing from the response');
    }
    console.info(`Task started! Task Id: ${taskId}`);
    return taskId;
}


export function pollFlashcardGenerationTask(taskId, waitDelay = 1000, updateDelay = 1000) {
    if (!isPollingActiveRef.current) return;

    const endpoint = `/flashcards/generator/${taskId}`;
    console.group('Flashcard Update Request');
    console.log(`Endpoint:${ endpoint }`);
    console.log('Method: GET');
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(task => {
            console.log('Data received:', task);
            if (task.state === 'FAILURE') {
                console.error(`Task ${task.state.toLowerCase()}: ${task.error}`);
            } else {
                setCurrentBatch(task.current);
                setTotalBatches(task.total);
                if (['PROCESSING', 'STARTED', 'PENDING'].includes(task.state)) {
                    let timeout = task.state === 'PROCESSING' ? updateDelay : waitDelay;
                    setTimeout(() => pollFlashcardGenerationTask(taskId), timeout);
                } else {
                    isPollingActiveRef.current = false;
                    if (task.state === 'SUCCESS') {
                        if (!task.retrievalToken) {
                            console.warn('Response missing retrievalToken:', task);
                            throw new Error('retrievalToken is missing from the response');
                        } else {
                            const retrievalToken = task.retrievalToken;
                            setCurrentStep(GenerationSteps.Complete);
                            downloadFlashcards(retrievalToken);
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // setTimeout(() => pollFlashcardGenerationTask(taskId), waitDelay);    // Uncomment me when done with UI design
        })
        .finally(() => {
            console.groupEnd();
        });
};

export function cancelFlashcardGenerationTask( taskId ) {
    isPollingActiveRef.current = false; // Stop polling
    const endpoint = `/flashcards/generator/${taskId}`
    console.group('Flashcard Cancellation Request');
    console.log(`Endpoint:${ endpoint }`);
    console.log('Method: DELETE');
    fetch(endpoint, {method: 'DELETE'})
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Cancellation successful:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            console.groupEnd();
        });
};

export function downloadFlashcards( retrievalToken ) {
    if (retrievalToken != null) {
        const endpoint = `/flashcards/retriever/${retrievalToken}`;
        console.group('Flashcard Download Request');
        console.log(`Endpoint:${ endpoint }`);
        console.log('Method: GET');
        fetch(endpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.blob()
            }).then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = exportFormat === 'csv' ? 'flashcards.csv' : 'flashcards.apkg';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
            .catch(error => {
                console.error('Error during file download:', error);
            });
    }
}