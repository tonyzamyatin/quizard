import {Mode, Language} from "../enum/GeneratorOptions";
import {GeneratorTask, GeneratorTaskInfo, TaskState} from "../dto/generator";

export function createDefaultGeneratorTask(): GeneratorTask {
    return {
        lang: null,
        mode: null,
        inputText: '',
    };
}

export function createDefaultGeneratorTaskInfo(): GeneratorTaskInfo {
    return {
        taskState: TaskState.pending,
    };
}
