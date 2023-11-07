import React, {useState, useEffect} from "react";
import DOMPurify from 'dompurify';

function TextUploadField({ text, setText}) {

    const sanitizeText = (dirtyText) => {
        return DOMPurify.sanitize(dirtyText);
    }
;

    const handleChange = (event) => {
        let sanitizedText;
        sanitizedText = sanitizeText(event.target.value)
        setText(sanitizedText);
    };

    useEffect(() => {
        // Load saved text from localStorage when the component mounts
        const savedText = localStorage.getItem('savedText');
        if (savedText) {
            setText(savedText);
        }
    }, []);

    useEffect(() => {
        // Save text to localStorage when it changes
        localStorage.setItem('savedText', text);
    }, [text]);

    return (
        <div className="text-upload-field">
            <textarea
                placeholder="Copy and paste your notes here (between 250 and 100,000 characters)"
                value={text} // Set the value of input to our state
                onChange={handleChange} // Update state when input changes
            />
        </div>
    );
}



export default TextUploadField;
