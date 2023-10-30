import React, {useState} from "react";
import ConfigContainer from "../components/generation_section/1_configuration/ConfigContainer";
import UploadContainer from "../components/generation_section/2_text_upload/UploadContainer";
import GenerationProgressContainer from "../components/generation_section/3_flashcard_generation/GenerationProgressContainer";
import GenerationSteps from "../components/global/GenerationSteps";

function GeneratorSection() {

    const [currentStep, setCurrentStep] = useState(GenerationSteps.CONFIGURATION)
    const renderContent = () => {
        switch (currentStep) {
            case GenerationSteps.CONFIGURATION:
                return <ConfigContainer setGenerationStep={setCurrentStep}/>;
            case GenerationSteps.TEXT_UPLOAD:
                return <UploadContainer setGenerationStep={setCurrentStep}/>;
            case GenerationSteps.GENERATION:
                return <GenerationProgressContainer/>
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