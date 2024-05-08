import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './app/components/App';

async function enableMocking() {
    if (process.env.REACT_APP_USE_MOCKS) {
        const { worker } = await import('./mocks/browser')

        // `worker.start()` returns a Promise that resolves
        // once the Service Worker is up and ready to intercept requests.
        return worker.start()
    }
}

enableMocking().then(() => {
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
})
