import React  from "react";
import CTAButton from "../../global/CTAButton/CTAButton";
import TextUploadField from "./TextUploadField";
import {GeneratorStep} from "../../../enum/GeneratorStep";
import {useGeneratorState} from "../GeneratorContext";

function UploadPage() {
    const { setStep, generatorTaskDto, setGeneratorTaskDto} = useGeneratorState();

    const text = generatorTaskDto.inputText;
    const setText = (text: string) => setGeneratorTaskDto({...generatorTaskDto, inputText: text});

    const minLength = 250
    const maxLength = 500000;

    function checkTextLength() {
        // Checks if the text is long enough to proceed
        return text.length > minLength && text.length <= maxLength;
    }

    function handleNextClick() {
        setStep(GeneratorStep.Configure);
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
                <CTAButton buttonText="Next" buttonType={'primary'} onButtonClick={handleNextClick} active={checkTextLength()}/>
            </div>
        </div>
    );
}

export default UploadPage;