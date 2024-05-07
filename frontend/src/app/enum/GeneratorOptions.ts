/*
    * This file contains the enums defining supported generator options,
    * mapping objects for the display names of the generator options,
    * and type definitions for the generator options and display name maps.
 */

/*
    * Enums to define the supported generator options.
    * The values of the enums are used by the API and backend, and should not be changed.
 */
export enum Mode {
    PRACTICE = 'PRACTICE',
    DEFINITIONS = 'DEFINITIONS',
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE',
    OPEN_ENDED = 'OPEN_ENDED',
}

export enum Language {
    EN = 'en',
    DE = 'de',
}

export enum FileFormat {
    CSV = 'csv',
    APKG = 'apkg',
}


/*
    * Mapping objects for the display names for the generator options.
    * The values are used to display the options in the UI. They can be changed.
 */
export const ModeDisplayNames = {
    [Mode.PRACTICE]: 'Practice',
    [Mode.DEFINITIONS]: 'Definitions',
    [Mode.MULTIPLE_CHOICE]: 'Multiple Choice',
    [Mode.OPEN_ENDED]: 'Open Ended',
} as const;

export const LanguageDisplayNames = {
    [Language.EN]: 'English',
    [Language.DE]: 'German',
} as const;

export const FileFormatDisplayNames = {
    [FileFormat.CSV]: 'CSV',
    [FileFormat.APKG]: 'Anki',
} as const;


/*
    * Type definitions for the generator options and display name maps, for TypeScript type checking.
 */
export type OptionEnum = typeof Mode | typeof Language | typeof FileFormat;
export type DisplayNameMap = typeof ModeDisplayNames | typeof LanguageDisplayNames | typeof FileFormatDisplayNames;