import React, {useState} from "react";
import CTAButton from "../../global/CTAButton";
import TextUploadField from "./TextUploadField";
import PDFUploadField from "./PDFUploadField";
import GenerationSteps from "../../global/GenerationSteps";

function UploadContainer({setGenerationStep, text, setText, generateFlashcards}) {
    const [selectedField, setSelectedField] = useState("Text");

    const handleFieldClick = (field) => {
        setSelectedField(field);
    }

    const handleBackClick = () => {
        setGenerationStep(GenerationSteps.CONFIGURATION);
    }

    const handleGenerateClick  = () => {
        // start generation of flashcards
        generateFlashcards();
        setGenerationStep(GenerationSteps.GENERATION);
    }

    const renderInputField = () => {
        if (selectedField === "Text") {
            return <TextUploadField text={text} setText={setText}/>;
        } else if (selectedField === "PDF") {
            return <PDFUploadField/>;
        }
    };

    return (
        <div className="generation-section-container upload-container">
            <h2>Enter your Notes</h2>
            {/* TODO: Uncomment Slider when PDF reader is ready for deployment.*/}
            {/*<Slider fields={["Text", "PDF"]} selectedField={selectedField} onFieldClick={handleFieldClick}/>*/}
            <div className="generation-section-box">
                {renderInputField()}
            </div>
            <div className="button-area">
                <CTAButton buttonName="Go back" onButtonClick={handleBackClick} active={true}/>
                <CTAButton buttonName="Generate" onButtonClick={handleGenerateClick} active={text.length > 250 && text.length <= 500000}/>
            </div>
        </div>
    );
}

export default UploadContainer;