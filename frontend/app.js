// app.js

// DOM Elements
const chatInput = document.getElementById("chatInput");
const chatSendBtn = document.getElementById("chatSendBtn");
const chatMessages = document.getElementById("chatMessages");
const versionSelect = document.getElementById("versionSelect");
const refreshPreviewBtn = document.getElementById("refreshPreviewBtn");
const deviceToggleBtn = document.getElementById("deviceToggleBtn");
const sitePreview = document.getElementById("sitePreview");
const previewPanel = document.getElementById("previewPanel");

// New toggle button for preview panel
const togglePreviewBtn = document.getElementById("togglePreviewBtn");

// Code panel stuff
const toggleCodeBtn = document.getElementById("toggleCodeBtn");
const codePanel = document.getElementById("codePanel");
const tabButtons = document.querySelectorAll(".tab-btn");
const codeBlocks = document.querySelectorAll(".code-block");

// Tag buttons
const createTagBtn = document.getElementById("createTag");
const reviseTagBtn = document.getElementById("reviseTag");

const examplesBtn = document.getElementById('examplesBtn');
const examplesPanel = document.getElementById('examplesPanel');
const closeExamplesBtn = document.getElementById('closeExamplesBtn');

// Layout container
const layoutContainer = document.getElementById('layoutContainer');

examplesBtn.addEventListener('click', () => {
    examplesPanel.classList.add('active');
});

closeExamplesBtn.addEventListener('click', () => {
    examplesPanel.classList.remove('active');
});

// Toggle Preview Panel
togglePreviewBtn.addEventListener('click', () => {
    previewPanel.classList.toggle('collapsed');
    layoutContainer.classList.toggle('preview-collapsed');
});

function showLoading() {
    const loadingOverlay = document.getElementById("loadingOverlay");
    if (loadingOverlay) {
        loadingOverlay.classList.add("active");
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById("loadingOverlay");
    if (loadingOverlay) {
        loadingOverlay.classList.remove("active");
    }
}

// Add to your app.js
document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const targetId = btn.dataset.target;
        const codeBlock = document.getElementById(targetId);
        const textToCopy = codeBlock.textContent;

        try {
            await navigator.clipboard.writeText(textToCopy);
            btn.textContent = 'Copied!';
            btn.classList.add('copied');
            setTimeout(() => {
                btn.textContent = 'Copy';
                btn.classList.remove('copied');
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    });
});

// Fake in-memory storage for versions/code (for demonstration):
let versions = [
    // Example:
    // { id: 1, html: "<!DOCTYPE html>...", css: "body { ... }", js: "console.log('Hello');" },
];

// Track "active" version
let currentVersionId = null;

// ---------------
// Initial State
// ---------------
chatInput.disabled = true;
chatSendBtn.disabled = true;
reviseTagBtn.disabled = true;

// ---------------
// Tag Button Event Listeners
// ---------------
createTagBtn.addEventListener("click", () => {
    // Prepend "/create " if not already present.
    if (!chatInput.value.toLowerCase().startsWith("/create")) {
        chatInput.value = "/create " + chatInput.value;
    }
    // Enable text input and send button.
    chatInput.disabled = false;
    chatSendBtn.disabled = false;
    // Enable /revise tag now for later use.
    reviseTagBtn.disabled = false;
    chatInput.focus();
});

reviseTagBtn.addEventListener("click", () => {
    // Prepend "/revise " if not already present.
    if (!chatInput.value.toLowerCase().startsWith("/revise")) {
        chatInput.value = "/revise " + chatInput.value;
    }
    chatInput.focus();
});

// ---------------
// Chat / Conversation Flow with Tag Detection
// ---------------
chatSendBtn.addEventListener("click", async () => {
    const rawMessage = chatInput.value.trim();
    if (!rawMessage) return;

    // Check for tags "/create" or "/revise"
    let tag = null;
    let content = rawMessage;
    if (rawMessage.toLowerCase().startsWith("/create")) {
        tag = "/create";
        content = rawMessage.slice(7).trim(); // Remove the tag
    } else if (rawMessage.toLowerCase().startsWith("/revise")) {
        tag = "/revise";
        content = rawMessage.slice(7).trim();
    } else {
        addChatMessage("Error: Please prefix your prompt with /create or /revise", "system");
        return;
    }

    // Display the original message (with the tag) in the chat
    addChatMessage(rawMessage, "user");
    chatInput.value = "";

    showLoading();

    await new Promise(resolve => setTimeout(resolve, 20));

    try {
        let endpoint = "";
        let payload = {};

        if (tag === "/create") {
            endpoint = "/generate";
            payload = { user_prompt: content };
        } else if (tag === "/revise") {
            endpoint = "/conversation";
            const selectedVersion = versions.find(v => v.id === currentVersionId);
            if (!selectedVersion) {
                addChatMessage("Error: No version selected to revise.", "system");
                hideLoading();
                return;
            }

            payload = {
                message: content,
                html: selectedVersion.html,
                css: selectedVersion.css
            };
        }

        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error("Failed to send message to server");
        }

        const data = await response.json();

        // For /create, we expect { html, css }
        // For /revise, we expect { reply, html, css } if a revision is applied.
        if (tag === "/create") {
            addChatMessage("Site created successfully.", "system");
            // Create a new version and update the preview.
            const newVersion = { id: Date.now(), html: data.html, css: data.css, inline_html: data.inline_html, js: "" };
            handleNewVersion(newVersion);
        } else if (tag === "/revise") {
            addChatMessage(data.reply, "system");
            if (data.html && data.css) {
                const newVersion = { id: Date.now(), html: data.html, css: data.css, inline_html: data.inline_html, js: "" };
                handleNewVersion(newVersion);
            }
        }
    } catch (err) {
        addChatMessage(`Error: ${err.message}`, "system");
    } finally {
        hideLoading();
    }
});

/**
 * Helper to add chat messages to the UI
 * @param {string} text
 * @param {'user'|'system'} sender
 */
function addChatMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("chat-message", sender);
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);

    // Auto-scroll the chat box
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ----------------------------------
// Handling Versions & Preview
// ----------------------------------
refreshPreviewBtn.addEventListener("click", () => {
    loadVersionIntoPreview(currentVersionId);
});

versionSelect.addEventListener("change", () => {
    const selectedId = parseInt(versionSelect.value, 10);
    loadVersionIntoPreview(selectedId);
});

/**
 * Load a version's HTML/CSS/JS into the preview iframe and code blocks
 * @param {number} versionId 
 */
function loadVersionIntoPreview(versionId) {
    if (!versionId) return;

    const selectedVersion = versions.find(v => v.id === versionId);
    if (!selectedVersion) return;

    currentVersionId = versionId;

    // Use inline_html if available, otherwise fallback to html.
    const previewHTML = selectedVersion.inline_html ? selectedVersion.inline_html : selectedVersion.html;

    // Load the chosen HTML into the iframe.
    const iframeDoc = sitePreview.contentDocument || sitePreview.contentWindow.document;
    iframeDoc.open();
    iframeDoc.write(previewHTML);
    iframeDoc.close();

    // Update code panels with the original HTML/CSS/JS.
    document.getElementById("htmlCode").textContent = selectedVersion.html;
    document.getElementById("cssCode").textContent = selectedVersion.css || "/* No CSS provided */";
    document.getElementById("jsCode").textContent = selectedVersion.js || "// No JS provided";
}


// -----------------------------
// Device Toggle
// -----------------------------
let isMobileView = false;
deviceToggleBtn.addEventListener("click", () => {
    isMobileView = !isMobileView;
    if (isMobileView) {
        sitePreview.style.width = "375px"; // approximate phone width
        sitePreview.style.height = "667px"; // approximate phone height
    } else {
        sitePreview.style.width = "100%";
        sitePreview.style.height = "100%";
    }
});

// -----------------------------
// Code Panel Tabs
// -----------------------------
tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        tabButtons.forEach(b => b.classList.remove("active"));
        codeBlocks.forEach(block => block.classList.remove("active"));

        btn.classList.add("active");

        const tab = btn.dataset.tab;
        const targetCodeBlock = document.getElementById(`${tab}Code`);
        if (targetCodeBlock) {
            targetCodeBlock.classList.add("active");
        }
    });
});

// -----------------------------
// Expand/Collapse Code Panel
// -----------------------------
toggleCodeBtn.addEventListener("click", () => {
    codePanel.classList.toggle("collapsed");
});

// -----------------------------
// Utility: Handling New or Updated Versions
// -----------------------------
function handleNewVersion(newVersion) {
    versions.push(newVersion);
    const option = document.createElement("option");
    option.value = newVersion.id;
    option.textContent = `Version ${newVersion.id}`;
    versionSelect.appendChild(option);

    versionSelect.value = newVersion.id;
    loadVersionIntoPreview(newVersion.id);
}