import React, {useEffect} from "react";
import Dropdown from "../../global/Dropdown";
import {FileFormat, Mode, Language} from "../../../enum/GeneratorOptions";
import {useGeneratorState} from "../GeneratorContext";

// TODO: Pep up config menu by using icons and make the ConigurationComponent process more user friendly
function ConfigMenu() {

    const { generatorTaskDto, setGeneratorTaskDto, fileFormat, setFileFormat} = useGeneratorState();
    const setLang = (lang: Language | null) => setGeneratorTaskDto({...generatorTaskDto, lang});
    const setMode = (mode: Mode | null) => setGeneratorTaskDto({...generatorTaskDto, mode});

    // Map enum keys to human-readable values
    const langOptions = Object.entries(Language).map(([key, value]) => ({key, value}));
    const modeOptions = Object.entries(Mode).map(([key, value]) => ({key, value}));
    const fileFormatOptions = Object.entries(FileFormat).map(([key, value]) => ({key, value}));

    // @ts-ignore
    const handleOptionChange = (options, setter) => (event) => {
        // @ts-ignore
        const selectedKey = options.find(option => option.value === event.target.value).key;
        setter(selectedKey);
    }

    const handleLangChange = handleOptionChange(langOptions, setLang);
    const handleModeChange = handleOptionChange(modeOptions, setMode);
    const handleExportFormatChange = handleOptionChange(fileFormatOptions, setFileFormat);



    return (
        <form className="config-menu">
            <Dropdown
                labelText="Select language"
                id={"lang-config-dropdown"}
                selected={generatorTaskDto.lang}
                options={langOptions.map(option => option.value)}
                onChange={handleLangChange}/>
            <Dropdown
                labelText="Select flashcard type"
                id={"mode-config-dropdown"}
                selected={generatorTaskDto.mode}
                options={modeOptions.map(option => option.value)}
                onChange={handleModeChange}/>
            <Dropdown
                labelText="Select file format "
                id={"file-format-config-dropdown"}
                selected={fileFormat}
                options={fileFormatOptions.map(option => option.value)}
                onChange={handleExportFormatChange}/>
        </form>
    );
}

export default ConfigMenu;