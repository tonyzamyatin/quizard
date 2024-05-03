import React, {useEffect} from "react";
import DOMPurify from 'dompurify';

function TextUploadField({ text, setText }) {

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
        // TODO: Comma separation doesn't work -.-
        let charStr = text.length.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        return (
            <p className="character-count-batch"> <span className="character-count-number">{charStr}</span > / 500,000 characters</p>
        );
    }

    useEffect(() => {
        // Load saved text from localStorage when the component mounts
        const savedText = sessionStorage.getItem('savedText');
        if (savedText) {
            setText(savedText);
        }
    }, [setText]);

    useEffect(() => {
        // Save text to localStorage when it changes
        sessionStorage.setItem('savedText', text);
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
