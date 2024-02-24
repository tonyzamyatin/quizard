import React from "react";
import CTAButton from "../../global/CTAButton";
import GenerationSteps from "../../global/GenerationSteps";

function CompletionPage({ setGenerationStep } ) {

    const handleBackClick = () => {
        setGenerationStep(GenerationSteps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container progress-container">
            <h2>Your flashcards are ready!</h2>
            <div className="generation-section-box">
                <div className="progress-box">
                    <div className="progress-info-container">
                    </div>
                </div>
            </div>
            <div className="button-area">
                <CTAButton buttonText="Back" buttonType={'secondary'} onButtonClick={handleBackClick} active={true}/>
            </div>
        </div>
    );
}

export default CompletionPage;