import React, {useEffect, useRef, useState} from "react";
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
    const isPollingActiveRef = useRef(false);
    // Define corresponding backend values
    const backendLanguageOptions = { English: 'en', German: 'de' };
    const backendModeOptions = { Practice: 'practice', Test: 'test', Cloze: 'cloze' };
    const backendExportOptions = { CSV: 'csv', Anki: 'anki' };

    // Batches of flashcard generation used to calculate progress and display progress bar
    const [currentBatch, setCurrentBatch] = useState(0);
    const  [totalBatches, setTotalBatches] = useState(1)

    // Generated flashcards
    const [flashcards, setFlashcards] = useState([]);

    // TODO: Use environment variables to set API URL or reverse proxy for production server
    // TODO: Enhance exception handling and provide more informative feedback to the user
    // TODO: Retry mechanism
    // TODO: Display success message when flashcards are ready


    // Method to generate flashcards with specified mode and text
    // TODO: Add robust error handling
    const startFlashcardGenerationTask = () => {
        const endpoint = '/api/mvp/flashcards/generate/start'
        console.group('Flashcard Generation Request');
        console.log(`Endpoint: ${endpoint}`);
        console.log('Method: POST');
        console.log('Payload:', { lang, mode, exportFormat, inputText: text });
        fetch(endpoint, {
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
                            console.error(`HTTP error! status:${response.status}, ${JSON.stringify(errorDetails)}`);
                            throw new Error(`HTTP error! status: ${response.status}`);
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
            } else {
                setTaskId(data.task_id);
                console.log(`Task started! Task Id: ${taskId}`)
                isPollingActiveRef.current = true;
                updateFlashcardGenerationProgress(data.task_id);
                setFlashcards(data.flashcards);
            }
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


    const updateFlashcardGenerationProgress = (taskId, retryDelay = 20000) => {
        if (!isPollingActiveRef.current) return;

        const endpoint = `/api/mvp/flashcards/generate/progress/${taskId}`;
        console.group('Flashcard Update Request');
        console.log(`Endpoint:${ endpoint }`);
        console.log('Method: GET');
        console.log('Payload:', { taskId });

        fetch(endpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Data received:', data);
                if (['PROCESSING', 'STARTED', 'PENDING'].includes(data.state)) {
                    setCurrentBatch(data.progress);
                    setTotalBatches(data.total);
                    let timeout = data.state === 'PROCESSING' ? 30000 : 50000;
                    setTimeout(() => updateFlashcardGenerationProgress(taskId), timeout);
                } else if (data.state === 'SUCCESS') {
                    console.log(`Task successful, current batch: ${currentBatch}, total batches: ${totalBatches}`);
                    setCurrentBatch(totalBatches);
                } else if (['FAILURE', 'CANCELLED'].includes(data.state)) {
                    console.error(`Task ${data.state.toLowerCase()}: ${data.error}`);
                } else {
                    console.log('Did not enter conditional block');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                setTimeout(() => updateFlashcardGenerationProgress(taskId), retryDelay);
            })
            .finally(() => {
                console.groupEnd();
            });
    };

    const cancelFlashcardGenerationTask = ( taskId ) => {
        isPollingActiveRef.current = false; // Stop polling
        const endpoint = `/api/mvp/flashcards/generate/cancel/${taskId}`
        console.group('Flashcard Cancellation Request');
        console.log(`Endpoint:${ endpoint }`);
        console.log('Method: GET');
        console.log('Payload:', { taskId });
        fetch(`/api/mvp/flashcards/generate/cancel/${taskId}`, {
            method: 'GET' // or 'POST' if you have additional data to send
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Cancellation successful:', data);
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                console.groupEnd();
            });
    };


    // useEffect for polling, triggered when taskId changes
    useEffect(() => {
        let timeoutId = null;

        if (taskId && isPollingActiveRef.current) {
            timeoutId = setTimeout(() => updateFlashcardGenerationProgress(taskId), 5000);
        }

        // Clean up the timeout when taskId changes or component unmounts
        return () => clearTimeout(timeoutId);
    }, [taskId]);

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