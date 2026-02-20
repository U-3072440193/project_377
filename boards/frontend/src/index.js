import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/style.css';
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import PrivateMessages from './components/PrivateMessages';

// === 1. Рендерим основное приложение (доски), ТОЛЬКО если есть элемент #root ===
const rootElement = document.getElementById('root');
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(
        <React.StrictMode>
            <BrowserRouter>
                <App />
            </BrowserRouter>
        </React.StrictMode>
    );
} else {
    console.log('Элемент #root не найден - основное React-приложение не будет смонтировано');
}

// === 2. Рендерим мессенджер, если есть элемент #private-chat-root ===
const chatElement = document.getElementById('private-chat-root');
if (chatElement) {
    const props = window.PRIVATE_CHAT_PROPS || {};
    
    // Рендерим только для авторизованных
    if (props.currentUser?.isAuthenticated) {
        const chatRoot = ReactDOM.createRoot(chatElement);
        chatRoot.render(
            <React.StrictMode>
                <PrivateMessages
                    currentUser={props.currentUser}
                    serverUrl={props.serverUrl}
                    csrfToken={props.csrfToken}
                />
            </React.StrictMode>
        );
    }
}