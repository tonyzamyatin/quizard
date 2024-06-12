import React, {createContext, useState, useContext, ReactNode} from 'react';

const HealthCheckContext = createContext({
    isBackendHealthy: false,
    checkBackendHealth: () => {},
});

export const HealthCheckProvider = ({ children }: { children: ReactNode }) => {
    const [isBackendHealthy, setIsBackendHealthy] = useState(true);

    const checkBackendHealth = () => {
        // Implement the actual health check logic here
        fetch('/health')
            .then(response => {
                if (!response.ok) throw new Error('Backend down');
                return response.json();
            })
            .then(data => setIsBackendHealthy(data.status === 'healthy'))
            .catch(() => setIsBackendHealthy(false));
    };

    return (
        <HealthCheckContext.Provider value={{ isBackendHealthy, checkBackendHealth }}>
            {children}
        </HealthCheckContext.Provider>
    );
};

export const useHealthCheck = () => useContext(HealthCheckContext);
