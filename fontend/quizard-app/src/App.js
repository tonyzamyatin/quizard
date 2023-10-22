// file path: C:\Users\Anton\OneDrive - TU Wien\Dokumente\Coding\Quizard\Proof of Concept\quizard-poc\fontend\quizard-app
import React, {useState} from "react";
import ReactDOM from 'react-dom'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faFileArrowUp} from '@fortawesome/free-solid-svg-icons'
import './Slider.css';
import './CTAButton.css'
import './UploadContainer.css';
import './ConfigContainer.css'
import './GeneratorSection.css'
import './Global.css'

function GeneratorSection() {

    const Steps = Object.freeze({
        TEXT_UPLOAD: 'TextUpload',
        CONFIGURATION: 'Configuration',
        GENERATION: 'Generation'
    });

    const [currentStep, setCurrentStep] = useState(Steps.TEXT_UPLOAD)

    const renderContent = () => {
        switch (currentStep) {
            case Steps.CONFIGURATION:
                return  <ConfigContainer />;
            case Steps.TEXT_UPLOAD:
                return <UploadContainer/>;
            case Steps.GENERATION:
                return <></>
        }
    }

    return (
        <div className="generator-section">
            <div className="description">
                <h1>Quizard Flashcard Generator</h1>
                {/*TODO: Add our own paragraph*/}
                <p>Our Flashcard Generator automatically transforms your notes or textbooks into flashcards using
                    the
                    power of artificial intelligence. Simply upload your materials and let our AI create your
                    flashcards
                    in seconds.</p>
            </div>
            {renderContent()}
        </div>
    );
}

function CTAButton({buttonName}) {
    return <button className={`CTA-button ${buttonName.replace(' ', '-').toLowerCase()}`}>{buttonName}</button>;
}

function ConfigContainer() {

    return (
        <div className="generation-section-container config-container">
            <h2>Configure the Flashcard Generator</h2>
            <div className="generation-section-box">
                <ConfigMenu />
            </div>
            <div className="button-area">
                <CTAButton buttonName="Next"/>
            </div>
        </div>
    )
}

function ConfigMenu() {

    const languageOptions = ["English", "German"];
    const modeOptions = ["Practice", "Test", "Cloze"];

    return (
        <div className="config-menu">
            <Dropdown labelText="Choose your language" options={languageOptions} />
            <Dropdown labelText="Choose your generation mode" options={modeOptions} />
        </div>
    )
}

function Dropdown({ labelText, options }){

    const [selectedOption, setSelectedOption] = useState("");

    const handleChange = (event) => {
        setSelectedOption(event.target.value);
    }

    return (
        <div>
            <label>{labelText}</label>
            <select value={selectedOption} onChange={handleChange} defaultValue="">
                <option value="" disabled>Select...</option>
                {options.map((optionText, index) => (
                    <option key={index} value={optionText}>
                        {optionText}
                    </option>
                ))}
            </select>
        </div>
    );
}

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

function Slider({ fields, selectedField, onFieldClick }) {
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

function TextUploadField() {
    return (
        <div className="text-upload-field">
            <p>Copy and paste your notes here (between 250 and 10,000 characters)</p>
        </div>
    );
}

function PDFUploadField({}) {
    return (
        <div className="PDF-upload-field">
            <div className="PDF-placeholder">
                <p>Document uploading coming soon...</p>
                <FontAwesomeIcon icon={faFileArrowUp} className="PDF-upload-icon"/>
            </div>
        </div>
    );
}


const App = () => {
    return <GeneratorSection/>;
};

export default App;

