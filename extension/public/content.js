chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_LOCATION") {
        const url = window.location.href;

        const regex = /@(-?\d+\.\d+),(-?\d+\.\d+)/;
        const match = url.match(regex);

        if (match) {
            sendResponse({
                latitude: parseFloat(match[1]),
                longitude: parseFloat(match[2]),
                success: true
            })
        } else {
            sendResponse({ success: false, error: "No coordinates found in URL" });
        }
    }
});