// public/js/app.js
const STORAGE_KEY = "manuscript_data";
const VERSION_KEY = "manuscript_version";

async function loadData() {
    try {
        // Ask for the 40-byte version file
        const resVersion = await fetch('./data/version.json');
        const { version: liveVersion } = await resVersion.json();

        // Compare with local storage
        if (localStorage.getItem(VERSION_KEY) === liveVersion) {
            console.log("Loading fast from cache...");
            return JSON.parse(localStorage.getItem(STORAGE_KEY));
        }

        // If versions don't match, download the new data
        console.log("Downloading fresh manuscript...");
        const resData = await fetch('./data/manuscript.json');
        const data = await resData.json();

        // Save it for next time
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
            localStorage.setItem(VERSION_KEY, liveVersion);
        } catch (e) {
            console.warn("Could not cache data (Storage full).");
        }

        return data;
    } catch (error) {
        console.error("Failed to load manuscript:", error);
    }
}
