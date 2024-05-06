import React, {createContext, useEffect, useRef, useState} from "react";
import ConfigPage from "./ConigurationComponent/ConfigPage";
import UploadPage from "./TextUploadComponent/UploadPage";
import WaitingPage from "./WaitingComponent/WaitingPage";
import CompletionPage from "./CompletionComponent/CompletionPage";
import {cancelFlashcardGeneratorTask, startFlashcardGeneratorTask, pollFlashcardGeneratorTask} from "../../service/generatorService";
import {GeneratorStep} from "../../enum/GeneratorStep";
import {GeneratorStateProvider, useGeneratorState} from "./GeneratorContext";


/**
 * TODO: Display meaningful error messages to the user
 * TODO: Use environment variables to set API URL or reverse proxy for production browser
 * TODO: Enhance exception handling and provide more informative feedback to the user
 */

function Generator() {
    const isDevelopmentMode = process.env.NODE_ENV === 'development';

    // App related hooks
    const {step, setStep, generatorTaskDto, generatorTaskInfo} = useGeneratorState();
    const [taskId, setTaskId] = useState('');
    const isPollingActiveRef = useRef(false);


    // Generated flashcards
    const [flashcards, setFlashcards] = useState(null);     // JSON object

    // Main function for the flashcard generation process
    function generateFlashcards() {
        startFlashcardGeneratorTask(generatorTaskDto)
            .then(taskId => {
                setTaskId(taskId);
                pollFlashcardGeneratorTask(
                    taskId,
                    (current) => {generatorTaskInfo.currentBatch = current},
                    (total) => {generatorTaskInfo.totalBatches = total},
                )
                    .then(() => {
                setStep(GeneratorStep.Complete);
            });
        });
    }

    function downloadFlashcards() {

    }

    useEffect(() => {
        // useEffect for polling, triggered when taskId changes
        let timeoutId = null;

        if (taskId && isPollingActiveRef.current) {
            timeoutId = setTimeout(() => pollFlashcardGeneratorTask(taskId), 40000);
        }

        // Clean up the timeout when taskId changes or component unmounts
        return () => clearTimeout(timeoutId);
    }, [taskId]);

    const renderContent = () => {
        switch (step) {
            case GeneratorStep.UploadText:
                return <UploadPage/>;
            case GeneratorStep.Configure:
                return <ConfigPage
                    generateFlashcards={generateFlashcards}
                />;
            case GeneratorStep.Wait:
                return <WaitingPage
                    cancelFlashcards={() => cancelFlashcardGeneratorTask(taskId)}
                />
            case GeneratorStep.Complete:
                return <CompletionPage
                    downloadFlashcards={downloadFlashcards}
                />
            default:
                return <UploadPage />;
        }
    }
    return (
            <GeneratorStateProvider>
                {renderContent()}
            </GeneratorStateProvider>
    );
}

export default Generator;