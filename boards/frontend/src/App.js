import React, { useState, useEffect } from "react";
import axios from "axios";
import Main from "./components/Main";

// ИСПРАВЬТЕ ЭТУ СТРОКУ:
const serverUrl = "http://127.0.0.1:8000/";

const App = () => {
  const [csrf, setCsrf] = useState("");
  const [isAuth, setIsAuth] = useState(false);
  const [username, setUsername] = useState("");
  const [userId, setUserId] = useState(null);
  const [user, setUser] = useState(null);
  const [board, setBoard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState([]);

  // Настройка axios для работы с CORS
  useEffect(() => {
    axios.defaults.withCredentials = true;
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    axios.defaults.xsrfCookieName = "csrftoken";
  }, []);

  // --- получаем CSRF токен и проверяем сессию ---
  useEffect(() => {
    getCSRF();
  }, []);

  const getCSRF = () => {
    axios
      .get(serverUrl + "api/csrf/", { 
        withCredentials: true,
        headers: {
          'Accept': 'application/json',
        }
      })
      .then((res) => {
        const token = res.headers["x-csrftoken"] || document.cookie
          .split('; ')
          .find(row => row.startsWith('csrftoken='))
          ?.split('=')[1];
        
        console.log("CSRF токен получен:", token ? "ДА" : "НЕТ");
        setCsrf(token || "");
        
        // После получения CSRF проверяем сессию
        getSession();
      })
      .catch((err) => {
        console.error("Ошибка получения CSRF:", err);
        // Пробуем продолжить без CSRF
        getSession();
      });
  };

  const getSession = () => {
    axios
      .get(serverUrl + "api/session/", { 
        withCredentials: true,
        headers: csrf ? { "X-CSRFToken": csrf } : {}
      })
      .then((res) => {
        console.log("Данные сессии:", res.data);
        if (res.data.isAuthenticated) {
          setUsername(res.data.username);
          setUserId(res.data.user_id);
          setIsAuth(true);
          fetchUserAndBoard(); // загружаем данные после подтвержденной сессии
        } else {
          // Если не авторизован
          setIsAuth(false);
          setUsername("");
          setUserId(null);
        }
      })
      .catch((err) => {
        console.error("Ошибка при проверке сессии:", err);
        setIsAuth(false);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const logout = () => {
    axios
      .get(serverUrl + "api/logout/", { 
        withCredentials: true,
        headers: csrf ? { "X-CSRFToken": csrf } : {}
      })
      .then(() => {
        setIsAuth(false);
        setUsername("");
        setUserId(null);
        setUser(null);
        setBoard(null);
        setMembers([]);
        // Перезагружаем страницу для очистки состояния
        window.location.reload();
      })
      .catch((err) => {
        console.error("Ошибка при выходе:", err);
        window.location.reload();
      });
  };

  const fetchUserAndBoard = () => {
    setLoading(true);
    const headers = csrf ? { "X-CSRFToken": csrf } : {};
    
    const fetchUser = axios.get(serverUrl + "api/user/", {
      withCredentials: true,
      headers
    });
    
    const fetchBoard = axios.get(serverUrl + "api/boards/17/", {  // ИСПРАВЬТЕ ID ДОСКИ ЕСЛИ НУЖНО
      withCredentials: true,
      headers
    });

    Promise.all([fetchUser, fetchBoard])
      .then(([userRes, boardRes]) => {
        console.log("Данные пользователя и доски:", userRes.data, boardRes.data);
        setUser(userRes.data);
        setBoard(boardRes.data);
      })
      .catch((err) => {
        console.error("Ошибка загрузки данных:", err);
        // Если ошибка 404 для доски, попробуем другую
        if (err.response?.status === 404) {
          axios.get(serverUrl + "api/boards/", {
            withCredentials: true,
            headers
          })
          .then(res => {
            if (res.data.length > 0) {
              setBoard(res.data[0]);
            }
          })
          .catch(e => console.error("Ошибка получения списка досок:", e));
        }
      })
      .finally(() => setLoading(false));
  };

  // --- загружаем участников после загрузки доски ---
  useEffect(() => {
    if (board?.id) {
      axios
        .get(`${serverUrl}api/boards/${board.id}/members/`, {
          withCredentials: true,
          headers: csrf ? { "X-CSRFToken": csrf } : {}
        })
        .then((res) => setMembers(res.data))
        .catch((err) => console.error("Ошибка загрузки участников:", err));
    }
  }, [board, csrf]);

  const removeMember = (userId) => {
    if (!board) return;
    axios
      .post(
        `${serverUrl}api/boards/${board.id}/remove-member/`,
        { user_id: userId },
        {
          withCredentials: true,
          headers: csrf ? { 
            "X-CSRFToken": csrf,
            'Content-Type': 'application/json'
          } : {}
        }
      )
      .then((res) => {
        // после успешного удаления обновляем список участников
        setMembers((prev) => prev.filter((m) => m.id !== userId));
      })
      .catch((err) => alert("Не удалось удалить участника"));
  };

  // --- Рендеринг ---
  if (loading) {
    return (
      <div style={{ padding: 20 }}>
        <p>Загрузка приложения...</p>
      </div>
    );
  }

  if (!isAuth) {
    return (
      <div style={{ padding: 20 }}>
        <h2>Требуется авторизация</h2>
        <p>Пожалуйста, выполните следующие шаги:</p>
        <ol>
          <li>Откройте <a href="http://127.0.0.1:8000/admin/" target="_blank" rel="noreferrer">Django админку</a></li>
          <li>Войдите в систему</li>
          <li>Вернитесь на эту страницу и обновите её (F5)</li>
        </ol>
        <button onClick={() => window.location.reload()}>Обновить страницу</button>
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2>Добро пожаловать, {username}!</h2>
        <button onClick={logout}>Выйти</button>
      </div>

      {board && user && (
        <Main
          board={board}
          user={user}
          csrfToken={csrf}
          members={members}
          removeMember={removeMember}
          serverUrl={serverUrl}
        />
      )}
    </div>
  );
};

export default App;