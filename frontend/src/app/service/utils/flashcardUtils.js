// flashcardUtils.js
import convertCSVToAPKG from '@2anki/csv-to-apkg';

/**
 * Converts flashcards to CSV format.
 * @param {Array} flashcards - The flashcards to convert.
 * @return {string} The CSV string.
 */
export function convertToCSV(flashcards) {
    const csvRows = [];
    const headers = ['frontSide', 'backSide'];
    // Iterate over the JSON data and extract only the required fields
    flashcards.forEach(row => {
        const frontSide = row.frontSide.replace(/"/g, '\\"'); // Escape double quotes
        const backSide = row.backSide.replace(/"/g, '\\"'); // Escape double quotes
        csvRows.push(`"${frontSide}";"${backSide}"`); // Create a row with frontSide and backSide
    });
    return csvRows.join('\n');
}

/**
 * Initiates a download of a CSV file.
 * @param {Array} flashcards - The flashcards to convert.
 * @param {string} filename - The name of the file to download (without extension).
 */
export function downloadCSV(flashcards, filename) {
    const csvData = convertToCSV(flashcards);
    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', `${filename}.csv`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

/**
 * Converts flashcards to the APKG format.
 * @param {Array} flashcards - The flashcards to convert.
 * @return {Promise<Buffer>} A promise that resolves with the APKG blob.
 */
export function convertToApkg(flashcards) {
    const csvData = convertToCSV(flashcards);
    return convertCSVToAPKG(csvData); // Promise<Buffer>
}

/**
 * Initiates a download of an APKG file.
 * @param {Array} flashcards - The flashcards to convert.
 * @param {string} filename - The name of the file to download (without extension).
 */
export function downloadApkg(flashcards, filename) {
    convertToApkg(flashcards).then(buffer => {
        const blob = new Blob([buffer], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', `${filename}.apkg`);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }).catch(error => {
        console.error('Error downloading APKG file:', error);
    });

}