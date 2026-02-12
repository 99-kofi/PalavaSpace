document.addEventListener('DOMContentLoaded', () => {
    const roomId = window.location.pathname.split('/').pop() || 'street-vibes';
    const socket = io();

    // Serverless Heartbeat: Poll the server to drive the AI loop
    setInterval(() => {
        fetch(`/api/tick/${roomId}`, { method: 'POST' })
            .then(res => res.json())
            .catch(err => console.error("Tick error:", err));
    }, 6000); // Tick every 6 seconds

    const messageFeed = document.getElementById('message-feed');
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    const usernameInput = document.getElementById('username-input');

    // Load saved username
    const savedName = localStorage.getItem('palava_username');
    if (savedName && usernameInput) {
        usernameInput.value = savedName;
    }

    // Save username changes locally
    if (usernameInput) {
        usernameInput.addEventListener('change', () => {
            localStorage.setItem('palava_username', usernameInput.value);
        });
    }

    socket.on('connect', () => {
        console.log('Socket Connected! ID:', socket.id);
        statusText.innerText = 'Server Online';
        statusDot.style.backgroundColor = '#22c55e'; // green
        socket.emit('join', { room_id: roomId });
    });

    socket.on('disconnect', () => {
        statusText.innerText = 'Disconnected';
        statusDot.style.backgroundColor = '#ef4444'; // red
    });

    socket.on('reaction', (data) => {
        console.log('Global reaction:', data.emoji, 'from', data.username);
        showReactionPopup(data.emoji, data.username);
    });

    socket.on('message', (msg) => {
        console.log('Received message:', msg);
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const messageDiv = document.createElement('div');
        messageDiv.className = msg.type === 'info' ? 'info-badge' : 'chat-msg';

        if (msg.type === 'chat') {
            messageDiv.innerHTML = `
                <div class="sender-label">${msg.sender_name || msg.sender}</div>
                <div class="msg-bubble">
                    <p class="msg-content">${msg.content}</p>
                    <span class="msg-time">${time}</span>
                </div>
            `;
        } else {
            messageDiv.innerText = msg.content;
        }

        messageFeed.appendChild(messageDiv);
        messageFeed.scrollTop = messageFeed.scrollHeight;
    });

    // Topic Trigger Demo
    window.triggerTopic = (topic) => {
        socket.emit('trigger_topic', { room_id: roomId, topic: topic });
    };

    // Handle reactions
    document.querySelectorAll('.emoji-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const emoji = btn.innerText;
            const username = document.getElementById('username-input').value || 'Anonymous Paddy';
            console.log('You reacted with:', emoji, 'as', username);
            socket.emit('reaction', { room_id: roomId, emoji: emoji, username: username });
        });
    });

    function showReactionPopup(emoji, username) {
        const popupWrapper = document.createElement('div');
        popupWrapper.className = 'fixed flex flex-col items-center pointer-events-none z-50 animate-bounce';
        popupWrapper.style.left = Math.random() * 80 + 10 + '%';
        popupWrapper.style.bottom = '20%';

        popupWrapper.innerHTML = `
            <span class="text-4xl">${emoji}</span>
            <span class="bg-black/60 backdrop-blur-sm text-[8px] font-black uppercase text-yellow-500 px-2 py-0.5 rounded-full mt-1 border border-yellow-500/20">
                ${username}
            </span>
        `;

        document.body.appendChild(popupWrapper);

        // Custom animation to float up and fade out
        let pos = 20;
        let opacity = 1;
        const id = setInterval(() => {
            if (opacity <= 0) {
                clearInterval(id);
                popupWrapper.remove();
            } else {
                pos += 1.5;
                opacity -= 0.015;
                popupWrapper.style.bottom = pos + '%';
                popupWrapper.style.opacity = opacity;
            }
        }, 30);
    }
});
