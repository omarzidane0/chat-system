const appShell = document.getElementById('appShell');
const messages = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const conversationList = document.getElementById('conversationList');
const newConversationDialog = document.getElementById('newConversationDialog');
const contactList = document.getElementById('contactList');
const selectedCount = document.getElementById('selectedCount');
const createConversationButton = document.getElementById('createConversation');
const currentUserId = Number(appShell.dataset.currentUserId);
const messagesByConversation = new Map();
let activeConversationId = document.querySelector('.conversation.active')?.dataset.conversationId ?? null;
let socket;

const formatTime = (value) => new Intl.DateTimeFormat('ar', { hour: 'numeric', minute: '2-digit' }).format(new Date(value));
const getCookie = (name) => document.cookie.split('; ').find((item) => item.startsWith(`${name}=`))?.split('=').slice(1).join('=');

const renderMessages = () => {
	messages.replaceChildren();
	const conversationMessages = messagesByConversation.get(activeConversationId) || [];
	if (!conversationMessages.length) return;

	const divider = document.createElement('div');
	divider.className = 'date-divider';
	divider.textContent = 'الرسائل';
	messages.append(divider);
	conversationMessages.forEach((item) => {
		const row = document.createElement('div');
		row.className = `message-row ${item.sender_id === currentUserId ? 'mine' : 'theirs'}`;
		const bubble = document.createElement('div');
		bubble.className = 'message';
		bubble.textContent = item.content;
		const time = document.createElement('span');
		time.className = 'message-time';
		time.textContent = formatTime(item.created_at);
		bubble.append(time);
		row.append(bubble);
		messages.append(row);
	});
	messages.scrollTop = messages.scrollHeight;
};

const updateConversationPreview = (item) => {
	const conversation = conversationList.querySelector(`[data-conversation-id="${item.conversation_id}"]`);
	if (!conversation) return;
	conversation.querySelector('.last-message').textContent = `${item.sender_id === currentUserId ? 'أنت: ' : `${item.sender}: `}${item.content}`;
	conversation.querySelector('.time').textContent = formatTime(item.created_at);
	conversationList.prepend(conversation);
};

const receiveMessage = (item) => {
	const conversationId = String(item.conversation_id);
	const items = messagesByConversation.get(conversationId) || [];
	if (items.some((existing) => existing.id === item.id)) return;
	items.push(item);
	items.sort((left, right) => new Date(left.created_at) - new Date(right.created_at) || left.id - right.id);
	messagesByConversation.set(conversationId, items);
	updateConversationPreview(item);
	if (conversationId === activeConversationId) renderMessages();
};

const connectSocket = () => {
	const scheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	socket = new WebSocket(`${scheme}//${window.location.host}/ws/conversations/`);
	socket.addEventListener('open', () => { document.getElementById('chatStatus').textContent = 'متصل'; });
	socket.addEventListener('message', (event) => {
		const payload = JSON.parse(event.data);
		if (payload.type === 'sync') {
			payload.messages.forEach(receiveMessage);
			renderMessages();
		} else if (payload.type === 'message') {
			receiveMessage(payload.message);
		} else if (payload.type === 'error') {
			document.getElementById('chatStatus').textContent = payload.message;
		}
	});
	socket.addEventListener('close', (event) => {
		document.getElementById('chatStatus').textContent = 'انقطع الاتصال';
		if (event.code !== 4401) window.setTimeout(connectSocket, 1500);
	});
};

const updateSelectedCount = () => {
	const count = contactList.querySelectorAll('input:checked').length;
	selectedCount.textContent = count ? `تم اختيار ${count} أشخاص` : 'لم يتم اختيار أشخاص';
	createConversationButton.disabled = count === 0;
};

document.getElementById('openNewConversation').addEventListener('click', () => newConversationDialog.showModal());
document.getElementById('closeNewConversation').addEventListener('click', () => newConversationDialog.close());
contactList.addEventListener('change', updateSelectedCount);
document.getElementById('contactSearch').addEventListener('input', (event) => {
	const query = event.target.value.trim().toLocaleLowerCase('ar');
	contactList.querySelectorAll('.contact-option').forEach((option) => {
		option.hidden = !option.dataset.name.toLocaleLowerCase('ar').includes(query);
	});
});

document.getElementById('newConversationForm').addEventListener('submit', async (event) => {
	event.preventDefault();
	const participantIds = [...contactList.querySelectorAll('input:checked')].map((checkbox) => checkbox.value);
	if (!participantIds.length) return;
	const response = await fetch('/conversations/create/', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
		body: JSON.stringify({ participant_ids: participantIds }),
	});
	if (response.ok) window.location.reload();
	else selectedCount.textContent = (await response.json()).error || 'تعذر إنشاء المحادثة.';
});

document.getElementById('conversationSearch').addEventListener('input', (event) => {
	const query = event.target.value.trim().toLocaleLowerCase('ar');
	conversationList.querySelectorAll('.conversation').forEach((conversation) => {
		conversation.hidden = !conversation.dataset.name.toLocaleLowerCase('ar').includes(query);
	});
});

conversationList.addEventListener('click', (event) => {
	const conversation = event.target.closest('.conversation');
	if (!conversation) return;
	document.querySelector('.conversation.active')?.classList.remove('active');
	conversation.classList.add('active');
	activeConversationId = conversation.dataset.conversationId;
	document.getElementById('chatName').textContent = conversation.dataset.name;
	document.getElementById('chatStatus').textContent = socket?.readyState === WebSocket.OPEN ? 'متصل' : 'جارٍ الاتصال';
	const avatar = document.getElementById('headerAvatar');
	avatar.className = `avatar ${conversation.dataset.color}`.trim();
	avatar.textContent = conversation.dataset.initials;
	renderMessages();
	appShell.classList.remove('show-sidebar');
});

document.getElementById('backToList').addEventListener('click', () => appShell.classList.add('show-sidebar'));
document.getElementById('messageForm').addEventListener('submit', (event) => {
	event.preventDefault();
	const text = messageInput.value.trim();
	if (!text || !activeConversationId || socket?.readyState !== WebSocket.OPEN) return;
	socket.send(JSON.stringify({ type: 'send', conversation_id: activeConversationId, content: text }));
	messageInput.value = '';
	messageInput.focus();
});

connectSocket();
if (activeConversationId) renderMessages();