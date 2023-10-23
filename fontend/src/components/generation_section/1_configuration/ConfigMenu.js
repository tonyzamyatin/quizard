import React from "react";
import Dropdown from "../../global/Dropdown";

function ConfigMenu() {

    const languageOptions = ["English", "German"];
    const modeOptions = ["Practice", "Test", "Cloze"];

    return (
        <div className="config-menu">
            <Dropdown labelText="Choose your language" options={languageOptions} />
            <Dropdown labelText="Choose your generation mode" options={modeOptions} />
        </div>
    )
}

export default ConfigMenu;