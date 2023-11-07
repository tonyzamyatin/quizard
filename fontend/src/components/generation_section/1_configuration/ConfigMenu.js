import React, {useEffect} from "react";
import Dropdown from "../../global/Dropdown";

function ConfigMenu({ lang, setLang, mode, setMode }) {
    const languageOptions = ["English", "German"];
    const modeOptions = ["Practice", "Test", "Cloze"];

    const handleModeChange = (event) => {
        setMode(event.target.value);
    };

    const handleLangChange = (event) => {
        setLang(event.target.value);
    };

    return (
        <div className="config-menu">
            <Dropdown labelText="Choose your language" selected={lang} options={languageOptions} onChange={handleLangChange}/>
            <Dropdown labelText="Choose your generation mode" selected={mode} options={modeOptions} onChange={handleModeChange}/>
        </div>
    );
}


export default ConfigMenu;