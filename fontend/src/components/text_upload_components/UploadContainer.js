import React, {useState} from "react";
import CTAButton from "../global_components/CTAButton";
import TextUploadField from "./TextUploadField";
import PDFUploadField from "./PDFUploadField";
import Slider from "../global_components/Slider";

function UploadContainer() {
    const [selectedField, setSelectedField] = useState("Text");

    function handleFieldClick(field) {
        setSelectedField(field);
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
                <CTAButton buttonName="Go back"/>
                <CTAButton buttonName="Generate"/>
            </div>
        </div>
    );
}

export default UploadContainer;