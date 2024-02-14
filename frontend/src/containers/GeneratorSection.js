import React, {useEffect, useState} from "react";
import ConfigContainer from "../components/generation_section/1_configuration/ConfigContainer";
import UploadContainer from "../components/generation_section/2_text_upload/UploadContainer";
import GenerationProgressContainer from "../components/generation_section/3_flashcard_generation/GenerationProgressContainer";
import GenerationSteps from "../components/global/GenerationSteps";
import {useHealthCheck} from "./HealthCheckContext";

function GeneratorSection() {
    // App related hooks
    const modelName = 'gpt-3.5-turbo'
    const defaultStep = sessionStorage.getItem('lastGenerationStep') || GenerationSteps.CONFIGURATION;
    const [currentStep, setCurrentStep] = useState(defaultStep);
    const [text, setText] = useState('');
    const [lang, setLang] = useState('');
    const [mode, setMode] = useState('');
    const [exportFormat, setExportFormat] = useState('')
    const [taskId, setTaskId] = useState('');

    // Define corresponding backend values
    const backendLanguageOptions = { English: 'en', German: 'de' };
    const backendModeOptions = { Practice: 'practice', Test: 'test', Cloze: 'cloze' };
    const backendExportOptions = { CSV: 'csv', Anki: 'anki' };
    // TODO: Implement config using a map (more compact)
    // const [config, setConfig] = useState({lang: "", mode: "", exportFormat: ""})

    // Batches of flashcard generation used to calculate progress and display progress bar
    const  [totalBatches, setTotalBatches] = useState(0)
    const [currentBatch, setCurrentBatch] = useState(0);

    // Generated flashcards
    const [flashcards, setFlashcards] = useState([]);

    // TODO: Use environment variables to set API URL or reverse proxy for production server
    // TODO: Enhance exception handling and provide more informative feedback to the user
    // TODO: Retry mechanism
    // TODO: Display success message when flashcards are ready
    const updateFlashcardGenerationProgress = (taskId) => {
        fetch(`flashcards/generate/progress/${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.state === 'PROGRESS') {
                    // Update state with the progress
                    setCurrentBatch(data.progress);
                    if (totalBatches === 0) {setTotalBatches(data.total);}
                    if (data.meta < data.total) {
                        // Continue polling if the work is not yet done
                        setTimeout(() => updateFlashcardGenerationProgress(taskId), 2000); // Poll every 2 seconds
                    }
                } else if (data.state === 'SUCCESS') {
                    // Update UI here
                    setCurrentBatch(totalBatches);
                } else if (data.state === 'FAILURE') {
                    // Exception handling here
                    throw new Error(`Task failed: ${data.error}`)
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Method to generate flashcards with specified mode and text
    // TODO: Add robust error handling

    const startFlashcardGenerationTask = () => {
        console.group('Flashcard Generation Request');
        console.log('Endpoint: /flashcards/generate');
        console.log('Method: POST');
        console.log('Payload:', { lang, mode, exportFormat, inputText: text });
        fetch('/flashcards/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model_name: modelName,
                lang: backendLanguageOptions[lang],
                mode: backendModeOptions[mode],
                export_format: backendExportOptions[exportFormat],
                input_text: text,
            }),
        })
            .then(response => {
                const contentType = response.headers.get('content-type');
                if (!response.ok) {
                    if (contentType && contentType.includes('application/json')) {
                        return response.json().then(errorDetails => {
                            console.error('HTTP Error:', response.status, errorDetails);
                            throw new Error(`HTTP Error ${response.status}: ${JSON.stringify(errorDetails)}`);
                        });
                    } else {
                        console.error('Non-JSON error from server:', response.statusText);
                        throw new Error('Non-JSON error from server');
                    }
                }
                return response.json();
            })
        .then(data => {
            if (!data.task_id) {
                console.warn('Response missing task_id:', data);
                throw new Error('task_id is missing from the response');
            }
            const taskId = data.task_id;
            // Start updating the progress
            updateFlashcardGenerationProgress(taskId);
            setFlashcards(data.flashcards);
        })
        .catch(error => {
            // The error could be from the fetch itself, or thrown from the .then() block
            console.error('Error during flashcard generation:', error);
            // Include stack trace and error object
            console.error(error.stack);
        })
        .finally(() => {
            console.groupEnd();
        });
    }

    const cancelFlashcardGenerationTask = ( taskId ) => {
        console.group('Flashcard Cancellation Request');
        console.log(`Endpoint: /flashcards/generate/cancel/${ taskId }`);
        console.log('Method: POST');
        console.log('Payload:', { taskId });
        fetch(`flashcards/generate/progress/${taskId}`, {method: 'POST'})
            .then(response => response.json())
            .catch(error => console.error('Error:', error));
    }

    // TODO: Add const to make API call to backend:
    // "Generate" -> sends the data from the configuration and the text to the backend and initiates generation, as well
    // as the updates of ProgressBar
    // "Go Back" from GenerationProcessContainer -> stops the generation process, saves the generated flashcard internally.
    // If the user doesn't change the text or config the generate button should say "Continue generating". If the something is changed
    // (i.e. the data is not the same) flashcards are discarded, and the button says "Generate". Reverting changes so that the
    // data is the same as used for the previous flashcard generation counts as "unchanged".

    useEffect(() => {
        // Loads the last generation step from sessionStorage when the component mounts
        const lastGenerationStep = sessionStorage.getItem('lastGenerationStep');
        if (lastGenerationStep) {
            setCurrentStep(lastGenerationStep);
        }
    }, [setCurrentStep]);

    useEffect(() => {
        // Save currentStep to sessionStorage when it changes
        sessionStorage.setItem('lastGenerationStep', currentStep);
    }, [currentStep]);

    const renderContent = () => {
        switch (currentStep) {
            case GenerationSteps.CONFIGURATION:
                return <ConfigContainer setGenerationStep={setCurrentStep} lang={lang} setLang={setLang} mode={mode} setMode={setMode} exportFormat={exportFormat} setExportFormat={setExportFormat}/>;
            case GenerationSteps.TEXT_UPLOAD:
                return <UploadContainer setGenerationStep={setCurrentStep} text={text} setText={setText} generateFlashcards={startFlashcardGenerationTask}/>;
            case GenerationSteps.GENERATION:
                return <GenerationProgressContainer setGenerationStep={setCurrentStep} totalBatches={totalBatches} currentBatch={currentBatch} flashcards={flashcards} cancelFlashcards={() => cancelFlashcardGenerationTask(taskId)} />
            default:
                return <ConfigContainer setGenerationStep={setCurrentStep} lang={lang} setLang={setLang} mode={mode} setMode={setMode} exportFormat={exportFormat} setExportFormat={setExportFormat}/>;
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
                {/*TODO: Add our own paragraph*/}
                <p>Our Flashcard Generator automatically transforms your notes or textbooks into flashcards using
                    the
                    power of artificial intelligence. Simply upload your materials and let our AI create your
                    flashcards
                    in seconds.</p>
            </div>
            {renderContent()}
        </div>
    );
}

export default GeneratorSection;