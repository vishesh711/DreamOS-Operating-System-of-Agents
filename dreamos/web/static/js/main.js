// DreamOS Web Interface JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const commandInput = document.getElementById('commandInput');
    const sendBtn = document.getElementById('sendBtn');
    const terminalOutput = document.getElementById('terminalOutput');
    const clearBtn = document.getElementById('clearBtn');
    const helpBtn = document.getElementById('helpBtn');
    const voiceToggle = document.getElementById('voiceToggle');
    const micBtn = document.getElementById('micBtn');
    const statusIndicator = document.getElementById('statusIndicator');
    const lastUpdateTime = document.getElementById('lastUpdateTime');
    const initModal = new bootstrap.Modal(document.getElementById('initModal'));
    const initButton = document.getElementById('initButton');
    const voiceFeature = document.getElementById('voiceFeature');
    const datavizFeature = document.getElementById('datavizFeature');
    const dbqueryFeature = document.getElementById('dbqueryFeature');
    const stopSpeechBtn = document.getElementById('stopSpeechBtn');
    
    // Socket.IO connection
    const socket = io();
    
    // Initialize UI state
    let isInitialized = false;
    let isVoiceEnabled = false;
    let isListening = false;
    
    // Show initialization modal on page load
    initModal.show();
    
    // Speech recognition setup (if browser supports it)
    let recognition = null;
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            commandInput.value = transcript;
            stopListening();
            sendCommand();
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
            stopListening();
            updateStatus('error', 'Speech recognition error: ' + event.error);
        };
        
        recognition.onend = function() {
            stopListening();
        };
    } else {
        micBtn.disabled = true;
        micBtn.title = 'Speech recognition not supported in this browser';
    }
    
    // Initialize DreamOS backend
    initButton.addEventListener('click', function() {
        initializeDreamOS();
    });
    
    // Event listeners
    commandInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendCommand();
        }
    });
    
    sendBtn.addEventListener('click', sendCommand);
    
    clearBtn.addEventListener('click', function() {
        // Clear terminal but keep greeting
        const greeting = terminalOutput.querySelector('.terminal-greeting');
        terminalOutput.innerHTML = '';
        if (greeting) {
            terminalOutput.appendChild(greeting);
        }
    });
    
    helpBtn.addEventListener('click', function() {
        commandInput.value = 'help';
        sendCommand();
    });
    
    voiceToggle.addEventListener('change', function() {
        isVoiceEnabled = voiceToggle.checked;
        updateStatus('info', isVoiceEnabled ? 'Voice enabled' : 'Voice disabled');
    });
    
    micBtn.addEventListener('click', function() {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    });
    
    // Stop Speech button
    stopSpeechBtn.addEventListener('click', function() {
        stopSpeech();
        updateStatus('info', 'Speech stopped');
    });
    
    // Socket.IO event listeners
    socket.on('connect', function() {
        console.log('Connected to server');
        updateStatus('success', 'Connected to server');
        
        // Hide connection error if it was showing
        document.getElementById('connectionError').classList.add('d-none');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateStatus('error', 'Disconnected from server');
        
        // Show connection error
        document.getElementById('connectionError').classList.remove('d-none');
    });
    
    socket.on('connect_error', function(err) {
        console.error('Connection error:', err);
        updateStatus('error', 'Connection error');
        
        // Show connection error
        document.getElementById('connectionError').classList.remove('d-none');
    });
    
    // Close error button
    document.getElementById('closeErrorBtn').addEventListener('click', function() {
        document.getElementById('connectionError').classList.add('d-none');
    });
    
    // Add keyboard shortcut to stop speech (Escape key)
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            stopSpeech();
        }
    });
    
    // Functions
    function initializeDreamOS() {
        const features = {
            enable_voice: voiceFeature.checked,
            enable_dataviz: datavizFeature.checked,
            enable_dbquery: dbqueryFeature.checked
        };
        
        updateStatus('warning', 'Initializing DreamOS...');
        
        fetch('/api/init', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(features)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isInitialized = true;
                isVoiceEnabled = features.enable_voice;
                voiceToggle.checked = isVoiceEnabled;
                
                initModal.hide();
                updateStatus('success', 'DreamOS initialized successfully');
                addSystemMessage('DreamOS initialized with features: ' + 
                                 Object.entries(features)
                                    .filter(([_, value]) => value)
                                    .map(([key, _]) => key.replace('enable_', ''))
                                    .join(', '));
            } else {
                updateStatus('error', 'Initialization failed: ' + data.message);
                addSystemMessage('Initialization failed: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error initializing DreamOS:', error);
            updateStatus('error', 'Error initializing DreamOS');
            addSystemMessage('Error initializing DreamOS: ' + error.message, 'error');
        });
    }
    
    function sendCommand() {
        const command = commandInput.value.trim();
        
        if (!command) return;
        
        if (!isInitialized) {
            addSystemMessage('Please initialize DreamOS first', 'error');
            return;
        }
        
        // Display the command in the terminal
        displayCommand(command);
        
        // Clear the input
        commandInput.value = '';
        
        // Update status
        updateStatus('warning', 'Processing command...');
        
        // Disable the input and send button while processing
        commandInput.disabled = true;
        sendBtn.disabled = true;
        
        // Add processing indicator
        const processingIndicator = document.createElement('div');
        processingIndicator.className = 'processing-indicator';
        processingIndicator.innerHTML = '<div class="spinner-border spinner-border-sm text-light me-2" role="status"></div><span>Processing...</span>';
        terminalOutput.appendChild(processingIndicator);
        scrollToBottom();
        
        // Send command to server with timeout
        const timeoutId = setTimeout(() => {
            // If no response after 15 seconds
            const indicator = document.querySelector('.processing-indicator');
            if (indicator) {
                indicator.innerHTML = '<span class="text-warning">Command is taking longer than expected...</span>';
            }
        }, 15000);
        
        // Send command to server
        socket.emit('command', { command: command });
        
        // Set up a timeout for server response
        socket.once('command_response', function(data) {
            clearTimeout(timeoutId);
            
            // Remove processing indicator
            const indicator = document.querySelector('.processing-indicator');
            if (indicator) {
                indicator.remove();
            }
            
            // Re-enable input and button
            commandInput.disabled = false;
            sendBtn.disabled = false;
            commandInput.focus();
            
            // Handle response
            displayResponse(data.command, data.response, data.status);
            updateStatus(data.status === 'success' ? 'success' : 'error', 
                        data.status === 'success' ? 'Command processed' : 'Error processing command');
            
            // If voice is enabled, speak the response
            if (isVoiceEnabled && data.response) {
                speakText(data.response);
            }
        });
    }
    
    function displayCommand(command) {
        const commandEntry = document.createElement('div');
        commandEntry.className = 'command-entry';
        commandEntry.innerHTML = `<span class="command-prompt">&gt;</span> <span class="command-text">${escapeHtml(command)}</span>`;
        terminalOutput.appendChild(commandEntry);
        scrollToBottom();
    }
    
    function displayResponse(command, response, status) {
        // Find the last command entry
        const commandEntries = document.querySelectorAll('.command-entry');
        const lastCommandEntry = commandEntries[commandEntries.length - 1];
        
        if (lastCommandEntry) {
            // Create response element
            const responseElement = document.createElement('div');
            responseElement.className = 'response-text';
            if (status === 'error') {
                responseElement.classList.add('error-text');
            }
            
            // Convert markdown to HTML if the response contains markdown
            if (response.includes('```') || response.includes('#') || 
                response.includes('*') || response.includes('|')) {
                responseElement.innerHTML = marked.parse(escapeHtml(response));
            } else {
                responseElement.textContent = response;
            }
            
            // Add the response after the command
            lastCommandEntry.appendChild(responseElement);
            scrollToBottom();
        }
    }
    
    function addSystemMessage(message, type = 'info') {
        const systemMessage = document.createElement('div');
        systemMessage.className = 'system-message';
        
        if (type === 'error') {
            systemMessage.classList.add('error-text');
        } else if (type === 'warning') {
            systemMessage.classList.add('warning-text');
        }
        
        systemMessage.textContent = message;
        terminalOutput.appendChild(systemMessage);
        scrollToBottom();
    }
    
    function updateStatus(type, message) {
        // Update status indicator
        statusIndicator.className = 'badge';
        switch (type) {
            case 'success':
                statusIndicator.classList.add('bg-success');
                break;
            case 'error':
                statusIndicator.classList.add('bg-danger');
                break;
            case 'warning':
                statusIndicator.classList.add('bg-warning');
                break;
            case 'info':
            default:
                statusIndicator.classList.add('bg-info');
                break;
        }
        
        statusIndicator.textContent = message;
        
        // Update timestamp
        const now = new Date();
        lastUpdateTime.textContent = now.toLocaleTimeString();
    }
    
    function scrollToBottom() {
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }
    
    function startListening() {
        if (!recognition) return;
        
        try {
            recognition.start();
            isListening = true;
            micBtn.classList.add('btn-danger');
            micBtn.classList.remove('btn-outline-secondary');
            updateStatus('warning', 'Listening...');
        } catch (e) {
            console.error('Error starting speech recognition:', e);
        }
    }
    
    function stopListening() {
        if (!recognition) return;
        
        try {
            recognition.stop();
        } catch (e) {
            console.error('Error stopping speech recognition:', e);
        }
        
        isListening = false;
        micBtn.classList.remove('btn-danger');
        micBtn.classList.add('btn-outline-secondary');
        updateStatus('success', 'Ready');
    }
    
    function speakText(text) {
        // Use browser's speech synthesis if available
        if ('speechSynthesis' in window && isVoiceEnabled) {
            // We should use browser speech in the following cases:
            // 1. When we're using the web interface only (no backend voice)
            // 2. When we're on a device that doesn't support the pyttsx3 backend
            
            // This could be made configurable via a setting in the future
            const useBrowserSpeech = true;
            
            if (useBrowserSpeech) {
                // Cancel any ongoing speech
                window.speechSynthesis.cancel();
                
                // Limit text length for speech
                let speakText = text;
                if (text.length > 300) {
                    // Speak only first part of very long responses
                    speakText = text.substring(0, 297) + '...';
                }
                
                const utterance = new SpeechSynthesisUtterance(speakText);
                
                // Optional: select voice (can be made configurable in settings)
                /*
                const voices = window.speechSynthesis.getVoices();
                if (voices.length > 0) {
                    // Find a preferred voice (e.g., first English voice)
                    const englishVoice = voices.find(voice => voice.lang.startsWith('en-'));
                    if (englishVoice) {
                        utterance.voice = englishVoice;
                    }
                }
                */
                
                // Speak the text
                window.speechSynthesis.speak(utterance);
            }
        }
    }
    
    function stopSpeech() {
        // Cancel any ongoing speech synthesis
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }
    
    // Helper functions
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}); 