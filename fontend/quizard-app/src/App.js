import React, {useState} from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import './Slider.css';
import './CTAButton.css'
import './UploadContainer.css';
import './Global.css'

function SliderField({ fieldName, isSelected, onClick }) {
    return (
        <div
            className={`slider-field ${isSelected ? "selected" : ""}`}
            onClick={() => onClick(fieldName)}
        >
            <span>{fieldName}</span>
        </div>
    );
}


function Slider({ fields, selectedField, onFieldClick}) {
    const fieldWidth = 200 / fields.length; // Assuming total width is 900px

    return (
        <div className="slider-container">
            <div className="slider-track">
                {fields.map((field) => (
                    <SliderField
                        fieldName={field}
                        isSelected={field === selectedField}
                        onClick={onFieldClick}
                        key={field}
                    />
                ))}
            </div>
            <div
                className="slider-knob-container"
                style={{
                    width: `${fieldWidth}px`,
                    left: `${fields.indexOf(selectedField) * fieldWidth}px`
                }}
            >
                <div className="slider-knob"></div>
            </div>
        </div>
    );
}


function TextUploadField () {
    return (
        <div className="text-upload-field">
            <p>Copy and paste your notes here (between 250 and 10,000 characters)</p>
        </div>
    );
}

function PDFUploadField ({ }) {
    return (
        <div className="PDF-upload-field">
            <div className="PDF-placeholder">
                <p>Document uploading coming soon...</p>
                <FontAwesomeIcon icon="fa-solid fa-file-arrow-up" style={{color: "#6a6870",}} />
            </div>
        </div>
    );
}

function CTAButton({ buttonName }) {
    return <button className={`CTA-button ${buttonName.replace(' ', '-').toLowerCase()}`}>{buttonName}</button>;
}

function UploadContainer() {
    const [selectedField, setSelectedField] = useState("Text");

    function handleFieldClick (field) {
        setSelectedField(field);
    }

    const renderInputField = () => {
        if (selectedField === "Text") {
            return <TextUploadField />;
        } else if (selectedField === "PDF") {
            return <PDFUploadField />;
        }
    };

    return (
        <div className="upload-container">
            <h2>Enter your Notes</h2>
            <Slider fields={["Text", "PDF"]} selectedField={selectedField} onFieldClick={handleFieldClick}/>
            <div className="input-area">
                {renderInputField()}
            </div>
            <div className="button-area">
                <CTAButton buttonName="Go back" />
                <CTAButton buttonName="Generate" />
            </div>
        </div>
    );
}

const App = () => {
    return <UploadContainer />;
};

export default App;

