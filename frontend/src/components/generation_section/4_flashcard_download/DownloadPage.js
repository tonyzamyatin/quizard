import React from "react";
import CTAButton from "../../global/CTAButton";

function DownloadPage( { flashcardsJSON, exportFormat } ) {

    console.log(`Export Format: ${exportFormat}, Flashcard JSON: ${ flashcardsJSON }`)

    const handleDownloadClick = () => {
        switch (exportFormat) {
            case "CSV":
                let csvData = convertToCSV();
                downloadCSV(csvData, 'flashcards.csv')
        }
    }

    const convertToCSV = () => {
        const csvRows = [];
        const headers = ['frontSide', 'backSide'];
        // Iterate over the JSON data and extract only the required fields
        flashcardsJSON.forEach(row => {
            const frontSide = row.frontSide.replace(/"/g, '\\"'); // Escape double quotes
            const backSide = row.backSide.replace(/"/g, '\\"'); // Escape double quotes
            csvRows.push(`"${frontSide}";"${backSide}"`); // Create a row with frontSide and backSide
        });
        return csvRows.join('\n');
    }

    const downloadCSV = (csvData, filename) => {
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', filename);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    return (
        <div className="generation-section-container ">
            <CTAButton buttonName="Download" onButtonClick={ handleDownloadClick } active={ true }/>
        </div>
    )
}

export default DownloadPage;