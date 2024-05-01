// src/app/dto/generator.ts
import {GenModeOptions, LangOptions, ExportOptions} from "../enums/GeneratorOptions";

export interface GeneratorTask {
        lang: LangOptions;
        mode: GenModeOptions;
        inputText: string;
}

enum TaskState {
        pending = 'PENDING',
        started = 'STARTED',
        inProgress =  'IN_PROGRESS',
        success = 'SUCCESS',
        failure = 'FAILURE',
        retry = 'RETRY',
        revoked = 'REVOKED',
}

export interface GeneratorTaskInfo {
        taskState: TaskState;
        currentBatch?: number;
        totalBatches?: number;
        retrievalToken?: string;
}