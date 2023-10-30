import React from "react";

function SliderField({ fieldName, isSelected, onClick }) {



    return (
        <div
            className={`slider-field ${isSelected ? "selected" : ""}`}
            onClick={() => onClick(fieldName)}
        >
            <span>{fieldName}</span>
        </div>
    );
}

function Slider({ fields, selectedField, onFieldClick }) {
    const fieldWidth = 200 / fields.length; // Assuming total width is 900px


    return (
        <div className="slider-container">
            <div className="slider-track">
                {fields.map((field) => (
                    <SliderField
                        fieldName={field}
                        isSelected={field === selectedField}
                        onClick={onFieldClick}
                        key={field}
                    />
                ))}
            </div>
            <div
                className="slider-knob-container"
                style={{
                    width: `${fieldWidth}px`,
                    left: `${fields.indexOf(selectedField) * fieldWidth}px`
                }}
            >
                <div className="slider-knob"></div>
            </div>
        </div>
    );
}

export default Slider;