// static/js/move_up.js
console.log('move_up.js загружен'); // Для отладки

document.addEventListener('DOMContentLoaded', function() {
    // Ищем CSRF токен
    let csrfToken = '';
    
    // Способ 1: Из скрытого поля
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        csrfToken = csrfInput.value;
        console.log('CSRF найден в скрытом поле:', csrfToken.substring(0, 10) + '...');
    }
    
    if (!csrfToken) {
        console.error('CSRF токен не найден!');
        alert('Ошибка безопасности. Пожалуйста, обновите страницу.');
        return;
    }
    
    console.log('Кнопок move-up:', document.querySelectorAll('.move-up').length);
    console.log('Кнопок move-down:', document.querySelectorAll('.move-down').length);
    
    // Функция отправки запроса на перемещение
    async function moveBoard(boardId, direction) {
        try {
            const url = `/boards/${boardId}/${direction}/`;
            console.log(`Отправка ${direction} для доски ${boardId}`);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            console.log('Статус ответа:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Ответ сервера:', data);
                
                if (data.success) {
                    // Показываем сообщение об успехе
                    if (data.message) {
                        alert(data.message);
                    }
                    // Перезагружаем страницу для обновления порядка
                    setTimeout(() => {
                        location.reload();
                    }, 500);
                } else {
                    alert(data.message || 'Не удалось переместить доску');
                }
            } else {
                try {
                    const errorData = await response.json();
                    alert('Ошибка: ' + (errorData.error || errorData.message || 'Неизвестная ошибка'));
                } catch {
                    alert(`Ошибка ${response.status}: ${response.statusText}`);
                }
            }
        } catch (error) {
            console.error('Ошибка соединения:', error);
            alert('Ошибка соединения с сервером. Проверьте интернет-соединение.');
        }
    }
    
    // Обработчики для кнопок "вверх"
    document.querySelectorAll('.move-up').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const boardId = this.dataset.boardId;
            console.log('Клик по move-up для доски:', boardId);
            moveBoard(boardId, 'move-up');
        });
    });
    
    // Обработчики для кнопок "вниз"
    document.querySelectorAll('.move-down').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const boardId = this.dataset.boardId;
            console.log('Клик по move-down для доски:', boardId);
            moveBoard(boardId, 'move-down');
        });
    });
    
    // Стили для кнопок (опционально)
    const style = document.createElement('style');
    style.textContent = `
        .move-up, .move-down {
            cursor: pointer;
            transition: background-color 0.2s;
            padding: 5px 10px;
            margin: 0 2px;
            border: 1px solid #ccc;
            border-radius: 3px;
            background: #f0f0f0;
        }
        .move-up:hover, .move-down:hover {
            background-color: #e0e0e0;
        }
        .move-up:active, .move-down:active {
            background-color: #d0d0d0;
        }
    `;
    document.head.appendChild(style);
});