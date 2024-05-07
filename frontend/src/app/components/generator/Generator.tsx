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
    const {step, setStep, generatorTaskDto, generatorTaskInfo, fileFormat} = useGeneratorState();
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
                setStep(GeneratorStep.COMPLETE);
            });
        });
    }

    function downloadFlashcards() {
        const blob = localStorage.getItem(`${fileFormat}${taskId}`
        if ()) {
            const flashcards = JSON.parse(localStorage.getItem(`flashcards-${taskId}`));
            const blob = new Blob([JSON.stringify(flashcards, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `flashcards-${taskId}.json`;
            a.click();
        }
    }




    const renderContent = () => {
        switch (step) {
            case GeneratorStep.UPLOAD_TEXT:
                return <UploadPage/>;
            case GeneratorStep.CONFIGURE:
                return <ConfigPage
                    generateFlashcards={generateFlashcards}
                />;
            case GeneratorStep.WAIT:
                return <WaitingPage
                    cancelFlashcards={() => cancelFlashcardGeneratorTask(taskId)}
                />
            case GeneratorStep.COMPLETE:
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