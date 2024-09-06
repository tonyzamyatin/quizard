import React from "react";
import Dropdown from "../../global/Dropdown";


import {useGeneratorState} from "../GeneratorContext";
import {displayNameFromEnumValue, enumValueFromDisplayName} from "../../../util/generatorOptionsUtil";
import {
    DisplayNameMap,
    FileFormat, FileFormatDisplayNames,
    Language,
    LanguageDisplayNames,
    Mode, ModeDisplayNames,
    OptionEnumType
} from "../../../enum/GeneratorOptions";

// TODO: Pep up config menu by using icons and make the ConfigurationComponent process more user friendly
function ConfigMenu() {

    const { generatorTaskDto, setGeneratorTaskDto} = useGeneratorState();
    const setLang = (lang: Language | null) => setGeneratorTaskDto({...generatorTaskDto, lang});
    const setMode = (mode: Mode | null) => setGeneratorTaskDto({...generatorTaskDto, mode});
    const setExportFormat = (exportFormat: FileFormat | null) => setGeneratorTaskDto({...generatorTaskDto, exportFormat});


    /**
     * Generic handler for changes in the option dropdowns.
     * Maps the selected display name to the corresponding enum value and sets the state.
     * @param enumObj the enum object to get the value from
     * @param displayNameMap the display names map for the corresponding enum
     * @param setter the state setter function
     */
    const handleOptionChange = (
        enumObj: OptionEnumType,
        displayNameMap: DisplayNameMap,
        setter: (value: OptionEnumType[keyof OptionEnumType] | null) => void
    ) => (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedDisplayName = event.target.value;
        const selectedEnumValue = enumValueFromDisplayName(enumObj, displayNameMap, selectedDisplayName);
        setter(selectedEnumValue);
    };


    // Specific handler for changes in the language dropdown.
    const handleLangChange = handleOptionChange(Language, LanguageDisplayNames, setLang);
    const handleModeChange = handleOptionChange(Mode, ModeDisplayNames, setMode);
    const handleExportFormatChange = handleOptionChange(FileFormat, FileFormatDisplayNames, setExportFormat);



    return (
        <form className="config-menu">
            <Dropdown
                labelText="Select language"
                id={"lang-config-dropdown"}
                selected={displayNameFromEnumValue(LanguageDisplayNames, generatorTaskDto.lang) || ''}
                options={Object.values(LanguageDisplayNames)}
                onChange={handleLangChange}/>
            <Dropdown
                labelText="Select flashcard type"
                id={"mode-config-dropdown"}
                selected={displayNameFromEnumValue(ModeDisplayNames, generatorTaskDto.mode) || ''}
                options={Object.values(ModeDisplayNames)}
                onChange={handleModeChange}/>
            <Dropdown
                labelText="Select file format "
                id={"file-format-config-dropdown"}
                selected={displayNameFromEnumValue(FileFormatDisplayNames, generatorTaskDto.exportFormat) || ''}
                options={Object.values(FileFormatDisplayNames)}
                onChange={handleExportFormatChange}/>
        </form>
    );
}

export default ConfigMenu;