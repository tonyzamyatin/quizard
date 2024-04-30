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
import Generator from "./generator/Generator";
import Footer from "./global/Footer";

const App = () => {

    return (
        <div>
            <Generator />
            <Footer />
        </div>
    );
}

export default App;
