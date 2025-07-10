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
        overlayElement.classList.remove('hidden'); // Make it display: flex or block
        // Add 'visible' class to trigger CSS opacity transition
        setTimeout(() => {
            overlayElement.classList.add('visible');
        }, 10); // A small delay to ensure display is applied before opacity transition
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
            alert("Please enter a math expression or equation!");
            return;
        }

        try {
            // This is the line that needs to be changed to connect to the public backend!
            // When you deploy your Python Backend to a hosting service (like Render),
            // you will receive a PUBLIC URL.
            // Example deployed URL: 'https://your-ams-backend.onrender.com/solve'
            // Please REPLACE 'http://127.0.0.1:5000/solve' with your PUBLIC URL.

            const backendApiUrl = 'https://ams-5b33.onrender.com/solve'; // <-- THIS LINE MUST BE CHANGED!

            // If you HAVE deployed your backend to Render and have the URL, change the line above to:
            // const backendApiUrl = 'https://YOUR_APP_NAME_ON_RENDER.onrender.com/solve';
            // Example: const backendApiUrl = 'https://ams-solver-backend.onrender.com/solve';

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

    // --- New JavaScript for Setting, Chat, Login/Signup ---

    // Simulated user login and comment status
    let isLoggedIn = false;
    let hasCommented = false;

    // Setting Button Elements
    const settingsButton = document.getElementById('settingsButton');

    // Chat Box Elements
    const chatButton = document.getElementById('chatButton');
    const chatBoxContainer = document.getElementById('chatBoxContainer');
    // Ensure chatBoxContainer is not null before querying its children
    const closeChatBtn = chatBoxContainer ? chatBoxContainer.querySelector('.close-btn') : null;
    const commentForm = document.getElementById('commentForm');
    const commentText = document.getElementById('commentText');
    const starsRating = document.getElementById('starsRating');
    const selectedRatingInput = document.getElementById('selectedRating');
    const commentSection = document.getElementById('commentSection');
    const chatStatusMessage = document.getElementById('chatStatusMessage');

    let currentRating = 0; // To store the current star rating

    // Auth Modal Elements
    const authButton = document.getElementById('authButton');
    const authModal = document.getElementById('authModal');
    // Ensure authModal is not null before querying its children
    const closeAuthButton = authModal ? authModal.querySelector('.close-button') : null;
    const tabButtons = authModal ? authModal.querySelectorAll('.tab-button') : [];
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const authMessage = document.getElementById('authMessage');

    // Function to update chat box status message based on login and comment status
    function updateChatStatus() {
        if (!isLoggedIn) {
            chatStatusMessage.textContent = 'You need to log in to comment and rate.';
            if (commentForm) commentForm.style.display = 'none';
        } else if (hasCommented) {
            chatStatusMessage.textContent = 'You have already submitted a comment and rating. Thank you!';
            if (commentForm) commentForm.style.display = 'none';
        } else {
            chatStatusMessage.textContent = 'Share your thoughts!';
            if (commentForm) commentForm.style.display = 'block';
        }
    }

    // --- Setting Button Logic ---
    if (settingsButton) {
        settingsButton.addEventListener('click', () => {
            alert('Settings functionality will be added later!');
            // You can open a dropdown menu or a settings modal here
        });
    }

    // --- Chat Box Logic ---
    if (chatButton) {
        chatButton.addEventListener('click', () => {
            if (chatBoxContainer) {
                // Use the existing openOverlay/closeOverlay functions for animation
                if (chatBoxContainer.classList.contains('hidden')) {
                    openOverlay(chatBoxContainer);
                } else {
                    closeOverlay(chatBoxContainer);
                }
                updateChatStatus(); // Update status message when opening/closing
            }
        });
    }

    if (closeChatBtn) {
        closeChatBtn.addEventListener('click', () => {
            if (chatBoxContainer) {
                closeOverlay(chatBoxContainer);
            }
        });
    }

    // Handle Star Rating
    if (starsRating) {
        const stars = starsRating.querySelectorAll('.star');

        stars.forEach(star => {
            star.addEventListener('mouseover', function() {
                if (!hasCommented) { // Only allow hover if not already commented
                    const value = parseInt(this.dataset.value);
                    stars.forEach((s, i) => {
                        if (i < value) {
                            s.classList.add('hovered');
                        } else {
                            s.classList.remove('hovered');
                        }
                    });
                }
            });

            star.addEventListener('mouseout', function() {
                if (!hasCommented) { // Only remove hover if not already commented
                    stars.forEach(s => s.classList.remove('hovered'));
                }
                // Maintain selected state
                stars.forEach((s, i) => {
                    if (i < currentRating) {
                        s.classList.add('selected');
                    } else {
                        s.classList.remove('selected');
                    }
                });
            });

            star.addEventListener('click', function() {
                if (!isLoggedIn) {
                    alert('You need to log in to rate!');
                    return;
                }
                if (hasCommented) {
                    alert('You can only rate and comment once!');
                    return;
                }
                const value = parseInt(this.dataset.value);
                currentRating = value;
                selectedRatingInput.value = value;
                stars.forEach((s, i) => {
                    if (i < value) {
                        s.classList.add('selected');
                    } else {
                        s.classList.remove('selected');
                    }
                });
            });
        });
    }

    // Handle Comment Form Submission (simulated)
    if (commentForm) {
        commentForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent page reload

            if (!isLoggedIn) {
                alert('You need to log in to submit comments and ratings!');
                return;
            }

            if (hasCommented) {
                alert('You can only submit a comment once!');
                return;
            }

            const comment = commentText.value.trim();
            const rating = parseInt(selectedRatingInput.value);

            if (comment === '' || rating === 0) {
                alert('Please enter a comment and select stars for rating!');
                return;
            }

            // Simulate comment submitted
            hasCommented = true;

            // Display comment on the page (in a real app, this goes to a server)
            const newCommentDiv = document.createElement('div');
            newCommentDiv.classList.add('user-comment');
            newCommentDiv.innerHTML = `
                <strong>You:</strong> <span class="rating">${'★'.repeat(rating)}${'☆'.repeat(5 - rating)}</span><br>
                <span>${comment}</span>
            `;
            commentSection.prepend(newCommentDiv); // Add new comment to the top

            // Clear form
            commentText.value = '';
            selectedRatingInput.value = '0';
            currentRating = 0;
            starsRating.querySelectorAll('.star').forEach(s => s.classList.remove('selected', 'hovered'));

            updateChatStatus(); // Update status after commenting
            alert('Thank you for your comment and rating!');
            commentForm.style.display = 'none'; // Hide the form after submission
        });
    }

    // --- Auth Modal (Login/Signup) Logic ---
    if (authButton) {
        authButton.addEventListener('click', () => {
            if (isLoggedIn) {
                // If already logged in, prompt for logout
                if (confirm('Do you want to log out?')) {
                    isLoggedIn = false;
                    hasCommented = false; // Reset comment status on logout
                    authButton.textContent = 'Log in / Sign up';
                    alert('You have been logged out!');
                    updateChatStatus(); // Update chat box status
                }
                // Close modal whether user logs out or not
                if (authModal) closeOverlay(authModal); // Use closeOverlay for animation
            } else {
                // If not logged in, show login modal
                if (authModal) openOverlay(authModal);
                if (authMessage) authMessage.textContent = ''; // Clear previous messages
            }
        });
    }

    if (closeAuthButton) {
        closeAuthButton.addEventListener('click', () => {
            if (authModal) closeOverlay(authModal);
        });
    }

    // Close modal when clicking outside the content
    if (authModal) {
        authModal.addEventListener('click', (event) => {
            if (event.target === authModal) {
                closeOverlay(authModal);
            }
        });
    }

    // Switch between Login and Signup tabs
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            const tab = this.dataset.tab;
            if (tab === 'login') {
                if (loginForm) loginForm.classList.remove('hidden');
                if (signupForm) signupForm.classList.add('hidden');
            } else {
                if (loginForm) loginForm.classList.add('hidden');
                if (signupForm) signupForm.classList.remove('hidden');
            }
            if (authMessage) authMessage.textContent = ''; // Clear messages when switching tabs
        });
    });

    // Handle Login Form Submission (simulated)
    if (loginForm) {
        loginForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            // Simple simulated login
            if (username === 'testuser' && password === 'password123') {
                isLoggedIn = true;
                authButton.textContent = 'Log out'; // Change button text
                if (authModal) closeOverlay(authModal);
                alert('Login successful!');
                updateChatStatus(); // Update chat box status
            } else {
                if (authMessage) authMessage.textContent = 'Incorrect username or password.';
            }
        });
    }

    // Handle Signup Form Submission (simulated)
    if (signupForm) {
        signupForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const signupUsername = document.getElementById('signupUsername').value;
            const signupEmail = document.getElementById('signupEmail').value;
            const signupPassword = document.getElementById('signupPassword').value;
            const signupConfirmPassword = document.getElementById('signupConfirmPassword').value;

            if (signupPassword !== signupConfirmPassword) {
                if (authMessage) authMessage.textContent = 'Passwords do not match.';
                return;
            }

            // In a real application, you would send this data to a server for registration
            alert('Registration successful! You can now log in.');
            // Automatically switch to login tab after successful registration
            const loginTabButton = document.querySelector('.tab-button[data-tab="login"]');
            if (loginTabButton) loginTabButton.click();
            if (authMessage) authMessage.textContent = ''; // Clear message
        });
    }

    // Initial update of chat status when the page loads
    updateChatStatus();
});