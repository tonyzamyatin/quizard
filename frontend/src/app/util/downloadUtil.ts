// downloadUtil.js



/**
 * Initiates a download of a CSV file.
 * @param {BlobPart} flashcardsCSV - The flashcards as CSV.
 * @param {string} filename - The name of the file to download (without extension).
 * @deprecated
 */
export function downloadCSV(flashcardsCSV: BlobPart, filename: string) {
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
 * @param {BlobPart} flashcardsAPKG - The flashcards as APKG format.
 * @param {string} filename - The name of the file to download (without extension).
 * @deprecated
 */
export function downloadApkg(flashcardsAPKG: BlobPart, filename: string) {
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

export function downloadBlob(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}