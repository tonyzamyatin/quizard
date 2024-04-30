// FlashcardUtils.js



/**
 * Initiates a download of a CSV file.
 * @param {Array} flashcardsCSV - The flashcards as CSV.
 * @param {string} filename - The name of the file to download (without extension).
 */
export function downloadCSV(flashcardsCSV, filename) {
    const blob = new Blob([flashcardsCSV], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', `${filename}.csv}`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}


/**
 * Initiates a download of an APKG file.
 * @param {Array} flashcardsAPKG - The flashcards as APKG format.
 * @param {string} filename - The name of the file to download (without extension).
 */
export function downloadApkg(flashcardsAPKG, filename) {
    const blob = new Blob([flashcardsAPKG], { type: 'application/octet-stream' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', `${filename}.apkg`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

}