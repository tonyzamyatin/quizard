import React, {useEffect, useState} from "react";

function Dropdown({ id, labelText, options, selected,  onChange }) {
    return (
        <div>
            <label htmlFor= {id}>{labelText}</label>
            <select id ={id} value={selected} onChange={onChange}>
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