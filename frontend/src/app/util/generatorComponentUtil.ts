import {config} from "../config";

/**
 * Check if the text length is within the allowed range
 * @param text
 */
export function inputTextLengthInRange(text: string) {
    return text.length > config.generator.minTextLength && text.length <= config.generator.maxTextLength;
}

/**
 * Safely divide two numbers, return 0 if denominator is 0
 * @param numerator
 * @param denominator
 */
export function safeDivide(numerator: number, denominator: number) {
    denominator = +denominator;  // Coerce to number.
    if (!denominator) {  // Matches +0, -0, NaN
        return 0;
    }
    return +numerator / denominator;
}