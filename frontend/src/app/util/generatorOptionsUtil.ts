/*
    * This file contains utility functions for mapping  between enum values of generator options and their
    * corresponding display names.
 */


import {DisplayNameMap, OptionEnum, OptionEnumType} from "../enum/GeneratorOptions";

/**
 * Returns the display name for the given enum value.
 * If the enum value is null, null is returned.
 *
 * @param displayNameMap the display name map for the corresponding enum
 * @param enumValue the enum value to get the display name for
 * @throws Error if no display name is found for the given enum value
 */
export function displayNameFromEnumValue(
    displayNameMap: DisplayNameMap,
    enumValue: OptionEnum | null
): string | undefined {
    if (enumValue === null) {
        return '';
    }
    const displayNameMapKey = enumValue as keyof typeof displayNameMap;
    return displayNameMap[displayNameMapKey] || '';
}

/**
 * Returns the enum value for the given display name.
 *
 * @param enumType the enum to map the value for (used for type inference)
 * @param displayNameMap the display name map which maps the enum values to the corresponding display names
 * @param displayName the display name to get the enum value for
 * @returns the enum value for the given display name, or null if the display name does not exist in the map
 */
export function enumValueFromDisplayName(
    enumType: OptionEnumType,
    displayNameMap: DisplayNameMap,
    displayName: string
): OptionEnumType[keyof OptionEnumType] | null {
    const displayNameMapKey = findDisplayNameKey(displayNameMap, displayName);
    if (!displayNameMapKey) {
        console.error(`No option found for display name: ${displayName}`);
        return null;
    }
    // Convert the displayNameMapKey (string value) to the enum value type
    return displayNameMapKey as OptionEnumType[keyof OptionEnumType];
}

/**
 * Helper function to find the key in the displayNameMap by display name.
 * @param displayNameMap the display name map for the corresponding enum
 * @param displayName the display name to find the key for
 *
 */
function findDisplayNameKey(displayNameMap: DisplayNameMap, displayName: string): keyof typeof displayNameMap | null {
    return (Object.keys(displayNameMap) as Array<keyof typeof displayNameMap>).find(key => displayNameMap[key] === displayName) || null;
}