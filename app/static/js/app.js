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
        this.addWelcomeMessage();
        this.initTextarea();
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
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.switchMode(mode);
            });
        });

        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keydown', (e) => this.handleKeydown(e));

        document.getElementById('voiceBtn').addEventListener('click', () => this.startVoiceInput());

        document.getElementById('closeSidebar').addEventListener('click', () => {
            document.getElementById('sidebarPanel').classList.add('hidden');
        });

        document.querySelector('.action-btn').addEventListener('click', () => this.clearChat());
    }

    initTextarea() {
        const textarea = document.getElementById('messageInput');
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
        });
    }

    handleKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    switchMode(mode) {
        this.currentMode = mode;
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        this.updateSidebar(mode);
    }

    updateSidebar(mode) {
        const sidebar = document.getElementById('sidebarPanel');
        const sidebarContent = document.getElementById('sidebarContent');
        const sidebarTitle = document.getElementById('sidebarTitle');

        switch (mode) {
            case 'chat':
                sidebar.classList.add('hidden');
                break;
            case 'teaching':
                sidebar.classList.remove('hidden');
                sidebarTitle.textContent = '教学模式';
                sidebarContent.innerHTML = `
                    <div class="form-group">
                        <label>教学主题</label>
                        <input type="text" id="teachingTopic" placeholder="例如：分数的认识">
                    </div>
                    <div class="form-group">
                        <label>教学大纲</label>
                        <textarea id="teachingOutline" placeholder="每行为一个知识点，例如：\n1. 分数的概念\n2. 分数的读写\n3. 分数的比较"></textarea>
                    </div>
                    <button class="submit-btn" onclick="app.startTeaching()">开始教学</button>
                `;
                break;
            case 'lesson':
                sidebar.classList.remove('hidden');
                sidebarTitle.textContent = '备课模式';
                sidebarContent.innerHTML = `
                    <div class="form-group">
                        <label>年级</label>
                        <select id="lessonGrade">
                            <option value="1">一年级</option>
                            <option value="2">二年级</option>
                            <option value="3">三年级</option>
                            <option value="4">四年级</option>
                            <option value="5">五年级</option>
                            <option value="6">六年级</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>学科</label>
                        <select id="lessonSubject">
                            <option value="chinese">语文</option>
                            <option value="math">数学</option>
                            <option value="english">英语</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>课题</label>
                        <input type="text" id="lessonTopic" placeholder="例如：分数的认识">
                    </div>
                    <div class="form-group">
                        <label>课时</label>
                        <input type="text" id="lessonDuration" placeholder="例如：40分钟" value="40分钟">
                    </div>
                    <button class="submit-btn" onclick="app.generateLessonPlan()">生成教案</button>
                    <div id="lessonResult" class="result-container" style="display: none;"></div>
                `;
                break;
        }
    }

    addWelcomeMessage() {
        this.addMessage('assistant', '同学们好！我是小慧老师，有什么问题尽管问我哦～');
    }

    addMessage(role, content) {
        const messagesList = document.getElementById('messagesList');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'assistant' ? '👩‍🏫' : '👨‍🎓';

        const contentWrapper = document.createElement('div');

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());

        contentWrapper.appendChild(messageContent);
        contentWrapper.appendChild(messageTime);

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

    clearChat() {
        const messagesList = document.getElementById('messagesList');
        messagesList.innerHTML = '';
        this.addWelcomeMessage();
    }

    async sendMessage() {
        const textarea = document.getElementById('messageInput');
        const text = textarea.value.trim();
        if (!text) return;

        this.addMessage('user', text);
        textarea.value = '';
        textarea.style.height = 'auto';

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

    async startTeaching() {
        const topic = document.getElementById('teachingTopic').value.trim();
        const outlineText = document.getElementById('teachingOutline').value.trim();
        const outline = outlineText.split('\n').filter(line => line.trim());

        if (!topic || outline.length === 0) {
            alert('请输入教学主题和大纲');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE}/chat/teaching`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    topic: topic,
                    outline: outline
                })
            });
            const data = await response.json();

            if (data.response) {
                this.switchMode('chat');
                this.addMessage('assistant', data.response.text);
            }
        } catch (error) {
            console.error('Failed to start teaching:', error);
        }
    }

    async generateLessonPlan() {
        const grade = document.getElementById('lessonGrade').value;
        const subject = document.getElementById('lessonSubject').value;
        const topic = document.getElementById('lessonTopic').value.trim();
        const duration = document.getElementById('lessonDuration').value.trim();

        if (!topic) {
            alert('请输入课题');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE}/lesson/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    grade: parseInt(grade),
                    subject: subject,
                    topic: topic,
                    duration: duration
                })
            });
            const data = await response.json();

            if (data.success) {
                const resultDiv = document.getElementById('lessonResult');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `
                    <h4>📚 生成的教案</h4>
                    <pre>${JSON.stringify(data.plan, null, 2)}</pre>
                `;
                this.switchMode('chat');
                this.addMessage('assistant', `教案已生成！主题：${topic}`);
            }
        } catch (error) {
            console.error('Failed to generate lesson plan:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new TeacherAssistantApp();
});