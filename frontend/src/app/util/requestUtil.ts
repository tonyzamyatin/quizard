import axios, {AxiosRequestConfig, AxiosResponse, Method} from 'axios';

interface RequestProps {
    endpoint: string
    method: Method,
    data?: any,
    config?: AxiosRequestConfig
}

export async function sendRequest({ endpoint, method, data, config }: RequestProps): Promise<AxiosResponse> {
    try {
        return await axios({
            url: endpoint,
            method: method,
            data: data,
            headers: {
                'Content-Type': 'application/json',
            },
            ...config
        });
    } catch (error: any) {
        throw error;
    }
}