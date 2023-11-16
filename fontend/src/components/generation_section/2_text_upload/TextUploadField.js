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
    }

    // Display character length of the text, separating every three digits with a comma
    const displayCharacterCount = () => {
        // For when we display the site in the browser language
        // let charsStr = Number(text.length).toLocaleString()
        // TODO: Comma seperation doesn't work -.-
        let charStr = text.length.toString().replace(/(\\d)(?=(\\d{3})+(?!\\d))/g, '$1,');
        return (
            <p className="character-count">{charStr}/500,000 characters</p>
        );
    }

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

    // TODO: Decide on the number of max characters. (currently 500.000)
    // TODO: Cut off text when it is too long and notify user that the text exceeds the accepted length
    return (
        <div className="text-upload-field">
            <textarea
                placeholder="Copy and paste your notes here (between 249 and 500,000 characters)"
                value={text} // Set the value of input to our state
                onChange={handleChange} // Update state when input changes
            />
            {displayCharacterCount()}
        </div>
    );
}



export default TextUploadField;
