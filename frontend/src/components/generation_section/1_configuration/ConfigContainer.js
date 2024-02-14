import CTAButton from '../../global/CTAButton';
import ConfigMenu from "./ConfigMenu";
import GenerationSteps from "../../global/GenerationSteps";

function ConfigContainer({setGenerationStep, lang, setLang, mode, setMode, exportFormat, setExportFormat}) {

    function handleNextClick() {
        setGenerationStep(GenerationSteps.TEXT_UPLOAD);
    }

    return (
        <div className="generation-section-container config-container">
            <h2>Configure the Flashcard Generator</h2>
            <div className="generation-section-box">
                <ConfigMenu lang={lang} setLang={setLang} mode={mode} setMode={setMode} exportFormat={exportFormat} setExportFormat={setExportFormat}/>
            </div>
            <div className="button-area">
                {/*TODO: Potentially dangerous condition in 'active={...}'. Susceptible to attack?*/}
                <CTAButton buttonName="Next" onButtonClick={handleNextClick} active={lang.length > 0 && mode.length > 0 && exportFormat.length > 0}/>
            </div>
        </div>
    )
}

export default ConfigContainer;


