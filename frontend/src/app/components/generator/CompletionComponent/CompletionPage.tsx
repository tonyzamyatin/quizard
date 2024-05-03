import React from "react";
import CTAButton from "../../global/CTAButton/CTAButton";
import {useExternalScript} from "../../../../hooks/useExternalScript";
import {useGeneratorState} from "../GeneratorContext";
import {createDefaultGeneratorTask, createDefaultGeneratorTaskInfo} from "../../../util/dtoUtil";
import {GeneratorStep} from "../../../enum/GeneratorStep";


function CompletionPage() {
    // TODO: Fix bug: Share buttons not loading on component mount (only on reload)
    // TODO: Fix bug: Form has black background (maybe create custom form).

    const {setStep, setGeneratorTaskDto, setGeneratorTaskInfo, setFileFormat} = useGeneratorState();

    const shareThisScript = "https://platform-api.sharethis.com/js/sharethis.js#property=65dc401e98ac00001970d5d9&product=inline-share-buttons";
    const state = useExternalScript(shareThisScript);


    const handleBackClick = () => {
        setGeneratorTaskDto(createDefaultGeneratorTask());
        setGeneratorTaskInfo(createDefaultGeneratorTaskInfo());
        setFileFormat(null);
        localStorage.removeItem('savedGeneratorTaskDto');
        sessionStorage.removeItem('savedGeneratorTaskDto');
        localStorage.removeItem('savedFileFormat');
        sessionStorage.removeItem('savedFileFormat');
        setStep(GeneratorStep.UploadText);
    }

    return (
    <div className="generation-section-container">
        <h2>Your flashcards are ready!</h2>
        <div className={"completion-content"}>
            <p>Found Quizard useful? Spread the magic!</p>
            {state === "loading" /*&& <p style={{margin: '10px 0 10px 0'}}>Loading</p>*/}
            {state === "ready" && <div className="sharethis-inline-share-buttons"></div>}
            <CTAButton buttonText="Back" buttonType={'secondary'} onButtonClick={handleBackClick}
                       active={true}/>
        </div>
        {/*<div */}
        {/*    class="powr-form-builder" */}
        {/*    id="sharethis-form-builder-65dc401e98ac00001970d5d9">*/}
        {/*</div>*/}
    </div>
    );
}

export default CompletionPage;