import React, {useEffect} from "react";
import Dropdown from "../../global/Dropdown";

// TODO: Pep up config menu by using icons and make the configuration process more user friendly
function ConfigMenu({ lang, setLang, mode, setMode, exportFormat, setExportFormat}) {
    const languageOptions = ["English", "German"];
    const modeOptions = ["Practice"];
    const exportOptions = ["CSV"]

    const handleLangChange = (event) => {
        setLang(event.target.value);
    };

    const handleModeChange = (event) => {
        setMode(event.target.value);
    };

    const handleExportFormatChange = (event) => {
        setExportFormat(event.target.value);
    }

    useEffect(() => {
        // Load saved value for the field from localStorage when the component mounts
        const savedLang= sessionStorage.getItem('savedLang');
        if (savedLang) {
            setLang(savedLang)
        }
    }, [setLang]);

    useEffect(() => {
        // Save value to localStorage when it changes
        sessionStorage.setItem('savedLang', lang)
    }, [lang]);


    useEffect(() => {
        // Load saved value for the field from localStorage when the component mounts
        const savedMode= sessionStorage.getItem('savedMode');
        if (savedMode) {
            setMode(savedMode)
        }
    }, [setLang]);

    useEffect(() => {
        // Save value to localStorage when it changes
        sessionStorage.setItem('savedMode', mode)
    }, [mode]);

    useEffect(() => {
        // Load saved value for the field from localStorage when the component mounts
        const savedFormat= sessionStorage.getItem('savedFormat');
        if (savedFormat) {
            setExportFormat(savedFormat)
        }
    }, [setLang]);

    useEffect(() => {
        // Save value to localStorage when it changes
        sessionStorage.setItem('savedFormat', exportFormat)
    }, [lang]);

    return (
        <div className="config-menu">
            <Dropdown labelText="Choose your language" selected={lang} options={languageOptions} onChange={handleLangChange}/>
            <Dropdown labelText="Choose generation mode" selected={mode} options={modeOptions} onChange={handleModeChange}/>
            <Dropdown labelText="Choose export format " selected={exportFormat} options={exportOptions} onChange={handleExportFormatChange}/>
        </div>
    );
}

export default ConfigMenu;