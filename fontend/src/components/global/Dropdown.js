import React, {useEffect, useState} from "react";

function Dropdown({ labelText, selected, options, onChange }) {
    return (
        <div>
            <label>{labelText}</label>
            <select value={selected} onChange={onChange}>
                <option value="" disabled>Select...</option>
                {options.map((optionText, index) => (
                    <option key={index} value={optionText}>
                        {optionText}
                    </option>
                ))}
            </select>
        </div>
    );
}


export default Dropdown;