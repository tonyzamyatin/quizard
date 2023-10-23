import React, {useState} from "react";
import CTAButton from '../../global/CTAButton';
import ConfigMenu from "./ConfigMenu";
import Steps from "../../global/GenerationSteps";

function ConfigContainer({setGenerationStep}) {

    function handleNextClick() {
        setGenerationStep(Steps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container config-container">
            <h2>Configure the Flashcard Generator</h2>
            <div className="generation-section-box">
                <ConfigMenu />
            </div>
            <div className="button-area">
                <CTAButton buttonName="Next" onClick={handleNextClick()}/>
            </div>
        </div>
    )
}

export default ConfigContainer;


