import CTAButton from '../../global/CTAButton';
import ConfigMenu from "./ConfigMenu";
import GenerationSteps from "../../global/GenerationSteps";
import React from "react";

function ConfigPage({setGenerationStep, lang, setLang, mode, setMode, exportFormat, setExportFormat, generateFlashcards}) {

    const handleGenerateClick  = () => {
        // start generation of flashcards
        generateFlashcards();
        setGenerationStep(GenerationSteps.GENERATION);
    }

    function handleBackClick() {
        setGenerationStep(GenerationSteps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container config-container">
            <h2>Configure your flashcards</h2>
            <div className="generation-section-box">
                <ConfigMenu lang={lang} setLang={setLang} mode={mode} setMode={setMode} exportFormat={exportFormat} setExportFormat={setExportFormat}/>
            </div>
            <div className="button-area">
                {/*TODO: Potentially dangerous condition in 'active={...}'. Susceptible to attack?*/}
                <CTAButton buttonText="Back" buttonType={'secondary'} onButtonClick={handleBackClick} active={true} lazy={true}/>
                <CTAButton buttonText="Generate" buttonType={'primary'} onButtonClick={handleGenerateClick} active={lang.length > 0 && mode.length > 0 && exportFormat.length > 0}/>
            </div>
        </div>
    )
}

export default ConfigPage;


