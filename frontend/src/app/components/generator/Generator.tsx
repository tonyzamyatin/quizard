import React, {useEffect, useRef, useState} from "react";
import ConfigPage from "./configuration/ConfigPage";
import UploadPage from "./text upload/UploadPage";
import WaitingPage from "./progress/WaitingPage";
import CompletionPage from "./completion/CompletionPage";
import {cancelFlashcardGenerationTask, startFlashcardGenerationTask, pollFlashcardGenerationTask} from "../../service/GeneratorService";
import {useHealthCheck} from "./HealthCheckContext";
import {GenerationSteps} from "../../enums/GenerationSteps";



// TODO: Use environment variables to set API URL or reverse proxy for production browser
// TODO: Enhance exception handling and provide more informative feedback to the user

function Generator() {
    const isDevelopmentMode = process.env.NODE_ENV === 'development';
    // App related hooks
    const modelName = 'gpt-3.5-turbo'
    const startStep = localStorage.getItem('lastGenerationStep') || GenerationSteps.TextUpload
    const [currentStep, setCurrentStep] = useState(startStep);
    const [text, setText] = useState('');
    const [lang, setLang] = useState('');
    const [mode, setMode] = useState('');
    const [exportFormat, setExportFormat] = useState('')
    const [generatorTaskDto, setGeneratorTaskDto] = useState(null);
    const [taskId, setTaskId] = useState('');
    const isPollingActiveRef = useRef(false);




    // Batches of flashcard generation used to calculate progress and display progress bar
    const [currentBatch, setCurrentBatch] = useState(0);
    const  [totalBatches, setTotalBatches] = useState(1)

    // Generated flashcards
    const [flashcards, setFlashcards] = useState(null);     // JSON object



    isPollingActiveRef.current = true;
    setTaskId(data.taskId);
    console.log(`Task started! Task Id: ${taskId}`)
    pollFlashcardGenerationTask(data.taskId);

    useEffect(() => {
        // useEffect for polling, triggered when taskId changes
        let timeoutId = null;

        if (taskId && isPollingActiveRef.current) {
            timeoutId = setTimeout(() => pollFlashcardGenerationTask(taskId), 40000);
        }

        // Clean up the timeout when taskId changes or component unmounts
        return () => clearTimeout(timeoutId);
    }, [taskId]);


    useEffect(() => {
        // Loads the last generation step from sessionStorage when the component mounts
        const lastGenerationStep = localStorage.getItem('lastGenerationStep');
        if (lastGenerationStep) {
            setCurrentStep(lastGenerationStep);
        }
    }, [setCurrentStep]);

    useEffect(() => {
        // Save currentStep to sessionStorage when it changes
        localStorage.setItem('lastGenerationStep', currentStep);
    }, [currentStep]);


    const renderContent = () => {
        switch (currentStep) {
            case GenerationSteps.TextUpload:
                return <UploadPage
                    setGenerationStep={setCurrentStep}
                    text={text}
                    setText={setText}
                />;
            case GenerationSteps.Configuration:
                return <ConfigPage
                    setGenerationStep={setCurrentStep}
                    lang={lang}
                    setLang={setLang}
                    mode={mode}
                    setMode={setMode}
                    exportFormat={exportFormat}
                    setExportFormat={setExportFormat}
                    generateFlashcards={startFlashcardGenerationTask}
                />;
            case GenerationSteps.Generation:
                return <WaitingPage
                    setGenerationStep={setCurrentStep}
                    totalBatches={totalBatches}
                    currentBatch={currentBatch}
                    cancelFlashcards={() => cancelFlashcardGenerationTask(taskId)}
                />
            case GenerationSteps.Complete:
                return <CompletionPage
                    setGenerationStep={setCurrentStep}
                    setText={setText}
                />
            default:
                return <ConfigPage
                    setGenerationStep={setCurrentStep}
                    lang={lang}
                    setLang={setLang}
                    mode={mode}
                    setMode={setMode}
                    exportFormat={exportFormat}
                    setExportFormat={setExportFormat}/>;
        }
    }


    // Check health status of backend and show error message immediately if it is down.
    const { isBackendHealthy } = useHealthCheck();
    if (!isBackendHealthy) {
        return <div>Service is currently unavailable. Please try again later.</div>;
    }
    return (
        <div className="generator-section">
            <div className="description">
                <h1>Quizard Flashcard Generator</h1>
                <p>Our Flashcard Generator automatically transforms your notes or textbooks into flashcards using the power of AI. Simply upload your text and lean back!</p>
            </div>
            {renderContent()}
        </div>
    );
}

export default Generator;