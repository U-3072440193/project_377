// Функция для получения CSRF токена
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Функция для преобразования роли в читаемый вид
function getRoleName(role) {
    const roleNames = {
        'owner': 'Владелец',
        'member': 'Участник',
        'viewer': 'Наблюдатель',
        'admin': 'Администратор'
    };
    return roleNames[role] || role;
}

document.addEventListener("DOMContentLoaded", function () {
    // === поиск пользователей ===
    document.querySelectorAll(".email-compose").forEach((form) => {
        const boardId = form.dataset.boardId?.trim();
        const input = document.getElementById(`recipient-${boardId}`);
        const suggestions = document.getElementById(`suggestions-${boardId}`);
        const recipientIdField = document.getElementById(
            `recipient_id-${boardId}`
        );
        if (!input || !suggestions || !recipientIdField) return;

        // URL для поиска пользователей - будет передан через data-атрибут
        const searchUrl = form.dataset.searchUrl || '/api/search-users/';

        input.addEventListener("input", function () {
            const query = this.value.trim();
            if (!query) {
                suggestions.innerHTML = "";
                recipientIdField.value = "";
                return;
            }

            fetch(`${searchUrl}?search=${encodeURIComponent(query)}`)
                .then((res) => res.json())
                .then((data) => {
                    let html = "";
                    if (!data.length)
                        html = '<div class="no-suggestions">Нет пользователей</div>';
                    else
                        data.forEach((user) => {
                            html += `<div class="suggest-item" data-id="${user.id}" data-name="${user.username}">
                                          ${user.username}
                                       </div>`;
                        });
                    suggestions.innerHTML = html;
                })
                .catch((error) => {
                    console.error('Ошибка поиска пользователей:', error);
                    suggestions.innerHTML = '<div class="no-suggestions">Ошибка поиска</div>';
                });
        });

        suggestions.addEventListener("click", function (e) {
            const item = e.target.closest(".suggest-item");
            if (!item) return;
            input.value = item.dataset.name;
            recipientIdField.value = item.dataset.id;
            suggestions.innerHTML = "";
        });

        form.addEventListener("submit", function (e) {
            if (!recipientIdField.value) {
                e.preventDefault();
                alert("Вы должны выбрать пользователя из списка");
            }
        });
    });

    // === показ участников доски ===
    document.querySelectorAll(".toggle-users").forEach((button) => {
        const boardId = button.dataset.boardId;
        const usersDiv = document.getElementById(`users-${boardId}`);
        const boardContainer = button.closest('.board-container');
        const boardOwnerId = parseInt(boardContainer.dataset.boardOwnerId);

        // Получаем ID текущего пользователя из data-атрибута
        const currentUserId = parseInt(button.dataset.currentUserId || document.body.dataset.currentUserId || "0");

        button.addEventListener("click", async () => {
            usersDiv.hidden = !usersDiv.hidden;

            // Меняем стрелку
            const arrow = button.querySelector('.arrow');
            if (arrow) {
                arrow.textContent = usersDiv.hidden ? '▼' : '▲';
            }

            if (!usersDiv.dataset.loaded) {
                try {
                    // Показываем загрузку
                    usersDiv.innerHTML = '<div class="loading-users">Загрузка участников...</div>';

                    // Получаем список участников доски
                    const response = await fetch(`/api/boards/${boardId}/members/`);

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const users = await response.json();

                    // Проверяем, является ли текущий пользователь владельцем доски
                    const isOwner = boardOwnerId === currentUserId;

                    // Формируем HTML для списка участников
                    let usersHTML = '';

                    if (users.length === 0) {
                        usersHTML = '<div class="no-users">Нет участников</div>';
                    } else {
                        usersHTML = users
                            .map(
                                (user) => `
                                    <div class="board-user" data-user-id="${user.id}">
                                        <img src="${user.avatar || '/static/images/default-avatar.png'}"
                                             alt="${user.username}"
                                             width="32"
                                             height="32"
                                             onerror="this.src='/static/images/default-avatar.png'">
                                        <span class="user-info">
                                            <strong>${user.username}</strong>
                                            <span class="user-role">(${getRoleName(user.role)})</span>
                                        </span>
                                        ${isOwner && user.id !== boardOwnerId ?
                                        `<button class="remove-user"
                                                data-user-id="${user.id}"
                                                title="Удалить участника">×</button>`
                                        : ''}
                                    </div>`
                            )
                            .join('');
                    }

                    usersDiv.innerHTML = usersHTML;

                    // Добавляем обработчики удаления только если есть кнопки
                    usersDiv.querySelectorAll(".remove-user").forEach((btn) => {
                        btn.addEventListener("click", async function (e) {
                            e.stopPropagation();

                            const userId = this.dataset.userId;
                            const userName = this.closest('.board-user').querySelector('strong').textContent;

                            // Подтверждение удаления
                            if (!confirm(`Вы уверены, что хотите удалить участника ${userName}?`)) {
                                return;
                            }

                            try {
                                const response = await fetch(
                                    `/api/boards/${boardId}/remove-member/`,
                                    {
                                        method: "POST",
                                        headers: {
                                            "Content-Type": "application/json",
                                            "X-CSRFToken": getCSRFToken(),
                                        },
                                        body: JSON.stringify({ user_id: userId }),
                                    }
                                );

                                if (response.ok) {
                                    // Удаляем пользователя из DOM
                                    const userElement = this.closest('.board-user');
                                    userElement.style.opacity = '0.5';

                                    setTimeout(() => {
                                        userElement.remove();

                                        // Если список пуст, показываем сообщение
                                        const remainingUsers = usersDiv.querySelectorAll('.board-user');
                                        if (remainingUsers.length === 0) {
                                            usersDiv.innerHTML = '<div class="no-users">Нет участников</div>';
                                        }
                                    }, 300);

                                } else {
                                    const errorData = await response.json().catch(() => ({}));
                                    alert(errorData.error || "Не удалось удалить участника");
                                }
                            } catch (error) {
                                console.error("Ошибка при удалении:", error);
                                alert("Произошла ошибка при удалении участника");
                            }
                        });
                    });

                    // Помечаем, что данные загружены
                    usersDiv.dataset.loaded = "true";

                } catch (error) {
                    console.error("Ошибка загрузки участников:", error);
                    usersDiv.innerHTML = '<div class="error-loading">Не удалось загрузить участников</div>';
                }
            }
        });
    });
});