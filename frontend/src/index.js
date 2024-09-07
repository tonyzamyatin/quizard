import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './app/components/App';

async function enableMocking() {
    if (process.env.REACT_APP_USE_MOCKS) {
        const { worker } = require('./mocks/browser')

        // Start the Service Worker
        return worker.start({
            onUnhandledRequest: 'bypass' // or 'warn' based on preference
        });
    }
}

enableMocking().then(() => {
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
}).catch(err => {
    console.error('Error starting mock worker:', err);
});
