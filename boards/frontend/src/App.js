import React, { useEffect, useState } from "react";
import Main from "./components/Main";

function App() {
  const [board, setBoard] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  console.log("API URL =", process.env.REACT_APP_API_URL);

  // 1. Проверяем сессию
  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}session/`, {
      credentials: "include",
    })
      .then(res => res.json())
      .then(data => {
        console.log("SESSION:", data);
        if (data.isAuthenticated) {
          setUser({
            id: data.user_id,
            username: data.username,
          });
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // 2. Загружаем доску
  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}boards/7/`, {
      credentials: "include",
    })
      .then(res => res.json())
      .then(data => {
        console.log("BOARD DATA:", data);
        setBoard(data);
      })
      .catch(err => console.error("BOARD ERROR:", err));
  }, []);

  if (loading) return <p>Проверка сессии...</p>;
  if (!board) return <p>Загрузка доски...</p>;

  return <Main user={user} board={board} />;
}

export default App;
