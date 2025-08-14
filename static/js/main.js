// main.js - Core application functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize application
    initializeApp();
});

function initializeApp() {
    // Check if database is initialized
    checkDatabaseStatus();
    
    // Add event listeners
    addEventListeners();
    
    // Initialize tooltips and UI enhancements
    initializeUI();
}

function addEventListeners() {
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmission);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Copy to clipboard functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn')) {
            copyToClipboard(e.target.dataset.copy);
        }
    });
}

function handleFormSubmission(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Add loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Executing...';
    submitBtn.disabled = true;
    
    // Submit form data
    submitForm(form.action || window.location.pathname, data)
        .finally(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
}

async function submitForm(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        displayResult(result);
        
        // Track attempt
        trackAttempt(endpoint, data, result.success);
        
    } catch (error) {
        displayError('Network error: ' + error.message);
    }
}

function handleKeyboardShortcuts(e) {
    // Ctrl + Enter to submit form
    if (e.ctrlKey && e.key === 'Enter') {
        const activeForm = document.querySelector('form');
        if (activeForm) {
            activeForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard!', 'success');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function trackAttempt(endpoint, data, success) {
    const attempt = {
        timestamp: new Date().toISOString(),
        endpoint: endpoint,
        payload: JSON.stringify(data),
        success: success,
        userAgent: navigator.userAgent
    };
    
    // Store in local storage for client-side tracking
    const attempts = JSON.parse(localStorage.getItem('ctf_attempts') || '[]');
    attempts.push(attempt);
    
    // Keep only last 100 attempts
    if (attempts.length > 100) {
        attempts.splice(0, attempts.length - 100);
    }
    
    localStorage.setItem('ctf_attempts', JSON.stringify(attempts));
}

async function checkDatabaseStatus() {
    try {
        const response = await fetch('/setup');
        const result = await response.json();
        
        if (result.error) {
            showNotification('Database not initialized. Click "Initialize CTF Database" to begin.', 'warning');
        }
    } catch (error) {
        console.log('Database status check failed:', error);
    }
}

function initializeUI() {
    // Add syntax highlighting to code blocks
    const codeBlocks = document.querySelectorAll('code');
    codeBlocks.forEach(block => {
        if (block.textContent.toLowerCase().includes('union') || 
            block.textContent.toLowerCase().includes('select')) {
            block.classList.add('sql-syntax');
        }
    });
    
    // Add copy buttons to code blocks
    codeBlocks.forEach(block => {
        if (block.textContent.length > 10) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.dataset.copy = block.textContent;
            copyBtn.title = 'Copy to clipboard';
            
            const wrapper = document.createElement('div');
            wrapper.className = 'code-wrapper';
            block.parentNode.insertBefore(wrapper, block);
            wrapper.appendChild(block);
            wrapper.appendChild(copyBtn);
        }
    });
}
