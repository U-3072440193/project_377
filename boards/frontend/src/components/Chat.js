// boards/frontend/src/components/Chat.js - ЗАМЕНИТЕ НА ЭТОТ КОД
import React, { useState, useEffect } from 'react';

const Chat = ({ boardId, currentUser, serverUrl = '', csrfToken }) => {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Загрузка истории
    useEffect(() => {
        loadHistory();
    }, [boardId]);

    const loadHistory = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(
                `${serverUrl}api/chat/boards/${boardId}/history/`
            );
            const data = await response.json();
            setMessages(data.messages || []);
            console.log('Загружены сообщения:', data.messages);
        } catch (error) {
            console.error('Ошибка загрузки:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const sendMessage = async () => {
        const text = inputText.trim();
        if (!text) return;

        try {
            const response = await fetch(
                `${serverUrl}api/chat/boards/${boardId}/send/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ text }),
                }
            );

            if (response.ok) {
                const newMessage = await response.json();
                setMessages([...messages, newMessage]);
                setInputText('');
                console.log('Отправлено сообщение:', newMessage);
            }
        } catch (error) {
            console.error('Ошибка отправки:', error);
        }
    };

    // Простой рендеринг БЕЗ сложной логики
    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h3 style={{margin: 0}}>💬 Чат доски #{boardId}</h3>
                <div style={styles.status}>
                    {isLoading ? 'Загрузка...' : `Сообщений: ${messages.length}`}
                </div>
            </div>

            <div style={styles.messages}>
                {messages.map((msg) => (
                    <div key={msg.id} style={styles.message}>
                        <div style={styles.messageHeader}>
                            <strong>{msg.author?.username}</strong>
                            <span style={styles.time}>{msg.created_display}</span>
                        </div>
                        <div style={styles.messageText}>{msg.text}</div>
                    </div>
                ))}
            </div>

            <div style={styles.inputContainer}>
                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Введите сообщение..."
                    style={styles.input}
                />
                <button 
                    onClick={sendMessage}
                    disabled={!inputText.trim()}
                    style={styles.button}
                >
                    Отправить
                </button>
            </div>
        </div>
    );
};

// Inline стили - не нужен CSS файл
const styles = {
    container: {
        border: '1px solid #ddd',
        borderRadius: '8px',
        background: 'white',
        height: '500px',
        display: 'flex',
        flexDirection: 'column',
    },
    header: {
        padding: '15px',
        background: '#f5f5f5',
        borderBottom: '1px solid #ddd',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    status: {
        padding: '5px 10px',
        background: '#e9ecef',
        borderRadius: '4px',
        fontSize: '14px',
    },
    messages: {
        flex: 1,
        overflowY: 'auto',
        padding: '15px',
    },
    message: {
        marginBottom: '15px',
        padding: '10px',
        background: '#f9f9f9',
        borderRadius: '5px',
    },
    messageHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: '5px',
    },
    messageText: {
        fontSize: '15px',
    },
    time: {
        color: '#666',
        fontSize: '12px',
    },
    inputContainer: {
        padding: '15px',
        borderTop: '1px solid #ddd',
        display: 'flex',
        gap: '10px',
    },
    input: {
        flex: 1,
        padding: '8px',
        border: '1px solid #ddd',
        borderRadius: '4px',
        fontSize: '14px',
    },
    button: {
        padding: '8px 20px',
        background: '#333',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '14px',
    },
};

export default Chat;