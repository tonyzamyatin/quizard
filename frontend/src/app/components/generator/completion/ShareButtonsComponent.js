import React, { useEffect } from 'react';

const ShareButtonComponent = () => {
    useEffect(() => {
        // Function to load the ShareThis script
        const loadScript = () => {
            const script = document.createElement('script');
            script.src = "https://platform-api.sharethis.com/js/sharethis.js#property=65dc401e98ac00001970d5d9&product=inline-share-buttons&source=platform";
            script.async = true;
            document.head.appendChild(script);
            return script;
        };

        // Remove any existing script to ensure it's clean
        const existingScript = document.querySelector(
            'script[src="https://platform-api.sharethis.com/js/sharethis.js#property=65dc401e98ac00001970d5d9&product=inline-share-buttons&source=platform"]'
        );

        if (existingScript) {
            document.head.removeChild(existingScript);
        }

        // Load a fresh script
        const script = loadScript();

        // Clean up the script when the component unmounts
        return () => {
            document.head.removeChild(script);
        };
    }, []);

    return;
};

export default ShareButtonComponent;
