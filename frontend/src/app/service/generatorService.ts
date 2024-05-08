// TODO: Better logging
// TODO: Add doc strings


import {GeneratorTask, GeneratorTaskInfo} from "../dto/generator";
import {sendRequest} from "../util/requestUtil";
import {FileFormat} from "../enum/generatorOptions";
import {TaskState} from "../enum/taskState";


// API Endpoint
const endpoint = '/flashcards/generator';

export async function startFlashcardGeneratorTask(generatorTaskDto: GeneratorTask): Promise<string> {
    console.group('startFlashcardGeneratorTask');
    console.info(`Endpoint: ${endpoint}`);
    console.info('Method: POST');
    console.info('Payload:', generatorTaskDto);
    const response = await sendRequest({
        endpoint: endpoint,
        method: 'POST',
        data: generatorTaskDto
    });
    const taskId = response.data.taskId;
    if (!taskId) {
        console.warn('Response missing taskId:');
        throw new Error('taskId is missing from the response');
    }
    console.info(`Task started! Task Id: ${taskId}`);
    console.groupEnd();
    return taskId;
}

export async function fetchFlashcardGeneratorTaskInfo(taskId: string): Promise<GeneratorTaskInfo> {
    const endpoint = `/flashcards/generator/${taskId}`;
    console.group('fetchFlashcardGeneratorTaskInfo');
    console.log(`Endpoint:${ endpoint }`);
    console.log('Method: GET');
    const response = await sendRequest({
        endpoint: endpoint,
        method: 'GET'
    });
    const taskInfo = response.data.taskInfo;
    if (!taskInfo) {
        console.warn('Response missing taskInfo:');
        throw new Error('taskInfo is missing from the response');
    }
    console.groupEnd();
    return taskInfo;
}

export async function cancelFlashcardGeneratorTask(taskId: string ) {
    const endpoint = `/flashcards/generator/${taskId}`
    console.group('cancelFlashcardGenerationTask');
    console.log(`Endpoint:${ endpoint }`);
    console.log('Method: DELETE');
    await sendRequest({
        endpoint: endpoint,
        method: 'DELETE'
    });
    console.groupEnd();
};

/**
 * Fetches the flashcard file in the specified file format.
 * @param retrievalToken the token to retrieve the file, provided in the task info when the task is complete (see fetchFlashcardGeneratorTaskInfo)
 * @param fileFormat the file format to download the flashcards in
 * @returns {Promise<{blob: Blob, filename: string}>} the flashcard file as a blob and the filename
 */
export async function fetchFlashcardFile(retrievalToken: string, fileFormat: FileFormat ): Promise<{blob: Blob, filename: string}> {
    console.group('getGeneratorTaskResult');
    if (retrievalToken == null) {
        console.warn('Retrieval token is missing')
        throw new Error('Retrieval token must not be null or undefined');
    }
    const endpoint = `/flashcards/exporter/${retrievalToken}?format=${fileFormat}`;
    console.log(`Endpoint:${ endpoint }`);
    console.log('Method: GET');
    const response = await sendRequest({
        endpoint: endpoint,
        method: 'GET',
        config: { responseType: 'blob' }
    });
    const contentDisposition = response.headers['Content-Disposition'];
    let filename = 'flashcards';
    if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/i);
        if (filenameMatch && filenameMatch.length > 1) {
            filename = filenameMatch[1];
        }
    }
    const blob = response.data;
    console.groupEnd();
    return { blob: blob, filename };
}