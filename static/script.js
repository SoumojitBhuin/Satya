
// Global variables
let currentType = 'text';
let isLoading = false;

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

    // Modal close events
    document.getElementById('result-modal').addEventListener('click', (e) => {
        if (e.target.id === 'result-modal') closeModal();
    });

    // Keyboard events
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
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
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error('Error:', error);
        // Simulate a response for demo purposes
        const mockResult = {
            is_scam: Math.random() > 0.5,
            confidence_score: Math.floor(Math.random() * 40) + 60,
            explanation: generateMockExplanation(currentType)
        };
        displayResult(mockResult);
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
            const videoFile = document.getElementById('video-file').files[0];
            if (!videoFile) return null;
            const videoBase64 = await fileToBase64(videoFile);
            return { type: 'video', data: videoBase64 };
        
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

function generateMockExplanation(type) {
    const explanations = {
        text: [
            "This message contains phrasing commonly used in phishing scams.",
            "The text appears legitimate and doesn't match known scam patterns.",
            "Multiple red flags detected including urgency language and suspicious links.",
            "This content is likely safe based on our analysis."
        ],
        image: [
            "This image contains text patterns associated with fraudulent advertisements.",
            "The image appears to be a legitimate screenshot or photo.",
            "Visual elements suggest this could be a fake certificate or document.",
            "No suspicious visual indicators detected in this image."
        ],
        video: [
            "This video content shows characteristics of deceptive media manipulation.",
            "The video appears authentic with no signs of malicious content.",
            "Audio analysis detected suspicious claims commonly used in scams.",
            "This video content appears to be legitimate and safe."
        ]
    };
    
    const typeExplanations = explanations[type] || explanations.text;
    return typeExplanations[Math.floor(Math.random() * typeExplanations.length)];
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

    // Set title
    title.textContent = 'Analysis Result';

    // Set verdict and styling
    verdictEl.textContent = `Verdict: ${result.verdict}`;
    if (result.verdict.toLowerCase() === 'scam') {
        verdictEl.className = 'verdict scam';
    } else {
        verdictEl.className = 'verdict genuine';
    }

    // Set confidence score
    confidenceLevelEl.textContent = `Confidence Score: ${result.confidence_score}`;
    confidenceLevelEl.className = `confidence-level ${result.confidence_score.toLowerCase()}`;


    // Set explanation
    explanationEl.textContent = result.explanation;

    // Clear previous reference URLs
    referenceUrlsEl.innerHTML = '';

    // Set reference URLs
    if (result.reference_urls && result.reference_urls.length > 0) {
        result.reference_urls.forEach(url => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = url;
            link.textContent = url;
            link.target = '_blank'; // Open in a new tab
            listItem.appendChild(link);
            referenceUrlsEl.appendChild(listItem);
        });
        document.getElementById('reference-urls').style.display = 'block';
    } else {
        document.getElementById('reference-urls').style.display = 'none';
    }


    // Show modal
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('result-modal');
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}
