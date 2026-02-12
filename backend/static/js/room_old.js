document.addEventListener('DOMContentLoaded', () => {
    const roomId = window.location.pathname.split('/').pop();
    const socket = io();

    const messageFeed = document.getElementById('message-feed');
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');

    socket.on('connect', () => {
        console.log('Socket Connected! ID:', socket.id);
        statusText.innerText = 'Server Online';
        statusDot.classList.remove('bg-red');
        statusDot.classList.add('bg-green');
        socket.emit('join', { room_id: roomId });
    });

    socket.on('disconnect', () => {
        statusText.innerText = 'Disconnected';
        statusDot.classList.remove('bg-green');
        statusDot.classList.add('bg-red');
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

    // Handle reactions locally for now or emit if needed
    document.querySelectorAll('.emoji-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const emoji = btn.innerText;
            console.log('Reacted with:', emoji);
            // socket.emit('reaction', { emoji, room_id: roomId });
        });
    });
});
