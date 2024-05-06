import React  from "react";
import CTAButton from "../../global/CTAButton/CTAButton";
import TextUploadField from "./TextUploadField";
import {GeneratorStep} from "../../../enum/GeneratorStep";
import {useGeneratorState} from "../GeneratorContext";
import {inputTextLengthInRange} from "../../../util/generatorComponentUtil";

function UploadPage() {
    const { setStep, generatorTaskDto, setGeneratorTaskDto} = useGeneratorState();

    const text = generatorTaskDto.inputText;
    const setText = (text: string) => setGeneratorTaskDto({...generatorTaskDto, inputText: text});

    function handleNextClick() {
        setStep(GeneratorStep.Configure);
    }

    function isActive() {
        return inputTextLengthInRange(text);
    }

    const renderInputField = () => {
        return <TextUploadField text={text} setText={setText}/>;
    };

    return (
        <div className="generation-section-container upload-container">
            <h2>Upload your notes</h2>
            <div className="generation-section-box">
                {renderInputField()}
            </div>
            <div className="button-area">
                <CTAButton
                    buttonText="Next"
                    buttonType={'primary'}
                    onButtonClick={handleNextClick}
                    active={isActive()}/>
            </div>
        </div>
    );
}

export default UploadPage;