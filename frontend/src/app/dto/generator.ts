// src/app/dto/generator.ts
import {TaskState} from "../enum/taskState";
import {FileFormat, Language, Mode} from "../enum/GeneratorOptions";

export interface GeneratorTask {
        lang: Language | null;
        mode: Mode | null;
        exportFormat: FileFormat | null;
        inputText: string;
}

export interface GeneratorTaskInfo {
        taskState: TaskState;
        currentBatch?: number;
        totalBatches?: number;
        retrievalToken?: string;
}

