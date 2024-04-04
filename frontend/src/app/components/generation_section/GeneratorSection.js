import React, {useEffect, useRef, useState} from "react";
import ConfigPage from "./1_configuration/ConfigPage";
import UploadPage from "./2_text_upload/UploadPage";
import WaitingPage from "./3_flashcard_generation/WaitingPage";
import CompletionPage from "./4_flashcard_download/CompletionPage";
import GenerationSteps from "../global/GenerationSteps";

function GeneratorSection() {
    const isDevelopmentMode = process.env.NODE_ENV === 'development';
    // App related hooks
    const modelName = 'gpt-3.5-turbo'
    const defaultStep = localStorage.getItem('lastGenerationStep') || GenerationSteps.TEXT_UPLOAD;
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
    const backendExportOptions = { CSV: 'csv', Anki: 'apkg' };

    // Batches of flashcard generation used to calculate progress and display progress bar
    const [currentBatch, setCurrentBatch] = useState(0);
    const  [totalBatches, setTotalBatches] = useState(1)

    // Generated flashcards
    const [flashcards, setFlashcards] = useState(null);     // JSON object


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
            case GenerationSteps.TEXT_UPLOAD:
                return <UploadPage
                    setGenerationStep={setCurrentStep}
                    text={text}
                    setText={setText}
                />;
            case GenerationSteps.CONFIGURATION:
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
            case GenerationSteps.GENERATION:
                return <WaitingPage
                    setGenerationStep={setCurrentStep}
                    totalBatches={totalBatches}
                    currentBatch={currentBatch}
                    cancelFlashcards={() => cancelFlashcardGenerationTask(taskId)}
                />
            case GenerationSteps.COMPLETE:
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


    // TODO: Use environment variables to set API URL or reverse proxy for production browser
    // TODO: Enhance exception handling and provide more informative feedback to the user

    // Method to generate flashcards with specified mode and text
    const startFlashcardGenerationTask = () => {
        const endpoint = '/flashcards/generator';
        const payload = {
            model_name: modelName,
            lang: backendLanguageOptions[lang],
            mode: backendModeOptions[mode],
            exportFormat: backendExportOptions[exportFormat],
            input_text: text,
        };
        console.group('Flashcard Generation Request');
        console.log(`Endpoint: ${endpoint}`);
        console.log('Method: POST');
        console.log('Payload:', payload);
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
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
                        console.error('Non-JSON error from browser:', response.statusText);
                        throw new Error('Non-JSON error from browser');
                    }
                }
                return response.json();
            })
        .then(data => {
            if (!data.taskId) {
                console.warn('Response missing taskId:', data);
                throw new Error('taskId is missing from the response');
            } else {
                isPollingActiveRef.current = true;
                setTaskId(data.taskId);
                console.log(`Task started! Task Id: ${taskId}`)
                pollFlashcardGenerationTask(data.taskId);
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


    const pollFlashcardGenerationTask = (taskId, waitDelay = 1000, updateDelay = 1000) => {
        if (!isPollingActiveRef.current) return;

        const endpoint = `/flashcards/generator/${taskId}`;
        console.group('Flashcard Update Request');
        console.log(`Endpoint:${ endpoint }`);
        console.log('Method: GET');
        fetch(endpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Data received:', data); if (data.state === 'FAILURE') {
                    console.error(`Task ${data.state.toLowerCase()}: ${data.error}`);
                } else {
                    setCurrentBatch(data.progress);
                    setTotalBatches(data.total);
                    if (['PROCESSING', 'STARTED', 'PENDING'].includes(data.state)) {
                        let timeout = data.state === 'PROCESSING' ? updateDelay : waitDelay;
                        setTimeout(() => pollFlashcardGenerationTask(taskId), timeout);
                    } else {
                        isPollingActiveRef.current = false;
                        if (data.state === 'SUCCESS') {
                            if (!data.retrievalToken) {
                                console.warn('Response missing retrievalToken:', data);
                                throw new Error('retrievalToken is missing from the response');
                            } else {
                                const retrievalToken = data.retrievalToken;
                                setCurrentStep(GenerationSteps.COMPLETE);
                                downloadFlashcards(retrievalToken);
                            }
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // setTimeout(() => pollFlashcardGenerationTask(taskId), waitDelay);    // Uncomment me when done with UI design
            })
            .finally(() => {
                console.groupEnd();
            });
    };

    const cancelFlashcardGenerationTask = ( taskId ) => {
        isPollingActiveRef.current = false; // Stop polling
        const endpoint = `/flashcards/generator/${taskId}`
        console.group('Flashcard Cancellation Request');
        console.log(`Endpoint:${ endpoint }`);
        console.log('Method: DELETE');
        fetch(endpoint, {method: 'DELETE'})
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

    const downloadFlashcards = ( retrievalToken ) => {
        if (retrievalToken != null) {
            const endpoint = `/flashcards/retriever/${retrievalToken}`;
            console.group('Flashcard Download Request');
            console.log(`Endpoint:${ endpoint }`);
            console.log('Method: GET');
            fetch(endpoint)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.blob()
                }).then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = exportFormat === 'csv' ? 'flashcards.csv' : 'flashcards.apkg';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
                .catch(error => {
                    console.error('Error during file download:', error);
                });
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

export default GeneratorSection;