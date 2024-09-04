import {Mode, Language} from "../enum/generatorOptions";
import {GeneratorTask, GeneratorTaskInfo} from "../dto/generator";
import {TaskState} from "../enum/taskState";

export function createDefaultGeneratorTask(): GeneratorTask {
    return {
        lang: null,
        mode: null,
        exportFormat: null,
        inputText: '',
    };
}

export function createDefaultGeneratorTaskInfo(): GeneratorTaskInfo {
    return {
        taskState: TaskState.pending,
    };
}
