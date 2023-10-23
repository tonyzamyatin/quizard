import React from "react";

function CTAButton({buttonName}) {
    return <button className={`CTA-button ${buttonName.replace(' ', '-').toLowerCase()}`}>{buttonName}</button>;
}

export default CTAButton