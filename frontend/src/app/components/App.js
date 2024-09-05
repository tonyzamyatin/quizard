// Import general styles first
import './global/global.css'
import './generator/Generator.css'
import './global/Slider/Slider.css';
import './global/CTAButton/CTAButton.css'
// Import specific styles later
import './generator/TextUploadComponent/GeneratorUploadPage.css';
import './generator/ConigurationComponent/GeneratorConfigPage.css'
import './generator/WaitingComponent/GeneratorWaitingPage.css'
import './generator/CompletionComponent/GeneratorCompletionPage.css'
import './generator/WaitingComponent/ProgressBar.css'
import Generator from "./generator/Generator";
import Footer from "./global/Footer";
import React from "react";
import {GeneratorStateProvider} from "./generator/GeneratorContext";

const App = () => {

    return (
        <>
            <main>
                <div className="description">
                    <h1>✨Quizard AI Flashcards✨</h1>
                    <p>Quizard automatically transforms your notes or textbooks into flashcards using AI.</p>
                    <p>Simply upload your text and lean back!</p>
                </div>
                <GeneratorStateProvider>
                    <Generator/>
                </GeneratorStateProvider>
            </main>
            <Footer/>
        </>
    );
}

export default App;
