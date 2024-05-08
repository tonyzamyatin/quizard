// src/app/hooks/useFlashcardGenerator.ts
import {useEffect, useState} from 'react';
import {
    cancelFlashcardGeneratorTask,
    startFlashcardGeneratorTask,
    fetchFlashcardFile, fetchFlashcardGeneratorTaskInfo
} from "../service/generatorService";
import {GeneratorStep} from "../enum/GeneratorStep";
import {createDefaultGeneratorTask, createDefaultGeneratorTaskInfo} from "../util/dtoUtil";
import {downloadBlob} from "../util/downloadUtil";
import {FileFormat} from "../enum/generatorOptions";
import {TaskState} from "../enum/taskState";
import {config} from "../config";

/*
 * TODO: Display meaningful error messages to the user
 * TODO: Use environment variables to set API URL or reverse proxy for production browser
 * TODO: Centralize logging and exception handling
 */

/**
 * Custom hook to manage the flashcard generator state and handle the flashcard generator task lifecycle.
 */
export function useFlashcardGenerator() {
    /*
        * State management for the flashcard generator
        * Cache the step, file format, generator task DTO in local storage.
     */
    const [step, setStep] = useState(() => {
        const savedStep = sessionStorage.getItem('savedStep');
        return savedStep ? (savedStep as GeneratorStep) : GeneratorStep.UPLOAD_TEXT;
    });
    const [fileFormat, setFileFormat] = useState(() => {
        const savedFileFormat = sessionStorage.getItem('savedFileFormat');
        return savedFileFormat ? (savedFileFormat as FileFormat) : null;
    });
    const [generatorTaskDto, setGeneratorTaskDto] = useState(() => {
        const savedTaskDto = sessionStorage.getItem('savedGeneratorTaskDto');
        return savedTaskDto ? JSON.parse(savedTaskDto) : createDefaultGeneratorTask();
    });
    const [generatorTaskInfo, setGeneratorTaskInfo] = useState(createDefaultGeneratorTaskInfo());
    const [taskId, setTaskId] = useState('');
    const [pollingIntervalId, setPollingIntervalId] = useState<number | null>(null);

    // Save step  to session storage whenever they change
    useEffect(() => {
        sessionStorage.setItem('savedStep', step);
    }, [step]);

    // Save file format to session storage whenever it changes
    useEffect(() => {
        if (fileFormat) {
            sessionStorage.setItem('savedFileFormat', fileFormat);
        }
    }, [fileFormat]);

    // Save generator task DTO to session storage whenever it changes
    useEffect(() => {
        sessionStorage.setItem('savedGeneratorTaskDto', JSON.stringify(generatorTaskDto));
    }, [generatorTaskDto]);

    /**
     * Poll the flashcard generator task until it is complete.
     * Polling starts when the step is set to 'WAIT'.
     * The polling interval is set to 'pollingDelayLong' when the task is pending and 'pollingDelayShort' when the task is in progress.
     */
    useEffect(() => {
        if (step === GeneratorStep.WAIT) {
            let timeout = config.generator.pollingDelayLong;
            const intervalId = window.setInterval(async () => {
                const taskInfo = await fetchFlashcardGeneratorTaskInfo(taskId);
                setGeneratorTaskInfo(taskInfo);
                if (taskInfo.taskState === TaskState.success) {
                    clearInterval(intervalId);
                    setStep(GeneratorStep.COMPLETE);
                }
                if (taskInfo.taskState === TaskState.inProgress) {
                    timeout = config.generator.pollingDelayShort;
                }
            }, timeout);    // Poll every 'timeout' milliseconds
            setPollingIntervalId(intervalId);
        }

        // useEffect returns a cleanup function that runs when the component unmounts or before the next time the side effect runs.
        return () => {
            if (pollingIntervalId) {
                clearInterval(pollingIntervalId);
            }
        };
    }, [step, taskId, generatorTaskInfo]);

    /**
     * Start the flashcard generator task and set the step to 'WAIT'.
     */
    async function generateFlashcards() {
        const taskId = await startFlashcardGeneratorTask(generatorTaskDto);
        setTaskId(taskId);
        setStep(GeneratorStep.WAIT);
    }

    /**
     * Download the flashcard file in the specified file format, if either the file is
     * available in session storage or the retrieval token and file format are available in the generator state.
     */
    async function downloadFlashcards() {
        // Check if the flashcard file is already stored in session storage
        const flashcardResultJSON = sessionStorage.getItem(`${fileFormat}${taskId}`);
        let flashcardBlob;
        let flashcardFileName;

        if (flashcardResultJSON) {
            const flashcardResult = JSON.parse(flashcardResultJSON);
            flashcardBlob = await fetch(flashcardResult.blob).then(r => r.blob());
            flashcardFileName = flashcardResult.filename;
        } else {
            const retrievalToken = generatorTaskInfo.retrievalToken;
            if (!retrievalToken || !fileFormat) {
                return;
            }
            const result = await fetchFlashcardFile(retrievalToken, fileFormat);
            flashcardBlob = result.blob;
            flashcardFileName = result.filename;

            // Save the flashcard file to session storage
            const reader = new FileReader();
            reader.readAsDataURL(result.blob);
            reader.onloadend = function () {
                const base64data = reader.result;
                const resultToStore = {blob: base64data, filename: result.filename};
                sessionStorage.setItem(`${fileFormat}${taskId}`, JSON.stringify(resultToStore));
            };
        }
        if (flashcardBlob && flashcardFileName) {
            downloadBlob(flashcardBlob, flashcardFileName);
        }
    }

    /**
     * Cancel the flashcard generator task and set the step to 'UPLOAD_TEXT'.
     */
    async function cancelFlashcards() {
        await cancelFlashcardGeneratorTask(taskId);
        setStep(GeneratorStep.UPLOAD_TEXT);
    }

    return {
        step,
        setStep,
        generatorTaskDto,
        setGeneratorTaskDto,
        generatorTaskInfo,
        setGeneratorTaskInfo,
        fileFormat,
        setFileFormat,
        generateFlashcards,
        downloadFlashcards,
        cancelFlashcards,
    };
}