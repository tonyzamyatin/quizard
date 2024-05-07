// src/app/dto/generator.ts
import {Mode, Language, FileFormat} from "../enum/generatorOptions";
import {TaskState} from "../enum/taskState";

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

