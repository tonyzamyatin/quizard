// setupDevMocks.js
import { server } from './mocks/server'; // Adjust path based on project structure

if (process.env.REACT_APP_USE_MOCKS) {
    server.listen({
        onUnhandledRequest: 'bypass' // or 'warn' based on preference
    });
}