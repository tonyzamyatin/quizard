import ProgressBar from "./ProgressBar";
import TriviaSlideShow from "./TriviaSlideShow";
import CTAButton from "../../global/CTAButton";
import React from "react";
import GenerationSteps from "../../global/GenerationSteps";

function GenerationProgressContainer({setGenerationStep}) {

    // The total number of flashcard batches being generated
    const totalUpdates = 0;

    // The number of the last flashcard batch that was generated
    const lastUpdate = 0;

    // Receives information about the current flashcard batch being generated
    function receiveUpdate() {

    }
    const renderProgressBar = () => {
        return (
            <ProgressBar/>
        );
    }

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
            <h2>Generating your flashcards.</h2>
            {renderProgressBar()}
            <div className="generation-section-box progress-info-box">
                <h3>Be patient...this might take a few minutes</h3>
                <p>
                    Quizard is hard at work to turn your text into high-quality flashcards. Imagine the pain of doing
                    this manually! Sit tight — the download will start automatically once your flashcards are ready, and
                    we'll give you a heads-up
                </p>
                {renderTriviaSlideShow(totalUpdates, lastUpdate)}
            </div>
            <div className="button-area">
                <CTAButton buttonName="Go back" onButtonClick={handleBackClick}/>
            </div>
        </div>
    );
}

export default GenerationProgressContainer;