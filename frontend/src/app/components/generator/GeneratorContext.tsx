import {GeneratorTask, GeneratorTaskInfo} from "../../dto/generator";
import {createContext, ReactNode, useContext, useState} from "react";
import {createDefaultGeneratorTask, createDefaultGeneratorTaskInfo} from "../../util/dtoUtil";
import {FileFormat} from "../../enum/GeneratorOptions";
import {GeneratorStep} from "../../enum/GeneratorStep";
import {ChildProp} from "../../../types";

interface GeneratorState  {
    // State interface for TS type checking
    step: GeneratorStep;
    setStep: (step: GeneratorStep) => void;
    generatorTaskDto: GeneratorTask;
    setGeneratorTaskDto: (generatorTaskDto: GeneratorTask) => void;
    generatorTaskInfo: GeneratorTaskInfo,
    setGeneratorTaskInfo: (generatorTaskInfo: GeneratorTaskInfo) => void;
    fileFormat: FileFormat | null
    setFileFormat: (fileFormat: FileFormat | null) => void;
}

// Context definition with default values for TS type checking
const GeneratorStateContext = createContext<GeneratorState>({
    step: GeneratorStep.UploadText,
    setStep: () => {},
    generatorTaskDto: createDefaultGeneratorTask(),
    setGeneratorTaskDto: () => {},
    generatorTaskInfo: createDefaultGeneratorTaskInfo(),
    setGeneratorTaskInfo: () => {},
    fileFormat: null,
    setFileFormat: () => {},
});

// Functional provider component to provide the generator state context to the child components
export function GeneratorStateProvider({ children } :  ChildProp) {
    const [step, setStep] = useState<GeneratorStep>(() => {
        const savedStep = localStorage.getItem('savedStep');
        if (!(savedStep === null || !(savedStep in GeneratorStep))) {
            return savedStep as GeneratorStep;
        } else {
            return GeneratorStep.UploadText;   // Default
        }
    });
    const [fileFormat, setFileFormat] = useState<FileFormat | null>(() => {
        const savedFileFormat = localStorage.getItem('savedFileFormat');
        if (!(savedFileFormat === null || !(savedFileFormat in FileFormat))) {
            return savedFileFormat as FileFormat;
        } else {
            return null;   // Default
        }
    });
    const [generatorTaskDto, setGeneratorTaskDto] = useState<GeneratorTask>(() => {
        const savedTaskDto = localStorage.getItem('savedGeneratorTaskDto');
        return savedTaskDto ? JSON.parse(savedTaskDto) : createDefaultGeneratorTask();
    });
    const [generatorTaskInfo, setGeneratorTaskInfo] = useState<GeneratorTaskInfo>(() => {
        return createDefaultGeneratorTaskInfo();
    });
    return (
        <GeneratorStateContext.Provider value={
            {
                step,
                setStep,
                generatorTaskDto,
                setGeneratorTaskDto,
                generatorTaskInfo,
                setGeneratorTaskInfo,
                fileFormat,
                setFileFormat
            }
        }>
            {children}
        </GeneratorStateContext.Provider>
    );
}

/**
 * Custom hook to use the generator state context in functional components.
 */
export const useGeneratorState = () => useContext(GeneratorStateContext);