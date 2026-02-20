import React, { useState, useEffect, useRef } from 'react';

const PrivateMessages = ({ currentUser, serverUrl, csrfToken, onClose }) => {
    const [dialogs, setDialogs] = useState([]);
    const [activeDialog, setActiveDialog] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [showNewChat, setShowNewChat] = useState(false);
    const [users, setUsers] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [ws, setWs] = useState(null);
    const messagesEndRef = useRef(null);

    // Подключение к WebSocket
    useEffect(() => {
        if (!currentUser?.isAuthenticated) return;

        const websocket = new WebSocket(`ws://127.0.0.1:8000/ws/private/`);
        
        websocket.onopen = () => {
            console.log('WebSocket connected');
        };
        
        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'new_message') {
                const newMessage = data.message;
                
                // Если сообщение из текущего чата - добавляем
                if (activeDialog === newMessage.chat_id) {
                    setMessages(prev => [...prev, newMessage]);
                }
                
                // Обновляем список диалогов
                loadDialogs();
            }
        };
        
        websocket.onclose = () => {
            console.log('WebSocket disconnected');
        };
        
        setWs(websocket);
        
        return () => {
            websocket.close();
        };
    }, [currentUser, activeDialog]); // добавили activeDialog в зависимости

    // Загрузка списка диалогов
    useEffect(() => {
        loadDialogs();
    }, []);

    // Скролл к последнему сообщению
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadDialogs = async () => {
        try {
            const response = await fetch(`${serverUrl}api/chat/my-dialogs/`, {
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include'
            });
            const data = await response.json();
            setDialogs(data || []);
        } catch (error) {
            console.error('Ошибка загрузки диалогов:', error);
        }
    };

    const loadMessages = async (chatId) => {
        try {
            setIsLoading(true);
            const response = await fetch(`${serverUrl}api/chat/dialog/${chatId}/messages/`, {
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include'
            });
            const data = await response.json();
            setMessages(data || []);
            setActiveDialog(chatId);
            
            // Обновляем список диалогов (для сброса счетчика)
            loadDialogs();
        } catch (error) {
            console.error('Ошибка загрузки сообщений:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Отправка через REST (запасной вариант)
    const sendMessageViaREST = async () => {
        if (!inputText.trim() || !activeDialog) return;
        
        try {
            const response = await fetch(`${serverUrl}api/chat/dialog/${activeDialog}/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
                body: JSON.stringify({ text: inputText }),
            });
            
            if (response.ok) {
                const newMessage = await response.json();
                setMessages([...messages, newMessage]);
                setInputText('');
                
                // Обновляем список диалогов (для последнего сообщения)
                loadDialogs();
            }
        } catch (error) {
            console.error('Ошибка отправки:', error);
        }
    };

    // Отправка через WebSocket
    const sendMessageViaWebSocket = () => {
        if (!inputText.trim() || !activeDialog || !ws) return;
        
        // Находим получателя
        const dialog = dialogs.find(d => d.id === activeDialog);
        if (!dialog) return;
        
        const recipient_id = dialog.other_user.id;
        
        ws.send(JSON.stringify({
            type: 'private_message',
            recipient_id: recipient_id,
            text: inputText
        }));
        
        setInputText('');
    };

    // Основная функция отправки
    const sendMessage = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            sendMessageViaWebSocket();
        } else {
            sendMessageViaREST();
        }
    };

    const searchUsers = async (term) => {
        if (term.length < 2) {
            setUsers([]);
            return;
        }
        
        try {
            const response = await fetch(`${serverUrl}api/chat/search-users/?q=${term}`, {
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include'
            });
            const data = await response.json();
            setUsers(data || []);
        } catch (error) {
            console.error('Ошибка поиска:', error);
        }
    };

    const startNewChat = async (userId) => {
        try {
            const response = await fetch(`${serverUrl}api/chat/create-dialog/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
                body: JSON.stringify({ user_id: userId }),
            });
            
            if (response.ok) {
                const data = await response.json();
                setShowNewChat(false);
                setSearchTerm('');
                setUsers([]);
                await loadDialogs();
                await loadMessages(data.chat_id);
            }
        } catch (error) {
            console.error('Ошибка создания чата:', error);
        }
    };

    const formatTime = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div style={styles.container}>
            {/* Левая панель - список диалогов */}
            <div style={styles.dialogsPanel}>
                <div style={styles.panelHeader}>
                    <h3 style={styles.panelTitle}>Мессенджер</h3>
                    <button 
                        onClick={() => setShowNewChat(!showNewChat)}
                        style={styles.newChatBtn}
                        title="Новый чат"
                    >
                        ✏️
                    </button>
                </div>

                {/* Поиск нового чата */}
                {showNewChat && (
                    <div style={styles.searchContainer}>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value);
                                searchUsers(e.target.value);
                            }}
                            placeholder="Поиск пользователей..."
                            style={styles.searchInput}
                            autoFocus
                        />
                        {users.length > 0 && (
                            <div style={styles.searchResults}>
                                {users.map(user => (
                                    <div
                                        key={user.id}
                                        style={styles.userItem}
                                        onClick={() => startNewChat(user.id)}
                                    >
                                        <div style={styles.userAvatar}>
                                            {user.username[0].toUpperCase()}
                                        </div>
                                        <span>{user.username}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Список диалогов */}
                <div style={styles.dialogsList}>
                    {dialogs.map(dialog => (
                        <div
                            key={dialog.id}
                            style={{
                                ...styles.dialogItem,
                                ...(activeDialog === dialog.id ? styles.activeDialog : {})
                            }}
                            onClick={() => loadMessages(dialog.id)}
                        >
                            <div style={styles.dialogAvatar}>
                                {dialog.other_user.username[0].toUpperCase()}
                            </div>
                            <div style={styles.dialogInfo}>
                                <div style={styles.dialogHeader}>
                                    <span style={styles.dialogName}>
                                        {dialog.other_user.username}
                                    </span>
                                    {dialog.last_message_time && (
                                        <span style={styles.dialogTime}>
                                            {formatTime(dialog.last_message_time)}
                                        </span>
                                    )}
                                </div>
                                <div style={styles.dialogLastMessage}>
                                    {dialog.last_message || 'Нет сообщений'}
                                </div>
                            </div>
                            {dialog.unread_count > 0 && (
                                <div style={styles.unreadBadge}>
                                    {dialog.unread_count}
                                </div>
                            )}
                        </div>
                    ))}
                    {dialogs.length === 0 && !showNewChat && (
                        <div style={styles.emptyDialogs}>
                            <p>Нет диалогов</p>
                            <button 
                                onClick={() => setShowNewChat(true)}
                                style={styles.startChatBtn}
                            >
                                Написать кому-нибудь
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Правая панель - переписка */}
            <div style={styles.chatPanel}>
                {activeDialog ? (
                    <>
                        <div style={styles.messagesArea}>
                            {messages.map((msg, index) => {
                                const isMyMessage = msg.sender_id === currentUser.id;
                                const showAvatar = index === 0 || 
                                    messages[index - 1]?.sender_id !== msg.sender_id;
                                
                                return (
                                    <div
                                        key={msg.id}
                                        style={{
                                            ...styles.messageWrapper,
                                            ...(isMyMessage ? styles.myMessageWrapper : {})
                                        }}
                                    >
                                        {!isMyMessage && showAvatar && (
                                            <div style={styles.messageAvatar}>
                                                {msg.sender_name[0].toUpperCase()}
                                            </div>
                                        )}
                                        <div style={{
                                            ...styles.messageBubble,
                                            ...(isMyMessage ? styles.myMessageBubble : {}),
                                            ...(!showAvatar && !isMyMessage ? styles.messageBubbleGrouped : {})
                                        }}>
                                            {!isMyMessage && !showAvatar && (
                                                <div style={styles.messageSender}>
                                                    {msg.sender_name}
                                                </div>
                                            )}
                                            <div style={styles.messageText}>{msg.text}</div>
                                            <div style={styles.messageTime}>
                                                {formatTime(msg.created)}
                                                {isMyMessage && (
                                                    <span style={styles.messageStatus}>
                                                        {msg.is_read ? ' ✓✓' : ' ✓'}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                            <div ref={messagesEndRef} />
                            {isLoading && (
                                <div style={styles.loading}>Загрузка...</div>
                            )}
                        </div>

                        <div style={styles.inputArea}>
                            <input
                                type="text"
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                                placeholder="Введите сообщение..."
                                style={styles.messageInput}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={!inputText.trim()}
                                style={{
                                    ...styles.sendButton,
                                    ...(!inputText.trim() ? styles.sendButtonDisabled : {})
                                }}
                            >
                                Отправить
                            </button>
                        </div>
                    </>
                ) : (
                    <div style={styles.noChat}>
                        <p>Выберите диалог</p>
                        <p style={styles.noChatSub}>или создайте новый</p>
                    </div>
                )}
            </div>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        width: '100%',
        height: '100%',
        background: 'white',
        borderRadius: '8px',
        overflow: 'hidden',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    },
    dialogsPanel: {
        width: '35%',
        borderRight: '1px solid #e0e0e0',
        display: 'flex',
        flexDirection: 'column',
        background: '#f8f9fa',
    },
    panelHeader: {
        padding: '16px',
        background: 'white',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    panelTitle: {
        margin: 0,
        fontSize: '18px',
        fontWeight: 600,
        color: '#1a1a1a',
    },
    newChatBtn: {
        width: '36px',
        height: '36px',
        borderRadius: '50%',
        border: 'none',
        background: '#f0f2f5',
        cursor: 'pointer',
        fontSize: '18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'background 0.2s',
        ':hover': {
            background: '#e4e6e9',
        },
    },
    searchContainer: {
        padding: '12px',
        borderBottom: '1px solid #e0e0e0',
        background: 'white',
    },
    searchInput: {
        width: '100%',
        padding: '10px 12px',
        border: '1px solid #e0e0e0',
        borderRadius: '20px',
        fontSize: '14px',
        outline: 'none',
        ':focus': {
            borderColor: '#333',
        },
    },
    searchResults: {
        marginTop: '8px',
        maxHeight: '200px',
        overflowY: 'auto',
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    },
    userItem: {
        display: 'flex',
        alignItems: 'center',
        padding: '10px 12px',
        cursor: 'pointer',
        transition: 'background 0.2s',
        ':hover': {
            background: '#f0f2f5',
        },
    },
    dialogsList: {
        flex: 1,
        overflowY: 'auto',
    },
    dialogItem: {
        display: 'flex',
        padding: '12px',
        cursor: 'pointer',
        borderBottom: '1px solid #f0f0f0',
        transition: 'background 0.2s',
        alignItems: 'center',
        ':hover': {
            background: '#f0f2f5',
        },
    },
    activeDialog: {
        background: '#e8f0fe',
        ':hover': {
            background: '#e8f0fe',
        },
    },
    dialogAvatar: {
        width: '48px',
        height: '48px',
        borderRadius: '50%',
        background: '#333',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '18px',
        fontWeight: 600,
        marginRight: '12px',
        flexShrink: 0,
    },
    dialogInfo: {
        flex: 1,
        minWidth: 0,
    },
    dialogHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '4px',
    },
    dialogName: {
        fontWeight: 600,
        fontSize: '14px',
        color: '#1a1a1a',
    },
    dialogTime: {
        fontSize: '11px',
        color: '#999',
    },
    dialogLastMessage: {
        fontSize: '13px',
        color: '#666',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
    },
    unreadBadge: {
        background: '#ff4444',
        color: 'white',
        borderRadius: '12px',
        padding: '2px 8px',
        fontSize: '12px',
        fontWeight: 600,
        marginLeft: '8px',
        minWidth: '20px',
        textAlign: 'center',
    },
    emptyDialogs: {
        padding: '32px 16px',
        textAlign: 'center',
        color: '#999',
    },
    startChatBtn: {
        padding: '8px 16px',
        background: '#333',
        color: 'white',
        border: 'none',
        borderRadius: '20px',
        cursor: 'pointer',
        marginTop: '12px',
        fontSize: '14px',
    },
    chatPanel: {
        width: '65%',
        display: 'flex',
        flexDirection: 'column',
        background: '#f0f2f5',
    },
    messagesArea: {
        flex: 1,
        padding: '20px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
    },
    messageWrapper: {
        display: 'flex',
        marginBottom: '8px',
        alignItems: 'flex-end',
    },
    myMessageWrapper: {
        justifyContent: 'flex-end',
    },
    messageAvatar: {
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        background: '#333',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '14px',
        fontWeight: 600,
        marginRight: '8px',
        flexShrink: 0,
    },
    messageBubble: {
        maxWidth: '60%',
        padding: '8px 12px',
        background: 'white',
        borderRadius: '16px',
        position: 'relative',
        boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
    },
    messageBubbleGrouped: {
        marginLeft: '40px',
    },
    myMessageBubble: {
        background: '#333',
        color: 'white',
    },
    messageSender: {
        fontSize: '12px',
        fontWeight: 600,
        color: '#666',
        marginBottom: '2px',
    },
    messageText: {
        fontSize: '14px',
        wordWrap: 'break-word',
    },
    messageTime: {
        fontSize: '10px',
        color: '#999',
        marginTop: '4px',
        textAlign: 'right',
    },
    messageStatus: {
        color: '#4CAF50',
        marginLeft: '4px',
    },
    loading: {
        textAlign: 'center',
        padding: '20px',
        color: '#999',
    },
    inputArea: {
        padding: '16px',
        background: 'white',
        borderTop: '1px solid #e0e0e0',
        display: 'flex',
        gap: '12px',
    },
    messageInput: {
        flex: 1,
        padding: '12px 16px',
        border: '1px solid #e0e0e0',
        borderRadius: '24px',
        fontSize: '14px',
        outline: 'none',
        ':focus': {
            borderColor: '#333',
        },
    },
    sendButton: {
        padding: '12px 24px',
        background: '#333',
        color: 'white',
        border: 'none',
        borderRadius: '24px',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: 500,
        transition: 'background 0.2s',
        ':hover': {
            background: '#444',
        },
    },
    sendButtonDisabled: {
        background: '#ccc',
        cursor: 'not-allowed',
        ':hover': {
            background: '#ccc',
        },
    },
    noChat: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        color: '#999',
        fontSize: '16px',
    },
    noChatSub: {
        fontSize: '14px',
        color: '#ccc',
        marginTop: '8px',
    },
};

export default PrivateMessages;