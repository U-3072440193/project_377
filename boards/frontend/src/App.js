import React, { useState, useEffect } from "react";
import axios from "axios";
import Main from "./components/Main";

const serverUrl = "http://localhost:8000/";

const App = () => {
  const [csrf, setCsrf] = useState("");
  const [loginVal, setLoginVal] = useState("");
  const [passwordVal, setPasswordVal] = useState("");
  const [isAuth, setIsAuth] = useState(false);
  const [username, setUsername] = useState("");
  const [userId, setUserId] = useState(null);
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);
  const [board, setBoard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [members, setMembers] = useState([]);

  // --- получаем CSRF токен сразу при монтировании ---
  useEffect(() => {
    getCSRF();
  }, []);

  useEffect(() => {
    getSession();
  }, []);

  const getSession = () => {
    axios
      .get(serverUrl + "api/session/", { withCredentials: true })
      .then((res) => {
        if (res.data.isAuthenticated) {
          setUsername(res.data.username);
          setUserId(res.data.user_id);
          setIsAuth(true);
          fetchUserAndBoard(); // загружаем данные после подтвержденной сессии
        } else {
          getCSRF();
        }
      })
      .catch((err) => console.error(err));
  };

  const getCSRF = () => {
    axios
      .get(serverUrl + "api/csrf/", { withCredentials: true })
      .then((res) => setCsrf(res.headers["x-csrftoken"]))
      .catch((err) => console.error(err));
  };

  const login = () => {
    axios
      .post(
        serverUrl + "api/login/",
        { username: loginVal, password: passwordVal },
        {
          withCredentials: true,
          headers: { "X-CSRFToken": csrf },
        }
      )
      .then((res) => {
        setLoginVal("");
        setPasswordVal("");
        setError("");
        getSession(); // обновляем данные пользователя
      })
      .catch((err) => setError("Неверные данные"));
  };

  const logout = () => {
    axios
      .get(serverUrl + "api/logout/", { withCredentials: true })
      .then(() => {
        setIsAuth(false);
        setUsername("");
        setUserId(null);
        setUser(null);
        setBoard(null);
        getCSRF();
      })
      .catch((err) => console.error(err));
  };

  const fetchUserAndBoard = () => {
    setLoading(true);
    const fetchUser = axios.get(serverUrl + "api/user/", {
      withCredentials: true,
    });
    const fetchBoard = axios.get(serverUrl + "api/boards/7/", {
      withCredentials: true,
    });

    Promise.all([fetchUser, fetchBoard])
      .then(([userRes, boardRes]) => {
        setUser(userRes.data);
        setBoard(boardRes.data);
      })
      .catch((err) => console.error("Ошибка загрузки данных:", err))
      .finally(() => setLoading(false));
  };
  // --- загружаем участников после загрузки доски ---
  useEffect(() => {
    if (board) {
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
          headers: { "X-CSRFToken": csrf },
        }
      )
      .then((res) => {
        // после успешного удаления обновляем список участников
        setMembers((prev) => prev.filter((m) => m.id !== userId));
      })
      .catch((err) => alert("Не удалось удалить участника"));
  };

  return (
    <div style={{ padding: 20 }}>
      <div>Вы - {isAuth ? username : "не авторизованы"}</div>

      {!isAuth ? (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            login();
          }}
        >
          <input
            type="text"
            value={loginVal}
            onChange={(e) => setLoginVal(e.target.value)}
            placeholder="Логин"
          />
          <input
            type="password"
            value={passwordVal}
            onChange={(e) => setPasswordVal(e.target.value)}
            placeholder="Пароль"
          />
          {error && <div>{error}</div>}
          <button type="submit">Войти</button>
        </form>
      ) : (
        <button onClick={logout}>Выйти</button>
      )}

      {/* --- Блок пользователя и доски --- */}
      {isAuth && loading && <p>Загрузка данных...</p>}

      {isAuth && !loading && (
        <>
          {user ? (
            <div>
              <h2>👤 Пользователь</h2>
              <p>Имя: {user.username}</p>
              <p>Email: {user.email}</p>
              {user.avatar && (
                <img
                  src={`${serverUrl}${user.avatar}`}
                  alt="avatar"
                  width={50}
                />
              )}
            </div>
          ) : (
            <p>Пользователь не найден</p>
          )}
          {board && members.length > 0 && (
            <div>
              <h3>Участники доски:</h3>
              <ul>
                {members.map((member) => (
                  <li key={member.id}>
                    <img
                      src={`${serverUrl}${member.avatar}`}
                      alt={member.username}
                      width={32}
                      height={32}
                      style={{ borderRadius: "50%" }}
                    />
                    {member.username} ({member.role}){/* Кнопка удаления */}
                    <button onClick={() => removeMember(member.id)}>
                      Удалить
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {board ? (
            <div>
              <h2>📋 Доска: {board.title}</h2>
              <p>Владелец: {board.owner.username}</p>
              <h3>Колонки:</h3>
              <ul>
                {board.columns.map((col) => (
                  <li key={col.id}>
                    <strong>{col.title}</strong> (позиция: {col.position})
                    <ul>
                      {col.tasks.map((task) => (
                        <li key={task.id}>{task.title}</li>
                      ))}
                    </ul>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p>Доска не найдена</p>
          )}
          <Main board={board} user={user} csrfToken={csrf} members={members} removeMember={removeMember} serverUrl={serverUrl} />
        </>
      )}
    </div>
  );
};

export default App;
