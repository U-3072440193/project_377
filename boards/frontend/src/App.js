import React, { useState, useEffect } from "react";
import axios from "axios";
import Main from "./components/Main";

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
  const [boardId, setBoardId] = useState(null);

  // ОДИН useEffect для настройки axios
  useEffect(() => {
    axios.defaults.withCredentials = true;
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    axios.defaults.xsrfCookieName = "csrftoken";
    
    // Интерцептор для ВСЕХ запросов
    axios.interceptors.request.use(config => {
      const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
        
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
        if (!csrf) setCsrf(csrfToken);
      }
      
      return config;
    });
  }, [csrf]);

  // Получаем board_id из URL
  useEffect(() => {
    const pathParts = window.location.pathname.split('/');
    const id = pathParts[3];
    console.log("Path parts:", pathParts, "Board ID from URL:", id);
    
    if (id && !isNaN(id)) {
      setBoardId(parseInt(id, 10));
    } else if (window.BOARD_ID) {
      setBoardId(window.BOARD_ID);
    }
  }, []);

  useEffect(() => {
    getCSRF();
  }, []);

  const getCSRF = () => {
    axios
      .get(serverUrl + "api/csrf/", { 
        withCredentials: true,
      })
      .then((res) => {
        const token = res.headers["x-csrftoken"] || document.cookie
          .split('; ')
          .find(row => row.startsWith('csrftoken='))
          ?.split('=')[1];
        
        console.log("CSRF токен получен:", token ? "ДА" : "НЕТ");
        setCsrf(token || "");
        getSession();
      })
      .catch((err) => {
        console.error("Ошибка получения CSRF:", err);
        getSession();
      });
  };

  const getSession = () => {
    axios
      .get(serverUrl + "api/session/", { 
        withCredentials: true,
      })
      .then((res) => {
        console.log("Данные сессии:", res.data);
        if (res.data.isAuthenticated) {
          setUsername(res.data.username);
          setUserId(res.data.user_id);
          setIsAuth(true);
        } else {
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
      })
      .then(() => {
        setIsAuth(false);
        setUsername("");
        setUserId(null);
        setUser(null);
        setBoard(null);
        setMembers([]);
        window.location.reload();
      })
      .catch((err) => {
        console.error("Ошибка при выходе:", err);
        window.location.reload();
      });
  };

  const fetchUserAndBoard = () => {
    if (!boardId) {
      console.error("Board ID не найден!");
      return;
    }
    
    setLoading(true);
    
    const fetchUser = axios.get(serverUrl + "api/user/", {
      withCredentials: true,
    });
    
    const fetchBoard = axios.get(serverUrl + `api/boards/${boardId}/`, {
      withCredentials: true,
    });

    Promise.all([fetchUser, fetchBoard])
      .then(([userRes, boardRes]) => {
        console.log("Данные пользователя и доски:", userRes.data, boardRes.data);
        setUser(userRes.data);
        setBoard(boardRes.data);
      })
      .catch((err) => {
        console.error("Ошибка загрузки данных:", err);
        if (err.response?.status === 404) {
          axios.get(serverUrl + "api/boards/", {
            withCredentials: true,
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

  useEffect(() => {
    if (boardId && isAuth) {
      fetchUserAndBoard();
    }
  }, [boardId, isAuth]);

  useEffect(() => {
    if (board?.id) {
      axios
        .get(`${serverUrl}api/boards/${board.id}/members/`, {
          withCredentials: true,
        })
        .then((res) => setMembers(res.data))
        .catch((err) => console.error("Ошибка загрузки участников:", err));
    }
  }, [board]);

  const removeMember = (userId) => {
    if (!board) return;
    axios
      .post(
        `${serverUrl}api/boards/${board.id}/remove-member/`,
        { user_id: userId },
        {
          withCredentials: true,
        }
      )
      .then((res) => {
        setMembers((prev) => prev.filter((m) => m.id !== userId));
      })
      .catch((err) => alert("Не удалось удалить участника"));
  };

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
          username={username}
        />
      )}
    </div>
  );
};

export default App;