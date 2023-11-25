import React   from "react";
import Dropdown from "../../global/Dropdown";

// TODO: Pep up config menu by using icons and make the configuration process more user friendly
function ConfigMenu({ lang, setLang, mode, setMode, exportFormat, setExportFormat}) {
    const languageOptions = ["English", "German"];
    const modeOptions = ["Practice", "Test", "Cloze"];
    const exportOptions = ["CSV", "Anki"]

    const handleLangChange = (event) => {
        setLang(event.target.value);
    };

    const handleModeChange = (event) => {
        setMode(event.target.value);
    };

    const handleExportFormatChange = (event) => {
        setExportFormat(event.target.value);
    }

    return (
        <div className="config-menu">
            <Dropdown labelText="Choose your language" selected={lang} options={languageOptions} onChange={handleLangChange}/>
            <Dropdown labelText="Choose generation mode" selected={mode} options={modeOptions} onChange={handleModeChange}/>
            <Dropdown labelText="Choose export format " selected={exportFormat} options={exportOptions} onChange={handleExportFormatChange}/>
        </div>
    );
}

export default ConfigMenu;