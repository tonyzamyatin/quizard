import React from "react";
import ProgressBar from "./ProgressBar";
import TriviaSlideShow from "./TriviaSlideShow";
import CTAButton from "../../global/CTAButton";
import GenerationSteps from "../../global/GenerationSteps";

function WaitingPage({setGenerationStep, totalBatches, currentBatch, cancelFlashcards}) {

    // Progress of flashcard generation process in percent
    const progress = currentBatch / totalBatches * 100

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

    const handleCancelClick = () => {
        setGenerationStep(GenerationSteps.CONFIGURATION);
        cancelFlashcards();
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
                <CTAButton buttonText="Cancel" buttonType={'secondary'} onButtonClick={handleCancelClick} active={true}/>
            </div>
        </div>
    );
}

export default WaitingPage;