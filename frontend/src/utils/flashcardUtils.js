// flashcardUtils.js

import { saveAs } from 'file-saver';
const AnkiExport = require('anki-apkg-export').default;

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
 * @param {string} deckName - The name of the Anki deck.
 * @return {Promise<Blob>} A promise that resolves with the APKG blob.
 */
export function convertToApkg(flashcards, deckName) {
    const apkg = new AnkiExport(deckName);
    for (const flashcard of flashcards) {
        apkg.addCard(flashcard.frontSide, flashcard.backSide);
    }
    return apkg.save(); // This returns a Promise
}

/**
 * Initiates a download of an APKG file.
 * @param {Array} cards - The flashcards to convert.
 * @param {string} deckName - The name of the Anki deck.
 * @param {string} filename - The name of the file to download (without extension).
 */
export function downloadApkg(cards, deckName, filename) {
    const apkg = new AnkiExport(deckName);

    cards.forEach(card => {
        apkg.addCard(card.frontSide, card.backSide);
    });

    apkg.save().then(zip => {
        saveAs(zip, `${deckName}.apkg`);
    }).catch(err => console.error(err));
}