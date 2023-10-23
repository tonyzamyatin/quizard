import React from "react";

function CTAButton({buttonName, handleClick}) {
    return <button className={`CTA-button ${buttonName.replace(' ', '-').toLowerCase()}`} onClick={handleClick()}>{buttonName}</button>;
}

export default CTAButton