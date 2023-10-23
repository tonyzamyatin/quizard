import React, {useState} from "react";

function Dropdown({ labelText, options }){

    const [selectedOption, setSelectedOption] = useState("");

    const handleChange = (event) => {
        setSelectedOption(event.target.value);
    }

    return (
        <div>
            <label>{labelText}</label>
            <select value={selectedOption} onChange={handleChange} defaultValue="">
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