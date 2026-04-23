class TeacherAssistantApp {
    constructor() {
        this.sessionId = null;
        this.currentMode = 'chat';
        this.API_BASE = '/api';

        this.init();
    }

    async init() {
        await this.createSession();
        this.bindEvents();
    }

    async createSession() {
        try {
            const response = await fetch(`${this.API_BASE}/chat/session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: 'web_user' })
            });
            const data = await response.json();
            this.sessionId = data.session_id;
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    }

    bindEvents() {
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.switchMode(mode);
            });
        });

        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.getElementById('voiceBtn').addEventListener('click', () => this.startVoiceInput());
    }

    switchMode(mode) {
        this.currentMode = mode;
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
    }

    addMessage(role, content, time = null) {
        const messagesList = document.getElementById('messagesList');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (role === 'assistant') {
            avatar.innerHTML = `
                <div class="avatar-glow">
                    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                        <circle cx="20" cy="20" r="18" fill="url(#grad1)"/>
                        <path d="M15 15V25M25 15V25M10 20H30" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
            `;
        } else {
            avatar.innerHTML = `
                <div class="avatar-glow user-avatar">
                    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                        <circle cx="20" cy="20" r="18" fill="url(#grad2)"/>
                        <path d="M15 25C15 25 17 22 20 22C23 22 25 25 25 25" stroke="white" stroke-width="2" stroke-linecap="round"/>
                        <circle cx="20" cy="16" r="4" fill="white"/>
                    </svg>
                </div>
            `;
        }

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'message-content';

        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';

        if (role === 'assistant') {
            const senderSpan = document.createElement('span');
            senderSpan.className = 'message-sender';
            senderSpan.textContent = '小慧老师';
            messageHeader.appendChild(senderSpan);
        }

        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = time || this.formatTime(new Date());
        messageHeader.appendChild(timeSpan);

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = content;

        contentWrapper.appendChild(messageHeader);
        contentWrapper.appendChild(messageText);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentWrapper);

        messagesList.appendChild(messageDiv);
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    formatTime(date) {
        return date.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const text = input.value.trim();
        if (!text) return;

        this.addMessage('user', text);
        input.value = '';

        try {
            const response = await fetch(`${this.API_BASE}/chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    text: text
                })
            });
            const data = await response.json();

            if (data.response) {
                this.addMessage('assistant', data.response.text);
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            this.addMessage('assistant', '抱歉，网络好像有点问题，等会儿再试试？');
        }
    }

    async startVoiceInput() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            const chunks = [];

            mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
            mediaRecorder.onstop = async () => {
                const blob = new Blob(chunks, { type: 'audio/wav' });
                await this.sendVoiceMessage(blob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setTimeout(() => mediaRecorder.stop(), 5000);
        } catch (error) {
            console.error('Voice input error:', error);
        }
    }

    async sendVoiceMessage(blob) {
        const formData = new FormData();
        formData.append('audio', blob);

        try {
            const response = await fetch(`${this.API_BASE}/voice/input`, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.text) {
                document.getElementById('messageInput').value = data.text;
                this.sendMessage();
            }
        } catch (error) {
            console.error('Failed to process voice:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new TeacherAssistantApp();
});