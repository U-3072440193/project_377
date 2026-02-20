import React from 'react';
import { createRoot } from 'react-dom/client';
import Chat from './components/Chat'; // Переиспользуем тот же компонент

// Функция для запуска чата, которую вызовем из Django-шаблона
export function initGeneralChat(containerId, props) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container #${containerId} not found`);
    return;
  }
  const root = createRoot(container);
  root.render(
    <Chat
      roomType="general"       // Укажем, что это общий чат
      currentUser={props.currentUser}
      serverUrl={props.serverUrl}
      csrfToken={props.csrfToken}
      
    />
  );
}

// Делаем функцию доступной глобально, чтобы её можно было вызвать из шаблона
//npm install @craco/craco --save-dev
window.initGeneralChat = initGeneralChat;