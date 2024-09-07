import {ErrorDetails} from "../dto/errorDetails";

/**
 * Handle error response from the server by logging the error details
 * and returning the error details as an object.
 * @param error the error response from the server
 * @returns the error details as an object
 */
export function handleError(error: any): ErrorDetails | null {
    if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        const { name, description } = error.response.data;
        console.log(`Error name: ${name}`);
        console.log(`Error description: ${description}`);
        return { name, message: description };
    } else if (error.request) {
        // The request was made but no response was received
        console.log(error.request);
    } else {
        // Something happened in setting up the request that triggered an Error
        console.log('Error', error.message);
    }
    return null;
}