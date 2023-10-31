import CTAButton from '../../global/CTAButton';
import ConfigMenu from "./ConfigMenu";
import GenerationSteps from "../../global/GenerationSteps";

function ConfigContainer({setGenerationStep}) {

    function handleNextClick() {
        setGenerationStep(GenerationSteps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container config-container">
            <h2>Configure the Flashcard Generator</h2>
            <div className="generation-section-box">
                <ConfigMenu />
            </div>
            <div className="button-area">
                <CTAButton buttonName="Next" onButtonClick={handleNextClick}/>
            </div>
        </div>
    )
}

export default ConfigContainer;


