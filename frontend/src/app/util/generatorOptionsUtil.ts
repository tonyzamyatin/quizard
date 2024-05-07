import {DisplayNameMap, OptionEnum} from "../enum/generatorOptions";
/*
    * This file contains utility functions for mapping  between enum values of generator options and their
    * corresponding display names.
 */


/**
 * Returns the display name for the given enum value.
 * If the enum value is null, null is returned.
 *
 * @param enumObject the enum to get the value from
 * @param displayNamesMap the display names map for the corresponding enum
 * @param enumValue the value to get the display name for
 * @throws Error if no display name is found for the given enum value
 */
export function displayNameFromEnumValue<T extends OptionEnum>(
    enumObject: T,
    displayNamesMap: DisplayNameMap,
    enumValue: T[keyof T] | null
): string | null {
    if (enumValue === null) {
        return null;
    }
    const key = enumObject[enumValue as keyof T] as keyof typeof displayNamesMap;
    const displayName = displayNamesMap[key];
    if (!displayName) {
        console.error(`No display name found for option: ${String(enumValue)}`);
        return null;
    }
    return displayName;
}

/**
 * Returns the enum value for the given display name.
 *
 * @param enumObject the enum to get the value from
 * @param displayNamesMap the display names map for the corresponding enum
 * @param displayName the display name to get the value for
 * @returns the enum value for the given display name, or null if no value is found
 */
export function enumValueFromDisplayName<T extends OptionEnum>(
    enumObject: T,
    displayNamesMap: DisplayNameMap,
    displayName: string
): T[keyof T] | null {
    const enumKey = findKeyByDisplayName(displayNamesMap, displayName);
    if (!enumKey) {
        console.error(`No option found for display name: ${displayName}`);
        return null;
    }
    return enumObject[enumKey];
}

/**
 * Helper function to find the key in the displayNamesMap by display name.
 * @param displayNamesMap the display names for the corresponding enum
 * @param displayName the display name to find the key for
 *
 */
function findKeyByDisplayName(displayNamesMap: DisplayNameMap, displayName: string): keyof typeof displayNamesMap | null {
    return (Object.keys(displayNamesMap) as Array<keyof typeof displayNamesMap>).find(key => displayNamesMap[key] === displayName) || null;
}