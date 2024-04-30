// TODO: Better logging
// TODO: Better error handling
// TODO: Add doc strings


import {GenerationSteps} from "../enums/GenerationSteps";
import {GeneratorTaskDto} from "../dto/GeneratorTaskDto";

// Define corresponding backend values
const backendLanguageOptions = { English: 'en', German: 'de' };
const backendModeOptions = { Practice: 'practice', Test: 'test', Cloze: 'cloze' };
const backendExportOptions = { CSV: 'csv', Anki: 'apkg' };

// API Endpoint
const endpoint = '/flashcards/generator';


export function startFlashcardGenerationTask(generatorTaskDto: GeneratorTaskDto) {
    console.group('Flashcard Generation Request');
    console.log(`Endpoint: ${endpoint}`);
    console.log('Method: POST');
    console.log('Payload:', generatorTaskDto);
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(generatorTaskDto),
    })
        .then(response => {
            const contentType = response.headers.get('content-type');
            if (!response.ok) {
                if (contentType && contentType.includes('application/json')) {
                    return response.json().then(errorDetails => {
                        console.error(`HTTP error! status:${response.status}, ${JSON.stringify(errorDetails)}`);
                        throw new Error(`HTTP error! status: ${response.status}`);
                    });
                } else {
                    console.error('Non-JSON error from browser:', response.statusText);
                    throw new Error('Non-JSON error from browser');
                }
            }
            return response.json();
        })
        .then(data => {
            if (!data.taskId) {
                console.warn('Response missing taskId:', data);
                throw new Error('taskId is missing from the response');
            } else {
                return data.taskId;
            }
        })
        .catch(error => {
            console.error('Error during flashcard generation:', error);
            console.error(error.stack);
        })
        .finally(() => {
            console.groupEnd();
        });
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
        .then(data => {
            console.log('Data received:', data);
            if (data.state === 'FAILURE') {
                console.error(`Task ${data.state.toLowerCase()}: ${data.error}`);
            } else {
                setCurrentBatch(data.progress);
                setTotalBatches(data.total);
                if (['PROCESSING', 'STARTED', 'PENDING'].includes(data.state)) {
                    let timeout = data.state === 'PROCESSING' ? updateDelay : waitDelay;
                    setTimeout(() => pollFlashcardGenerationTask(taskId), timeout);
                } else {
                    isPollingActiveRef.current = false;
                    if (data.state === 'SUCCESS') {
                        if (!data.retrievalToken) {
                            console.warn('Response missing retrievalToken:', data);
                            throw new Error('retrievalToken is missing from the response');
                        } else {
                            const retrievalToken = data.retrievalToken;
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