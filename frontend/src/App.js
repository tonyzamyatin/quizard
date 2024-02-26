import GeneratorSection from "./components/generation_section/GeneratorSection";
import { HealthCheckProvider } from './components/generation_section/HealthCheckContext';
// Import general styles first
import './styles/Global.css'
import './styles/Generator.css'
import './styles/Slider.css';
import './styles/CTAButton.css'
// Import specific styles later
import './styles/GeneratorUploadPage.css';
import './styles/GeneratorConfigPage.css'
import './styles/GeneratorWaitingPage.css'
import './styles/GeneratorCompletionPage.css'
import './styles/ProgressBar.css'
import Footer from "./components/global/Footer";

const App = () => {

    return (
        <HealthCheckProvider>
            <GeneratorSection />
            <Footer />
        </HealthCheckProvider>
    );
}

export default App;
