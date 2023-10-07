import React, {useState} from "react";
import './slider.css';

function SelectionSliderField({ fieldName, isSelected, onClick }) {
    return (
        <div
            className={`slider-field ${isSelected ? "selected" : ""}`}
            onClick={() => onClick(fieldName)}
        >
            <span>{fieldName}</span>
        </div>
    );
}


function SelectionSlider({ fields }) {
    const [selectedField, setSelectedField] = useState("Text");
    const fieldWidth = 200 / fields.length; // Assuming total width is 900px

    const handleFieldClick = (fieldName) => {
        setSelectedField(fieldName);
    };

    return (
        <div className="slider-container">
            <div className="slider-track">
                {fields.map((field) => (
                    <SelectionSliderField
                        fieldName={field}
                        isSelected={field === selectedField}
                        onClick={handleFieldClick}
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

function TextInputField ({ placeholder }) {
    return (
        <div className="Input-field">
            <p className="Input-field-placeholder">
                {placeholder}
            </p>
        </div>
    );
}

function PDFUploadField ({ placeholder }) {
    return (
        <div className="Input-field">
            <p className="Input-field-placeholder">
                Coming soon ...
            </p>
            // TODO: Display a big font-awesome icon below the text
        </div>
    );
}




function TextUploadField ({ placeholder }) {
    return (
        <div className="Input-field">
            <p className="Input-field-placeholder">
                {placeholder}
            </p>
        </div>
    );
}

// function UploadContainer() {
//     return (
//          //TODO
//     )
// }
//

function CTAButton({ buttonName }) {
    return (
        <button className="CTA-button">
            {buttonName}
        </button>
    );
}

const App = () => {
    return <SelectionSlider fields={["Text", "PDF"]} />;
};

export default App;



// function UploadContainer() {
//     return (
//         // TODO
//     );
// }
//
// TextInputField is a field where the user is able to enter text. It is used in multiple places in the app, varying in size
//
// UploadContainer contains the slider and below the slider an input field, which is a grey 1044x446 px box. Is the slider set to "Text" the box displays the placeholder text :
//     "Copy and paste your notes here (between 250 and 10,000 characters) "
// and the user can directly insert text. Is it set to "PDF" the box should change to a darker shade of grey and displey the message "Document uplaoding coming soon..." with a 60x60 black font awesome icon below that.
//
//     Do you think I should use a seperate component for the PDF upload, give that I will implement it later down the line?
//
//     Below the input field, aligned to the right of the container, is a teal 196x40px button that says "Generate". Clicking this button will cause the whole section to slide out of view to the left, and the next setcion to slide into view from the left. Clicking the button send the text to the backend.
//
//     Next to the "Generate" button there is a grey 196x40px button that says "Go back", to go back one step in the process and display the last section with all its contents (selected or entered by the user). It should slide in the same way from the left as it slid out of view.
//
//     Write an appropriate React structure and CSS to bring this discription to life!
