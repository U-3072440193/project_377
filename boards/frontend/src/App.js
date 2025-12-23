import React, { useState, useEffect } from "react";
import axios from "axios";

const serverUrl = "http://localhost:8000/";

function App() {
  const [board, setBoard] = useState(null);
  const [csrfToken, setCsrfToken] = useState(null);
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isAuth, setIsAuth] = useState(false);
  const [username, setUsername] = useState("");
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);

  // Получаем CSRF и проверяем сессию при старте
  useEffect(() => {
    axios
      .get(serverUrl + "api/csrf/", { withCredentials: true })
      .then((res) => {
        const token = res.headers["x-csrftoken"];
        setCsrfToken(token);
      })
      .catch((err) => console.error("CSRF ERROR:", err))
      .finally(() => {
        getSession();
      });
  }, []);

  // Проверяем сессию
  const getSession = () => {
    axios
      .get(serverUrl + "api/session/", { withCredentials: true })
      .then((res) => {
        if (res.data.isAuthenticated) {
          setUserId(res.data.user_id);
          setUsername(res.data.username);
          setIsAuth(true);
          getBoard();
        } else {
          setIsAuth(false);
        }
      })
      .catch((err) => console.error("SESSION ERROR:", err))
      .finally(() => setLoading(false));
  };

  // Загружаем доску
  const getBoard = () => {
    axios
      .get(serverUrl + "api/boards/7/", { withCredentials: true })
      .then((res) => setBoard(res.data))
      .catch((err) => console.error("BOARD ERROR:", err));
  };

  // Вход пользователя
  const loginUser = () => {
    axios
      .post(
        serverUrl + "api/login/",
        { username: login, password: password },
        {
          withCredentials: true,
          headers: { "X-CSRFToken": csrfToken },
        }
      )
      .then(() => {
        setIsAuth(true);
        setLogin("");
        setPassword("");
        setError(null);
        getSession();
      })
      .catch(() => setError("Неверные данные"));
  };

  if (loading) return <p>Проверка сессии...</p>;
  if (!isAuth)
    return (
      <div>
        <h2>Вход</h2>
        <input
          placeholder="Логин"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
        />
        <input
          placeholder="Пароль"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button onClick={loginUser}>Войти</button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    );

  if (!board) return <p>Загрузка доски...</p>;

  return (
    <div style={{ padding: 20 }}>
      <h2>👤 Текущий пользователь</h2>
      <pre>{JSON.stringify({ userId, username }, null, 2)}</pre>

      <h2>📋 Доска</h2>
      <pre>{JSON.stringify(board, null, 2)}</pre>
    </div>
  );
}

export default App;
