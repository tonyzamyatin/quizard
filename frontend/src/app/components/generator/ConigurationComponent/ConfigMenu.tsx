import React, {useEffect} from "react";
import Dropdown from "../../global/Dropdown";
import {
    FileFormat,
    Mode,
    Language,
    LanguageDisplayNames,
    ModeDisplayNames,
    FileFormatDisplayNames,
    OptionEnum,
    DisplayNameMap,
} from "../../../enum/generatorOptions";
import {useGeneratorState} from "../GeneratorContext";
import {displayNameFromEnumValue, enumValueFromDisplayName} from "../../../util/generatorOptionsUtil";

// TODO: Pep up config menu by using icons and make the ConfigurationComponent process more user friendly
function ConfigMenu() {

    const { generatorTaskDto, setGeneratorTaskDto, fileFormat, setFileFormat} = useGeneratorState();
    const setLang = (lang: Language | null) => setGeneratorTaskDto({...generatorTaskDto, lang});
    const setMode = (mode: Mode | null) => setGeneratorTaskDto({...generatorTaskDto, mode});


    /**
     * Generic handler for changes in the option dropdowns.
     * Maps the selected display name to the corresponding enum value and sets the state.
     * @param enumObj the enum object to get the value from
     * @param displayNameMap the display names map for the corresponding enum
     * @param setter the state setter function
     */
    const handleOptionChange = <T extends OptionEnum>(
        enumObj: T,
        displayNameMap: DisplayNameMap,
        setter: (value: T[keyof T] | null) => void
    ) => (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedDisplayName = event.target.value;
        const selectedEnumValue = enumValueFromDisplayName(enumObj, displayNameMap, selectedDisplayName);
        setter(selectedEnumValue);
    };


    // Specific handler for changes in the language dropdown.
    const handleLangChange = handleOptionChange(Language, LanguageDisplayNames, setLang);
    const handleModeChange = handleOptionChange(Mode, ModeDisplayNames, setMode);
    const handleExportFormatChange = handleOptionChange(FileFormat, FileFormatDisplayNames, setFileFormat);



    return (
        <form className="config-menu">
            <Dropdown
                labelText="Select language"
                id={"lang-config-dropdown"}
                selected={displayNameFromEnumValue(Language, LanguageDisplayNames, generatorTaskDto.lang)}
                options={Object.values(LanguageDisplayNames)}
                onChange={handleLangChange}/>
            <Dropdown
                labelText="Select flashcard type"
                id={"mode-config-dropdown"}
                selected={displayNameFromEnumValue(Mode, ModeDisplayNames, generatorTaskDto.mode)}
                options={Object.values(ModeDisplayNames)}
                onChange={handleModeChange}/>
            <Dropdown
                labelText="Select file format "
                id={"file-format-config-dropdown"}
                selected={displayNameFromEnumValue(FileFormat, FileFormatDisplayNames, fileFormat)}
                options={Object.values(FileFormatDisplayNames)}
                onChange={handleExportFormatChange}/>
        </form>
    );
}

export default ConfigMenu;