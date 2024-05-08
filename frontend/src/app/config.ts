/**
 * Configuration file for the application. Do not expose on client side.
 */
export const config = {
    generator : {
        minTextLength: 250,             // characters
        maxTextLength: 500000,     // characters
        pollingDelayLong: 3000,        // milliseconds
        pollingDelayShort: 1000,        // milliseconds
    }
}