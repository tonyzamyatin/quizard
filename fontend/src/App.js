import React, {useState} from "react";
import ReactDOM from 'react-dom'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faFileArrowUp} from '@fortawesome/free-solid-svg-icons'
import ConfigContainer from './components/generation_section/1_configuration/ConfigContainer';
import './styles/Slider.css';
import './styles/CTAButton.css'
import './styles/UploadContainer.css';
import './styles/ConfigContainer.css'
import './styles/GeneratorSection.css'
import './styles/Global.css'
import GeneratorSection from "./containers/GeneratorSection";

// Get the display language of the browser and display the content in that language (for starters, either "German" or "English").
function getBrowserLanguage() {

}
const App = () => {
    return <GeneratorSection/>;
};

export default App;

