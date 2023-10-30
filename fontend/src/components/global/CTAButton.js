import React from "react";

function CTAButton({buttonName, onButtonClick}) {

    function handleClick()  {
        onButtonClick();
    }

    return <button className={`CTA-button ${buttonName.replace(' ', '-').toLowerCase()}`} onClick={handleClick}>{buttonName}</button>;
}

export default CTAButton