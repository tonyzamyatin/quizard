import CTAButton from '../../global/CTAButton/CTAButton';
import ConfigMenu from "./ConfigMenu";
import React from "react";
import {useGeneratorState} from "../GeneratorContext";
import {GeneratorStep} from "../../../enum/GeneratorStep";

interface ConfigPageProps {
    generateFlashcards: () => void;
}

function ConfigPage({generateFlashcards} : ConfigPageProps) {

    const {setStep, generatorTaskDto, fileFormat} = useGeneratorState();
    const {lang, mode} = generatorTaskDto;

    const handleGenerateClick  = () => {
        // start generation of flashcards
        generateFlashcards();
        setStep(GeneratorStep.Wait)
    }

    function handleBackClick() {
        setStep(GeneratorStep.UploadText);
    }

    function isButtonActive() {
        return lang.length > 0 && mode.length > 0 && fileFormat.length > 0;
    }

    return (
        <div className="generation-section-container config-container">
            <h2>Configure your flashcards</h2>
            <div className="generation-section-box">
                <ConfigMenu />
            </div>
            <div className="button-area">
                {/*TODO: Potentially dangerous condition in 'active={...}'. Susceptible to attack?*/}
                <CTAButton
                    buttonText="Back" buttonType={'secondary'}
                    onButtonClick={handleBackClick}
                    active={true} nonHover={true}/>
                <CTAButton
                    buttonText="Generate" buttonType={'primary'}
                    onButtonClick={handleGenerateClick}
                    active={lang.length > 0 && mode.length > 0 && fileFormat.length > 0}/>
            </div>
        </div>
    )
}

export default ConfigPage;


