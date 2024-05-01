import axios, { Method } from 'axios';

export async function sendRequest<T>(endpoint: string, method: Method, data?: any): Promise<T> {
    try {
        const response = await axios({
            url: endpoint,
            method: method,
            data: data,
            headers: {
                'Content-Type': 'application/json',
            },
        });
        return response.data;
    } catch (error: any) {
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log(error.response.data);
            console.log(error.response.status);
            console.log(error.response.headers);
        } else if (error.request) {
            // The request was made but no response was received
            console.log(error.request);
        } else {
            // Something happened in setting up the request that triggered an Error
            console.log('Error', error.message);
        }
        throw error;
    }
}