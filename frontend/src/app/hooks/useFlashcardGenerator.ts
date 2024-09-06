// src/app/hooks/useFlashcardGenerator.ts
import {useEffect, useRef, useState} from 'react';
import {
    cancelFlashcardGeneratorTask,
    fetchFlashcardFile,
    fetchFlashcardGeneratorTaskInfo,
    startFlashcardGeneratorTask
} from "../service/generatorService";
import {GeneratorStep} from "../enum/GeneratorStep";
import {createDefaultGeneratorTask, createDefaultGeneratorTaskInfo} from "../util/dtoUtil";
import {downloadBlob} from "../util/downloadUtil";
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
    const [generatorTaskDto, setGeneratorTaskDto] = useState(() => {
        const savedTaskDto = sessionStorage.getItem('savedGeneratorTaskDto');
        return savedTaskDto ? JSON.parse(savedTaskDto) : createDefaultGeneratorTask();
    });
    const [generatorTaskInfo, setGeneratorTaskInfo] = useState(createDefaultGeneratorTaskInfo());
    const [taskId, setTaskId] = useState('');
    const pollingIntervalId = useRef<number | null>(null);
    const isPollingActive = useRef(false);
    const [pollingTimeout, setPollingTimeOut] = useState(config.generator.pollingDelayLong)

    // Save step  to session storage whenever they change
    useEffect(() => {
        sessionStorage.setItem('savedStep', step);
    }, [step]);

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
        // console.debug('Polling use effect called')
        if (step === GeneratorStep.WAIT && taskId) {
            // console.debug('Activating polling')
            isPollingActive.current = true
            pollingIntervalId.current = window.setInterval(taskPollingHandler, pollingTimeout);
        }
        return () => {
            if (pollingIntervalId.current) {
                clearInterval(pollingIntervalId.current);
            }
        };
    }, [step, taskId, taskPollingHandler]);

    async function taskPollingHandler() {
        try {
            console.debug('Task polling called')
            console.debug('Is polling active:', isPollingActive.current)
            if (step !== GeneratorStep.WAIT) return;
            if (!isPollingActive.current) return;

            isPollingActive.current = true;
            const taskInfo = await fetchFlashcardGeneratorTaskInfo(taskId);
            setGeneratorTaskInfo(taskInfo);
            if (taskInfo.taskState === TaskState.success) {
                setStep(GeneratorStep.COMPLETE);
                // Reset all polling variables
                if (pollingIntervalId.current) {
                    clearInterval(pollingIntervalId.current);
                }
                isPollingActive.current = false;
                setPollingTimeOut(config.generator.pollingDelayLong);
            }
            if (taskInfo.taskState === TaskState.inProgress) {
                setPollingTimeOut(config.generator.pollingDelayShort);
            }
        } catch (error) {
            console.log('Error occurred when polling flashcard generator task:', error);
            isPollingActive.current = false;
        }
    }

    /**
     * Start the flashcard generator task and set the step to 'WAIT'.
     */
    async function generateFlashcards() {
        try {
            const taskId = await startFlashcardGeneratorTask(generatorTaskDto);
            setTaskId(taskId);
            setStep(GeneratorStep.WAIT);
        } catch (error) {
            console.log('Error occurred when starting flashcard generation:', error)
        }
    }

    /**
     * Download the flashcard file in the specified file format, if either the file is
     * available in session storage or the retrieval token and file format are available in the generator state.
     */
    async function downloadFlashcards() {
        // Check if the flashcard file is already stored in session storage
        const fileFormat = generatorTaskDto.exportFormat;
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
            try {

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
            } catch (error) {
                console.log('Error occurred when downloading flashcards:', error);
            }
        }
        if (flashcardBlob && flashcardFileName) {
            downloadBlob(flashcardBlob, flashcardFileName);
        }
    }

    /**
     * Cancel the flashcard generator task and set the step to 'UPLOAD_TEXT'.
     */
    async function cancelFlashcards() {
        isPollingActive.current = false
        setGeneratorTaskInfo(createDefaultGeneratorTaskInfo)
        try {
            await cancelFlashcardGeneratorTask(taskId);

        } catch (error) {
            console.log('Error occurred when cancelling flashcard generation:', error);
        }
        setStep(GeneratorStep.UPLOAD_TEXT);
    }

    return {
        step,
        setStep,
        generatorTaskDto,
        setGeneratorTaskDto,
        generatorTaskInfo,
        setGeneratorTaskInfo,
        generateFlashcards,
        downloadFlashcards,
        cancelFlashcards,
    };
}