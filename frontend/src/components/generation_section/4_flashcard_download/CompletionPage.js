import React from "react";
import CTAButton from "../../global/CTAButton";
import GenerationSteps from "../../global/GenerationSteps";

function CompletionPage({ setGenerationStep, setText } ) {

    const handleBackClick = () => {
        setText('');
        localStorage.removeItem('lastText');
        sessionStorage.removeItem('lastText');
        setGenerationStep(GenerationSteps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container">
            <h2>Your flashcards are ready!</h2>
            <div className={""}>
                <p>Found Quizard useful? Spread the magic!</p>
                <div className="button-area">
                    <CTAButton buttonText="Back" buttonType={'secondary'} onButtonClick={handleBackClick}
                               active={true}/>
                    <CTAButton buttonText="Share" buttonType={'primary'} onButtonClick={() => ({})}
                               active={true}/>
                </div>

            </div>
        </div>
    );
}

export default CompletionPage;