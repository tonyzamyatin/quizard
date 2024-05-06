// TODO: Better logging
// TODO: Add doc strings


import {GeneratorStep} from "../enum/GeneratorStep";
import {GeneratorTask, GeneratorTaskInfo, TaskState,} from "../dto/generator";
import {sendRequest} from "../util/requestUtil";
import {FileFormat} from "../enum/GeneratorOptions";


// API Endpoint
const endpoint = '/flashcards/generator';

export async function startFlashcardGeneratorTask(generatorTaskDto: GeneratorTask): Promise<string> {
    console.group('startFlashcardGeneratorTask');
    console.info(`Endpoint: ${endpoint}`);
    console.info('Method: POST');
    console.info('Payload:', generatorTaskDto);
    console.groupEnd();
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
    return taskId;
}

async function getFlashcardGeneratorTaskInfo(taskId: string): Promise<GeneratorTaskInfo> {
    const endpoint = `/flashcards/generator/${taskId}`;
    console.group('getFlashcardGeneratorTaskInfo');
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

export async function exportGeneratorTaskResult(retrievalToken: string, fileFormat: FileFormat ) {
    console.group('getGeneratorTaskResult');
    if (retrievalToken == null) {
        console.warn('Retrieval token is missing')
        return;
    }
    // @ts-ignore - FileFormat is an enum
    const fileFormatKey = FileFormat[fileFormat];
    const endpoint = `/flashcards/exporter/${retrievalToken}?format=${fileFormatKey}`;
    console.log(`Endpoint:${ endpoint }`);
    console.log('Method: DELETE');
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
    return { blob: response.data, filename };
}