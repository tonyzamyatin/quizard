// TODO: Better logging
// TODO: Add doc strings


import {GeneratorStep} from "../enum/GeneratorStep";
import {GeneratorTask, GeneratorTaskInfo, TaskState,} from "../dto/generator";
import {sendRequest} from "../util/requestUtil";


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

async function getFlashcardGeneratorTaskInfo(taskId: string): Promise<GeneratorTaskInfo> {
    const endpoint = `/flashcards/generator/${taskId}`;
    console.group('Flashcard Update Request');
    console.log(`Endpoint:${ endpoint }`);
    console.log('Method: GET');

    const taskInfo = await sendRequest<GeneratorTaskInfo>(endpoint, 'GET');
    if (!taskInfo) {
        console.warn('Response missing taskInfo:');
        throw new Error('taskInfo is missing from the response');
    }
    return taskInfo;
}

export async function pollFlashcardGeneratorTask(taskId: string, setCurrentBatch: (current: number) => void, setTotalBatches: (total: number) => void, waitDelay = 1000, updateDelay = 1000) {
    const taskInfo = await getFlashcardGeneratorTaskInfo(taskId);
    if (taskInfo.currentBatch && taskInfo.totalBatches) {
        setCurrentBatch(taskInfo.currentBatch);
        setTotalBatches(taskInfo.totalBatches);
    }
    if (taskInfo.taskState === TaskState.success) {
        return;
    } else {
        let timeout = taskInfo.taskState === TaskState.inProgress ? updateDelay : waitDelay;
        setTimeout(() => pollFlashcardGeneratorTask(taskId, setCurrentBatch, setTotalBatches, waitDelay, updateDelay), timeout);
    }
}


export function cancelFlashcardGenerationTask( taskId: string ) {
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

export function downloadFlashcards( retrievalToken: string ) {
    if (retrievalToken != null) {
        const endpoint = `/flashcards/retriever/${retrievalToken}`;
        fetch(endpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'flashcards';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="(.+)"/i);
                    if (filenameMatch && filenameMatch.length > 1) {
                        filename = filenameMatch[1];
                    }
                }
                return response.blob().then(blob => ({blob, filename}));
            })
            .then(({blob, filename}) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error during file download:', error);
            });
    }
}