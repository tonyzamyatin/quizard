// src/app/dto/GeneratorTaskDto.ts
import {GenModeOptions, LangOptions, ExportOptions} from "../enums/GeneratorOptions";

export class GeneratorTaskDto {
    constructor(
        public lang: LangOptions,
        public mode: GenModeOptions,
        public exportFormat: ExportOptions,
        public inputText: string,
    ) {}
}