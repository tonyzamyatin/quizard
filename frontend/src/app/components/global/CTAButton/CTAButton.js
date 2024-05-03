import React from "react";

function CTAButton({ buttonText, buttonType, onButtonClick, active, nonHover = false}) {

    const buttonTypes = []

    function handleClick() {
        if (active) { // Only call onButtonClick if the button is active
            onButtonClick();
        }
    }

    return (
        <button
            className={`CTA-button ${buttonType} ${nonHover ? 'static' : ''}`}
            onClick={handleClick}
            disabled={!active} // Disable the button if not active
        >
            {buttonText}
        </button>
    );
}

export default CTAButton;
