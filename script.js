// script.js

// --- DOM Elements ---
const btnVersions = document.getElementById('btnVersions');
const settingsButton = document.getElementById('settingsButton');
const chatButton = document.getElementById('chatButton');
const authButton = document.getElementById('authButton'); // The login/register button
const btnInstructions = document.getElementById('btnInstructions');

const versionsSection = document.getElementById('versionsSection');
const instructionsSection = document.getElementById('instructionsSection');
const chatBoxContainer = document.getElementById('chatBoxContainer');
const authModal = document.getElementById('authModal');

const mainInput = document.getElementById('mathExpressionInput');
const solveButton = document.getElementById('solveButton');
const resultsSection = document.getElementById('resultsSection');
const resultText = document.getElementById('resultText');
const explanationText = document.getElementById('explanationText');

// Auth Modal specific elements
const authModalCloseButton = authModal.querySelector('.close-button');
const loginTab = authModal.querySelector('button[data-tab="login"]');
const signupTab = authModal.querySelector('button[data-tab="signup"]');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const authMessage = document.getElementById('authMessage');

// Password toggle icons
const loginPasswordInput = document.getElementById('loginPassword');
const signupPasswordInput = document.getElementById('signupPassword');
const signupConfirmPasswordInput = document.getElementById('signupConfirmPassword');

// Navbar user profile elements (new)
const navbarRight = document.querySelector('.navbar-right');
let userProfileInfo = null; // Will be created dynamically
let profilePicture = null;
let userName = null;

// --- Initial State / Setup ---
// Simulate user login status (true if logged in, false if not)
let isLoggedIn = false; // Initially not logged in

// Function to update navbar based on login status
function updateNavbarAuthStatus() {
    if (isLoggedIn) {
        authButton.classList.add('hidden'); // Hide login/register button
        if (!userProfileInfo) { // Create profile info elements if they don't exist
            userProfileInfo = document.createElement('div');
            userProfileInfo.id = 'userProfileInfo';
            profilePicture = document.createElement('img');
            profilePicture.id = 'profilePicture';
            profilePicture.src = 'https://via.placeholder.com/30/87ceeb/FFFFFF?text=P'; // Default profile pic (blue background, white text 'P')
            profilePicture.alt = 'Profile Picture';
            userName = document.createElement('span');
            userName.id = 'userName';
            userName.textContent = 'User Name'; // Default user name

            userProfileInfo.appendChild(profilePicture);
            userProfileInfo.appendChild(userName);
            navbarRight.prepend(userProfileInfo); // Add to the right side of navbar

            // Add event listener for profile click (for customization)
            userProfileInfo.addEventListener('click', showProfileCustomization);
        }
        userProfileInfo.classList.remove('hidden'); // Show profile info
        // You might want to load actual user data here if available
        // userName.textContent = currentUser.name;
        // profilePicture.src = currentUser.profilePicUrl;
    } else {
        authButton.classList.remove('hidden'); // Show login/register button
        if (userProfileInfo) {
            userProfileInfo.classList.add('hidden'); // Hide profile info
        }
    }
}

// Function to show/hide the profile customization modal (simulated)
function showProfileCustomization() {
    alert('Profile Customization: Here you can change your profile picture and name.');
    // In a real app, you'd open another modal for editing profile
}

// Call on load to set initial state
updateNavbarAuthStatus();

// --- Event Listeners for Modals/Overlays ---

// Common close button logic for all overlays (versions, instructions, settings, auth modal)
document.querySelectorAll('.overlay .close-button, .modal .close-button').forEach(button => {
    button.addEventListener('click', () => {
        button.closest('.overlay, .modal').classList.remove('visible');
    });
});

// Chat box close button
chatBoxContainer.querySelector('.close-btn').addEventListener('click', () => {
    chatBoxContainer.classList.remove('visible');
});

// Open Versions Overlay
btnVersions.addEventListener('click', () => {
    versionsSection.classList.add('visible');
});

// Open Instructions Overlay
btnInstructions.addEventListener('click', () => {
    instructionsSection.classList.add('visible');
});

// Open Settings Overlay (placeholder)
settingsButton.addEventListener('click', () => {
    // For now, it just shows an alert. You can make a real overlay later.
    alert('Settings functionality will be implemented here!');
});

// Toggle Chat Box visibility
chatButton.addEventListener('click', () => {
    chatBoxContainer.classList.toggle('visible');
});

// Open Auth Modal
authButton.addEventListener('click', () => {
    authModal.classList.add('visible');
    // Ensure login tab is active by default when opening
    activateTab('login');
});

// Click outside to close overlays (optional but good UX)
document.addEventListener('click', (event) => {
    // Check if the clicked element is the overlay itself (not content inside)
    if (event.target.classList.contains('overlay') && !event.target.closest('.modal-content')) {
        event.target.classList.remove('visible');
    }
    // Also handle authModal if it has the .modal class
    if (event.target.classList.contains('modal') && !event.target.closest('.modal-content')) {
        event.target.classList.remove('visible');
    }
});


// --- Auth Modal Logic ---

// Function to activate a specific tab (login or signup)
function activateTab(tabName) {
    if (tabName === 'login') {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
    } else { // tabName === 'signup'
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        signupForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
    authMessage.textContent = ''; // Clear previous messages
}

loginTab.addEventListener('click', () => activateTab('login'));
signupTab.addEventListener('click', () => activateTab('signup'));

// Password Toggle Functionality
function setupPasswordToggle(inputElement) {
    if (!inputElement) return; // Exit if element doesn't exist

    const parentFormGroup = inputElement.closest('.form-group');
    if (!parentFormGroup) return;

    let toggleIcon = parentFormGroup.querySelector('.password-toggle-icon');

    if (!toggleIcon) { // Create toggle icon if it doesn't exist
        toggleIcon = document.createElement('i');
        toggleIcon.classList.add('fas', 'fa-eye-slash', 'password-toggle-icon'); // Default to eye-slash (hidden)
        parentFormGroup.appendChild(toggleIcon);
    }

    toggleIcon.addEventListener('click', () => {
        if (inputElement.type === 'password') {
            inputElement.type = 'text';
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        } else {
            inputElement.type = 'password';
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        }
    });
}

// Apply password toggle to all relevant fields
setupPasswordToggle(loginPasswordInput);
setupPasswordToggle(signupPasswordInput);
setupPasswordToggle(signupConfirmPasswordInput);


// Switch to Login from Signup Form (the "Log in now" link)
const switchToLoginLink = document.getElementById('switchToLoginLink');
if (switchToLoginLink) {
    switchToLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        activateTab('login');
    });
}

// Switch to Signup from Login Form (the "Register now" link)
const switchToSignupLink = document.getElementById('switchToSignupLink');
if (switchToSignupLink) {
    switchToSignupLink.addEventListener('click', (e) => {
        e.preventDefault();
        activateTab('signup');
    });
}


// --- Form Submission Handlers (Simulated) ---

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    // Basic validation
    if (username === '' || password === '') {
        authMessage.textContent = 'Please enter both username and password.';
        authMessage.style.color = 'red';
        return;
    }

    // Simulate successful login
    if (username === 'testuser' && password === 'password123') {
        authMessage.textContent = 'Login successful!';
        authMessage.style.color = 'green';
        isLoggedIn = true;
        updateNavbarAuthStatus();
        setTimeout(() => {
            authModal.classList.remove('visible'); // Close modal after successful login
            loginForm.reset(); // Clear form fields
            authMessage.textContent = '';
        }, 1000);
    } else {
        authMessage.textContent = 'Invalid username or password.';
        authMessage.style.color = 'red';
    }
});

signupForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;
    const termsCheckbox = document.getElementById('termsCheckbox');

    // Basic validation
    if (username === '' || email === '' || password === '' || confirmPassword === '') {
        authMessage.textContent = 'Please fill in all fields.';
        authMessage.style.color = 'red';
        return;
    }
    if (password !== confirmPassword) {
        authMessage.textContent = 'Passwords do not match.';
        authMessage.style.color = 'red';
        return;
    }
    if (!