// Global variables
let currentType = 'text';
let isLoading = false;
let analysisResult = null; // Store the latest result for the report button

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupFileUpload();
});

function initializeEventListeners() {
    // Input selector buttons
    const selectorButtons = document.querySelectorAll('.selector-btn');
    selectorButtons.forEach(button => {
        button.addEventListener('click', () => switchInputType(button.dataset.type));
    });

    // Check button
    document.getElementById('check-button').addEventListener('click', handleVerification);

    // --- FIX STARTS HERE ---
    // Modal close events - with a safety check
    const modal = document.getElementById('result-modal');
    
    // Only add listeners if the modal element actually exists
    if (modal) {
        modal.addEventListener('click', (e) => {
            // Close if clicking on the background overlay
            if (e.target.id === 'result-modal') closeModal();
        });
        // Find the close button inside the modal and add listener
        const closeButton = modal.querySelector('.close-button');
        if (closeButton) {
            closeButton.addEventListener('click', closeModal);
        }

        // Report button logic
        const reportButton = modal.querySelector('.report-button');
        if (reportButton) {
            reportButton.addEventListener('click', () => {
                // Use the stored analysis result to pass the detailed explanation to the report page
                const explanation = analysisResult ? encodeURIComponent(analysisResult.detailed_explanation) : "";
                window.location.href = `/report?explanation=${explanation}`;
            });
        }
    } else {
        console.error("Error: The result modal was not found in the HTML.");
    }
    // --- FIX ENDS HERE ---


    // Keyboard events
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    // Report button logic
    const reportButton = modal.querySelector('.report-button');
    reportButton.addEventListener('click', () => {
        // Use the stored analysis result to pass the detailed explanation to the report page
        const explanation = analysisResult ? encodeURIComponent(analysisResult.detailed_explanation) : "";
        window.location.href = `/report?explanation=${explanation}`;
    });
}

function switchInputType(type) {
    if (isLoading) return;

    currentType = type;
    
    // Update button states
    document.querySelectorAll('.selector-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });

    // Update input areas
    document.querySelectorAll('.input-area').forEach(area => {
        area.classList.toggle('active', area.id === `${type}-input`);
    });
}

function setupFileUpload() {
    const fileUploadAreas = document.querySelectorAll('.file-upload-area');
    
    fileUploadAreas.forEach(area => {
        // Drag and drop events
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });

        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const fileInput = area.parentElement.querySelector('.file-input');
                fileInput.files = files;
                updateFileUploadDisplay(area, files[0]);
            }
        });
    });

    // File input change events
    document.querySelectorAll('.file-input').forEach(input => {
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const area = e.target.parentElement.querySelector('.file-upload-area');
                updateFileUploadDisplay(area, e.target.files[0]);
            }
        });
    });
}

function updateFileUploadDisplay(area, file) {
    const uploadText = area.querySelector('.upload-text');
    const uploadSubtext = area.querySelector('.upload-subtext');
    
    uploadText.textContent = file.name;
    uploadSubtext.textContent = `File selected: ${(file.size / 1024 / 1024).toFixed(2)} MB`;
    area.style.background = 'linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.05))';
    area.style.borderColor = '#28A745';
}

async function handleVerification() {
    if (isLoading) return;

    const data = await prepareData();
    if (!data) {
        alert('Please provide content to verify.');
        return;
    }

    setLoadingState(true);

    try {
        const response = await fetch('/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            // This will catch HTTP errors like 500, 404 etc.
            throw new Error(`The server responded with an error: ${response.status}`);
        }

        const result = await response.json();
        analysisResult = result; // Store the successful result
        displayResult(result);

    } catch (error) {
        console.error('Verification Error:', error);
        // **FIX**: Show a user-friendly error in the modal instead of crashing
        const errorResult = {
            verdict: 'Error',
            explanation: 'An unexpected error occurred. Could not connect to the verification service. Please try again later.',
            detailed_explanation: 'There was a network or server error. Check the browser console for more details.'
        };
        analysisResult = errorResult; // Store the error result
        displayResult(errorResult);
    } finally {
        setLoadingState(false);
    }
}

async function prepareData() {
    switch (currentType) {
        case 'text':
            const textContent = document.getElementById('text-content').value.trim();
            if (!textContent) return null;
            return { type: 'text', data: textContent };
        
        case 'image':
            const imageFile = document.getElementById('image-file').files[0];
            if (!imageFile) return null;
            const imageBase64 = await fileToBase64(imageFile);
            return { type: 'image', data: imageBase64 };
        
        case 'video':
            alert("Video verification is not supported in this version.");
            return null;
        
        default:
            return null;
    }
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function setLoadingState(loading) {
    isLoading = loading;
    const button = document.getElementById('check-button');
    
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<div class="spinner"></div> Analyzing...';
    } else {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-shield-alt"></i> Check with Satya';
    }
}

function displayResult(result) {
    const modal = document.getElementById('result-modal');
    const title = document.getElementById('result-title');
    const verdictEl = document.getElementById('result-verdict');
    const confidenceLevelEl = document.getElementById('confidence-level');
    const explanationEl = document.getElementById('result-explanation');
    const referenceUrlsEl = document.getElementById('reference-urls').querySelector('ul');

    title.textContent = 'Analysis Result';

    // **FIX**: Safely access properties to prevent crashes
    const verdict = result.verdict || 'N/A';
    const confidence = result.confidence_score || 'unknown';
    
    verdictEl.textContent = `Verdict: ${verdict}`;
    verdictEl.className = 'verdict'; // Reset classes
    verdictEl.classList.add(verdict.toLowerCase());

    confidenceLevelEl.textContent = `Confidence: ${confidence}`;
    confidenceLevelEl.className = 'confidence-level'; // Reset classes
    confidenceLevelEl.classList.add(confidence.toLowerCase());

    explanationEl.textContent = result.explanation || 'No explanation available.';

    referenceUrlsEl.innerHTML = '';
    const referenceContainer = document.getElementById('reference-urls');

    if (result.reference_urls && result.reference_urls.length > 0) {
        result.reference_urls.forEach(url => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = url;
            link.textContent = url;
            link.target = '_blank';
            listItem.appendChild(link);
            referenceUrlsEl.appendChild(listItem);
        });
        referenceContainer.style.display = 'block';
    } else {
        referenceContainer.style.display = 'none';
    }

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('result-modal');
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}


