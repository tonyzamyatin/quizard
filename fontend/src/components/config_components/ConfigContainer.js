import React, {useState} from "react";
import CTAButton from '../global_components/CTAButton';
import ConfigMenu from "./ConfigMenu";

function ConfigContainer() {

    return (
        <div className="generation-section-container config-container">
            <h2>Configure the Flashcard Generator</h2>
            <div className="generation-section-box">
                <ConfigMenu />
            </div>
            <div className="button-area">
                <CTAButton buttonName="Next"/>
            </div>
        </div>
    )
}

export default ConfigContainer;


