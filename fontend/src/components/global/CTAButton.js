import React from "react";

function CTAButton({ buttonName, onButtonClick, active }) {

    function handleClick() {
        if (active) { // Only call onButtonClick if the button is active
            onButtonClick();
        }
    }

    return (
        <button
            className={`CTA-button ${buttonName.replace(' ', '-').toLowerCase()} ${!active ? 'inactive' : ''}`}
            onClick={handleClick}
            disabled={!active} // Disable the button if not active
        >
            {buttonName}
        </button>
    );
}

export default CTAButton;
