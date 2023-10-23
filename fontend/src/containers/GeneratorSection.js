import React, {useState} from "react";
import ConfigContainer from "../components/config_components/ConfigContainer";
import UploadContainer from "../components/text_upload_components/UploadContainer";

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
                return <ConfigContainer/>;
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

export default GeneratorSection;