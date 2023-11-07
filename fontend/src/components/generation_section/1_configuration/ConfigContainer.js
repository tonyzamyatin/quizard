import CTAButton from '../../global/CTAButton';
import ConfigMenu from "./ConfigMenu";
import GenerationSteps from "../../global/GenerationSteps";

function ConfigContainer({setGenerationStep, lang, setLang, mode, setMode}) {

    function handleNextClick() {
        setGenerationStep(GenerationSteps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container config-container">
            <h2>Configure the Flashcard Generator</h2>
            <div className="generation-section-box">
                <ConfigMenu lang={lang} setLang={setLang} mode={mode} setMode={setMode}/>
            </div>
            <div className="button-area">
                <CTAButton buttonName="Next" onButtonClick={handleNextClick} active={lang.length > 0 && mode.length > 0}/>
            </div>
        </div>
    )
}

export default ConfigContainer;


