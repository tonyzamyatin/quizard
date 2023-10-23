import React, {useState} from "react";
import CTAButton from "../../global/CTAButton";
import TextUploadField from "./TextUploadField";
import PDFUploadField from "./PDFUploadField";
import Slider from "../../global/Slider";
import Steps from "../../global/GenerationSteps";

function UploadContainer({setGenerationStep}) {
    const [selectedField, setSelectedField] = useState("Text");

    function handleFieldClick(field) {
        setSelectedField(field);
    }

    function handleBackClick() {
        setGenerationStep(Steps.CONFIGURATION);
    }

    function handleGenerateClick() {
        setGenerationStep(Steps.GENERATION);
    }

    const renderInputField = () => {
        if (selectedField === "Text") {
            return <TextUploadField/>;
        } else if (selectedField === "PDF") {
            return <PDFUploadField/>;
        }
    };

    return (
        <div className="generation-section-container upload-container">
            <h2>Enter your Notes</h2>
            <Slider fields={["Text", "PDF"]} selectedField={selectedField} onFieldClick={handleFieldClick}/>
            <div className="generation-section-box">
                {renderInputField()}
            </div>
            <div className="button-area">
                <CTAButton buttonName="Go back" handleClick={handleBackClick()}/>
                <CTAButton buttonName="Generate" handleClick={handleGenerateClick()}/>
            </div>
        </div>
    );
}

export default UploadContainer;