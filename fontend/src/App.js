import React, {useState} from "react";
import ReactDOM from 'react-dom'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faFileArrowUp} from '@fortawesome/free-solid-svg-icons'
import ConfigContainer from './components/config_components/ConfigContainer';
import './styles/Slider.css';
import './styles/CTAButton.css'
import './styles/UploadContainer.css';
import './styles/ConfigContainer.css'
import './styles/GeneratorSection.css'
import './styles/Global.css'
import GeneratorSection from "./containers/GeneratorSection";

const App = () => {
    return <GeneratorSection/>;
};

export default App;

