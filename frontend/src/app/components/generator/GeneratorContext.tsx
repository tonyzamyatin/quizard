import {GeneratorTask, GeneratorTaskInfo} from "../../dto/generator";
import {createContext, ReactNode, useContext} from "react";
import {createDefaultGeneratorTask, createDefaultGeneratorTaskInfo} from "../../util/dtoUtil";
import {GeneratorStep} from "../../enum/GeneratorStep";
import {useFlashcardGenerator} from "../../hooks/useFlashcardGenerator";


/**
 * Generator state context interface (for TS type checking)
 */
interface GeneratorState  {
    step: GeneratorStep;
    setStep: (step: GeneratorStep) => void;
    generatorTaskDto: GeneratorTask;
    setGeneratorTaskDto: (generatorTaskDto: GeneratorTask) => void;
    generatorTaskInfo: GeneratorTaskInfo,
    setGeneratorTaskInfo: (generatorTaskInfo: GeneratorTaskInfo) => void;
    generateFlashcards: () => void;
    downloadFlashcards: () => void;
    cancelFlashcards: () => void;
}

/**
 * Generator state context definition of the generator state provided to the child components.
 * GeneratorState interface defines the context value (for TS type checking).
 * Default values are set for all values (initial state, necessity).
 */
const GeneratorStateContext = createContext<GeneratorState>({
    step: GeneratorStep.UPLOAD_TEXT,
    setStep: () => {},
    generatorTaskDto: createDefaultGeneratorTask(),
    setGeneratorTaskDto: () => {},
    generatorTaskInfo: createDefaultGeneratorTaskInfo(),
    setGeneratorTaskInfo: () => {},
    generateFlashcards: () => {},
    downloadFlashcards: () => {},
    cancelFlashcards: () => {},
});

/**
 * Custom hook that returns the generator state context.
 * @returns generator state context
 */
export const useGeneratorState = () => useContext(GeneratorStateContext);

/**
 * Provider component that wraps the application and provides the generator state context to all child components.
 * Uses the {@link useFlashcardGenerator} hook to get the generator state.
 * @param children - child components to which the generator state context is provided
 */
export function GeneratorStateProvider({ children } :  { children: ReactNode }) {
    const flashcardGenerator = useFlashcardGenerator();

    return (
        <GeneratorStateContext.Provider value={ flashcardGenerator }>
            { children }
        </GeneratorStateContext.Provider>
    );
}
