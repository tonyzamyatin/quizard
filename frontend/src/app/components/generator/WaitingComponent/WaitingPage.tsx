import React from "react";
import ProgressBar from "./ProgressBar";
import  {GeneratorStep} from "../../../enum/GeneratorStep";
import {useGeneratorState} from "../GeneratorContext";
import CTAButton from "../../global/CTAButton/CTAButton";

function WaitingPage() {

    const { setStep, generatorTaskInfo, cancelFlashcards } = useGeneratorState();
    let { currentBatch, totalBatches } = generatorTaskInfo;
    currentBatch = currentBatch || 0;
    totalBatches = totalBatches || 1;

    // Progress of flashcard generation process in percent
    const progress = currentBatch / totalBatches * 100


    const renderProgressBar = () => {
        return <ProgressBar progress={progress}/>;
    }

    const handleCancelClick = () => {
        cancelFlashcards();
        setStep(GeneratorStep.UPLOAD_TEXT);
    }


    return (
        <div className="generation-section-container">
            <h2>Generating</h2>
            <div className="progress-box">
                <div className="progress-info-container">
                </div>

                <div className="progress-bar-container">
                    {renderProgressBar()}
                    <div className="button-area">
                        <CTAButton
                            buttonText="Cancel"
                            buttonType={'warn'}
                            onButtonClick={handleCancelClick}
                            active={true}
                            nonHover={true}
                        />
                    </div>
                </div>
            </div>
            {/*<div className={"ad-container"}>*/}
            {/*    <div className={"ad-box"}>*/}
            {/*        <script async*/}
            {/*                src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6997800913244414"*/}
            {/*                crossOrigin="anonymous"></script>*/}
            {/*    </div>*/}
            {/*</div>*/}
        </div>
    );
}

export default WaitingPage;