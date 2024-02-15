import GeneratorSection from "./containers/GeneratorSection";
import { HealthCheckProvider } from './containers/HealthCheckContext';
// Import general styles first
import './styles/Global.css'
import './styles/GeneratorSection.css'
import './styles/Slider.css';
import './styles/CTAButton.css'
// Import specific styles later
import './styles/UploadContainer.css';
import './styles/ConfigContainer.css'
import './styles/GenerationProgressContainer.css'
import './styles/ProgressBar.css'

// TODO: Get the display language of the browser and display the content in that language (for starters, either "German" or "English").
// function getBrowserLanguage() {
//
// }
const App = () => {

    return (
        <HealthCheckProvider>
            <div className="app">
                <GeneratorSection />
            </div>
        </HealthCheckProvider>
    );
}

export default App;
