import React, {useEffect, useState} from "react";
import ConfigContainer from "../components/generation_section/1_configuration/ConfigContainer";
import UploadContainer from "../components/generation_section/2_text_upload/UploadContainer";
import GenerationProgressContainer from "../components/generation_section/3_flashcard_generation/GenerationProgressContainer";
import GenerationSteps from "../components/global/GenerationSteps";

function GeneratorSection() {

    // TODO: Send data from configuration and text input to backend and initiates generation when "Generate Button" is used.
    const defaultStep = sessionStorage.getItem('lastGenerationStep') || GenerationSteps.CONFIGURATION;
    const [currentStep, setCurrentStep] = useState(defaultStep);
    const [text, setText] = useState('');
    const [lang, setLang] = useState('');
    const [mode, setMode] = useState('');
    const [exportFormat, setExportFormat] = useState('')
    // TODO: Implement config using a map (more compact)
    // const [config, setConfig] = useState({lang: "", mode: "", exportFormat: ""})

    // TODO: Get batch numbers from backend
    // Batches of flashcard generation used to calculate progress and display progress bar
    const  [totalBatches, setTotalBatches] = useState(1)
    const [currentBatch, setCurrentBatch] = useState(0);

    // Generated flashcards
    const [flashcards, setFlashcards] = useState([]);


    const updateProgress = (taskId) => {
        fetch(`http://localhost:5000/api/v1/flashcard/generate/progress/${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.state === 'PROGRESS') {
                    // Update state with the progress
                    setCurrentBatch(data.progress);
                    setTotalBatches(data.total);
                    if (data.progress < data.total) {
                        // Continue polling if the work is not yet done
                        setTimeout(() => updateProgress(taskId), 2000); // Poll every 2 seconds
                    }
                } else if (data.state === 'SUCCESS') {
                    // Handle task completion
                } else if (data.state === 'FAILURE') {
                    // Handle task failure
                }
            })
            .catch(error => console.error('Error:', error));
    }


    // TODO: Pass generateFlashcards to Generate button and ensure that the program is robust in handling user behaviour.
    // Method to generate flashcards with specified mode and text
    const generateFlashcards = () => {
        fetch('http://localhost:5000/api/v1/flashcards/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lang: lang,
                mode: mode,
                exportFormat: exportFormat,
                inputText: text,
            }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (!data.task_id) {
                    throw new Error('task_id is missing from the response');
                }
                const taskId = data.task_id;
                // Start updating the progress
                updateProgress(taskId);
                setFlashcards(data.flashcards);
            })
            .catch(error => {
                console.error('Error during flashcard generation:', error);
            });
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
                return <UploadContainer setGenerationStep={setCurrentStep} text={text} setText={setText} generateFlashcards={generateFlashcards}/>;
            case GenerationSteps.GENERATION:
                return <GenerationProgressContainer setGenerationStep={setCurrentStep} totalBatches={totalBatches} currentBatch={currentBatch} flashcards={flashcards}/>
        }
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