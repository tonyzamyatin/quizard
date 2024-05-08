import React from "react";
import ConfigPage from "./ConigurationComponent/ConfigPage";
import UploadPage from "./TextUploadComponent/UploadPage";
import WaitingPage from "./WaitingComponent/WaitingPage";
import CompletionPage from "./CompletionComponent/CompletionPage";
import {GeneratorStep} from "../../enum/GeneratorStep";
import {GeneratorStateProvider} from "./GeneratorContext";
import {useFlashcardGenerator} from "../../hooks/useFlashcardGenerator";

function Generator() {
    const {
        step,
    } = useFlashcardGenerator();

    const renderContent = () => {
        switch (step) {
            case GeneratorStep.UPLOAD_TEXT:
                return <UploadPage />;
            case GeneratorStep.CONFIGURE:
                return <ConfigPage />;
            case GeneratorStep.WAIT:
                return <WaitingPage />;
            case GeneratorStep.COMPLETE:
                return <CompletionPage  />;
            default:
                return <UploadPage />;
        }
    }
    return (
        <GeneratorStateProvider>
            {renderContent()}
        </GeneratorStateProvider>
    );
}

export default Generator;