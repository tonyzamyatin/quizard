// Import general styles first
import '../styles/Global.css'
import '../styles/Generator.css'
import '../styles/Slider.css';
import '../styles/CTAButton.css'
// Import specific styles later
import '../styles/GeneratorUploadPage.css';
import '../styles/GeneratorConfigPage.css'
import '../styles/GeneratorWaitingPage.css'
import '../styles/GeneratorCompletionPage.css'
import '../styles/ProgressBar.css'
import GeneratorSection from "./generation_section/GeneratorSection";
import Footer from "./global/Footer";

const App = () => {

    return (
        <div>
            <GeneratorSection />
            <Footer />
        </div>
    );
}

export default App;
