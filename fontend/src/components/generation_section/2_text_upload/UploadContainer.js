import React, {useState} from "react";
import CTAButton from "../../global/CTAButton";
import TextUploadField from "./TextUploadField";
import PDFUploadField from "./PDFUploadField";
import GenerationSteps from "../../global/GenerationSteps";

function UploadContainer({setGenerationStep}) {
    const [selectedField, setSelectedField] = useState("Text");

    const handleFieldClick = (field) => {
        setSelectedField(field);
    }

    const handleBackClick = () => {
        setGenerationStep(GenerationSteps.CONFIGURATION);
    }

    const handleGenerateClick  = () => {
        setGenerationStep(GenerationSteps.GENERATION);
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
            {/* TODO: Uncomment Slider when PDF reader is ready for deployment.*/}
            {/*<Slider fields={["Text", "PDF"]} selectedField={selectedField} onFieldClick={handleFieldClick}/>*/}
            <div className="generation-section-box">
                {renderInputField()}
            </div>
            <div className="button-area">
                <CTAButton buttonName="Go back" onButtonClick={handleBackClick}/>
                <CTAButton buttonName="Generate" onButtonClick={handleGenerateClick}/>
            </div>
        </div>
    );
}

export default UploadContainer;