import React, {useState} from "react";
import ProgressBar from "./ProgressBar";
import TriviaSlideShow from "./TriviaSlideShow";
import CTAButton from "../../global/CTAButton";
import GenerationSteps from "../../global/GenerationSteps";

function GenerationProgressContainer({setGenerationStep, totalBatches, currentBatch, flashcards}) {

    // The number of the last flashcard batch that was generated
    const [currentUpdate, setCurrentUpdate] = useState(60);

    // Progress of flashcard generation process in percent
    const progress = currentBatch / totalBatches * 100

    // Receives information about the current flashcard batch being generated
    function receiveUpdate() {

    }
    const renderProgressBar = () => {
        return <ProgressBar progress={progress}/>;
    }

    // Slide show to display trivia and fun facts while user waits during flashcard generation
    // TODO: Implement after test version is launched
    const renderTriviaSlideShow = () => {
        return (
            <TriviaSlideShow />
        );
    }

    const handleBackClick = () => {
        setGenerationStep(GenerationSteps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container progress-container">
            <h2>Generating your flashcards</h2>
            <div className="generation-section-box">
                <div className="progress-box">
                    <div className="progress-info-container">
                        <h3>Be patient...this might take a few minutes</h3>
                        <p>
                            Quizard is hard at work to turn your text into high-quality flashcards. Imagine the pain of doing
                            this manually! Sit tight — the download will start automatically once your flashcards are ready, and
                            we'll give you a heads-up
                        </p>
                    </div>
                    {renderProgressBar()}
                </div>
            </div>
            <div className="button-area">
                <CTAButton buttonName="Go back" onButtonClick={handleBackClick} active={true}/>
            </div>
        </div>
    );
}

export default GenerationProgressContainer;