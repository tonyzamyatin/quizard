import React from "react";
import ConfigPage from "./ConfigurationComponent/ConfigPage";
import UploadPage from "./TextUploadComponent/UploadPage";
import WaitingPage from "./WaitingComponent/WaitingPage";
import CompletionPage from "./CompletionComponent/CompletionPage";
import {GeneratorStep} from "../../enum/GeneratorStep";
import {useGeneratorState} from "./GeneratorContext";

function Generator() {
    const { step} = useGeneratorState();

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
        renderContent()
    );
}

export default Generator;