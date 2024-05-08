import CTAButton from '../../global/CTAButton/CTAButton';
import ConfigMenu from "./ConfigMenu";
import React from "react";
import {useGeneratorState} from "../GeneratorContext";
import {GeneratorStep} from "../../../enum/GeneratorStep";
import {inputTextLengthInRange} from "../../../util/generatorComponentUtil";

function ConfigPage() {

    const {setStep, generatorTaskDto, fileFormat, generateFlashcards} = useGeneratorState();
    const {lang, mode, inputText} = generatorTaskDto;

    const handleGenerateClick  = () => {
        // start generation of flashcards
        generateFlashcards();
        setStep(GeneratorStep.WAIT)
    }

    function handleBackClick() {
        setStep(GeneratorStep.UPLOAD_TEXT);
    }

    function isDtoComplete() {
        return !! (lang && mode && fileFormat && inputTextLengthInRange(inputText));
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
                    active={isDtoComplete()}/>
            </div>
        </div>
    )
}

export default ConfigPage;


