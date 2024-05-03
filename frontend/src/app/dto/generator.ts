// src/app/dto/generator.ts
import {Mode, Language, FileFormat} from "../enum/GeneratorOptions";

export interface GeneratorTask {
        lang: Language | null;
        mode: Mode | null;
        inputText: string;
}

export interface GeneratorTaskInfo {
        taskState: TaskState;
        currentBatch?: number;
        totalBatches?: number;
        retrievalToken?: string;
}

export enum TaskState {
        pending = 'PENDING',
        started = 'STARTED',
        inProgress =  'IN_PROGRESS',
        success = 'SUCCESS',
        failure = 'FAILURE',
        retry = 'RETRY',
        revoked = 'REVOKED',
}