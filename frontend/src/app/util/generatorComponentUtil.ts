import {config} from "../config";

/**
 * Check if the text length is within the allowed range
 * @param text
 */
export function inputTextLengthInRange(text: string) {
    return text.length > config.generator.minTextLength && text.length <= config.generator.maxTextLength;
}


