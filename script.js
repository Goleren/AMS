// script.js
document.addEventListener('DOMContentLoaded', () => {
    // Main HTML elements
    const mathExpressionInput = document.getElementById('mathExpressionInput');
    const solveButton = document.getElementById('solveButton');
    const resultsSection = document.getElementById('resultsSection');
    const resultText = document.getElementById('resultText');
    const explanationText = document.getElementById('explanationText');

    // Elements for navigation bar and overlays
    const btnVersions = document.getElementById('btnVersions');
    const btnInstructions = document.getElementById('btnInstructions');
    const versionsSection = document.getElementById('versionsSection');
    const instructionsSection = document.getElementById('instructionsSection');
    const closeVersions = document.getElementById('closeVersions');
    const closeInstructions = document.getElementById('closeInstructions');

    // Function to open an overlay/modal
    function openOverlay(overlayElement) {
        overlayElement.classList.remove('hidden'); // Make it display: flex
        // Add 'visible' class to trigger CSS opacity transition
        setTimeout(() => {
            overlayElement.classList.add('visible');
        }, 10); // A small delay to ensure display:flex is applied before opacity transition
    }

    // Function to close an overlay/modal
    function closeOverlay(overlayElement) {
        overlayElement.classList.remove('visible'); // Remove 'visible' class to trigger opacity transition
        setTimeout(() => {
            overlayElement.classList.add('hidden'); // After transition, hide completely
        }, 300); // Wait time matches CSS transition duration
    }

    // Event listeners for "AMS 1.0" (Versions) button
    btnVersions.addEventListener('click', () => {
        openOverlay(versionsSection);
    });

    // Event listeners for "Instructions" button
    btnInstructions.addEventListener('click', () => {
        openOverlay(instructionsSection);
    });

    // Event listeners for closing buttons (the 'x')
    closeVersions.addEventListener('click', () => {
        closeOverlay(versionsSection);
    });

    closeInstructions.addEventListener('click', () => {
        closeOverlay(instructionsSection);
    });

    // Optional: Close overlay when clicking outside the content area
    versionsSection.addEventListener('click', (event) => {
        if (event.target === versionsSection) { // Only close if clicking directly on the dimmed background
            closeOverlay(versionsSection);
        }
    });

    instructionsSection.addEventListener('click', (event) => {
        if (event.target === instructionsSection) { // Only close if clicking directly on the dimmed background
            closeOverlay(instructionsSection);
        }
    });


    // --- Math Solving Logic ---
    solveButton.addEventListener('click', async () => {
        const expression = mathExpressionInput.value.trim();

        if (expression === "") {
            alert("Please enter a math expression or equation!"); // Alert message in English
            return;
        }

        try {
            // !!! IMPORTANT: CHANGE THIS URL TO YOUR DEPLOYED BACKEND URL FOR PUBLIC ACCESS !!!
            // Currently, it points to your local machine (127.0.0.1:5000).
            // Example of a deployed URL: 'https://your-ams-backend.onrender.com/solve'
            const backendApiUrl = 'http://127.0.0.1:5000/solve'; 

            const response = await fetch(backendApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expression: expression })
            });

            // Check if the HTTP response itself was successful (e.g., 200 OK)
            if (!response.ok) {
                // If backend returned an error status (e.g., 400, 500)
                const errorData = await response.json(); // Try to parse error message from backend
                resultText.textContent = `Error: ${errorData.message || 'Unknown error occurred on the server.'}`;
                explanationText.textContent = errorData.explanation || "Please check your input or refer to the instructions.";
                resultsSection.classList.remove('hidden');
                console.error("Backend error response:", errorData);
                return; // Stop execution here
            }

            const data = await response.json(); // Parse the successful JSON response from Backend

            if (data.success) {
                resultText.textContent = data.result;
                explanationText.textContent = data.explanation;
                resultsSection.classList.remove('hidden'); // Show results section
            } else {
                // This branch handles cases where backend explicitly sends success: false, but HTTP status is 200
                resultText.textContent = `Error: ${data.message}`;
                explanationText.textContent = data.explanation || "Could not solve this expression/equation.";
                resultsSection.classList.remove('hidden');
            }

        } catch (error) {
            // This catches network errors (e.g., server not running, connection refused)
            resultText.textContent = "Connection Error!";
            explanationText.textContent = "Could not connect to the math solver server. Please ensure the Python backend is running or check the API URL in script.js.";
            resultsSection.classList.remove('hidden');
            console.error("Error connecting to backend:", error);
        }
    });
});
