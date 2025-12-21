import React, { useState, useEffect } from "react";
import Task from "./Task";
import "./Column.css";

function Column({ column, removeColumn, isOwner }) { // добавляем isOwner в props
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [showInput, setShowInput] = useState(false);

  // при загрузке колонки кладём её задачи в state
  useEffect(() => {
    setTasks(column.tasks || []);
  }, [column]);
  console.log("Column:", column.title, "isOwner", isOwner, "removeColumn", removeColumn);

  // функция для получения CSRF токена
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const addTask = () => {
    if (!newTaskTitle.trim()) return;

    const csrftoken = getCookie("csrftoken");

    fetch(`${process.env.REACT_APP_API_URL}columns/${column.id}/tasks/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      credentials: "include", // обязательно для авторизации
      body: JSON.stringify({ title: newTaskTitle }),
    })
      .then((res) => res.json())
      .then((data) => {
        setTasks((prev) => [...prev, data]);
        setNewTaskTitle("");
        setShowInput(false);
      })
      .catch(console.error);
  };

  const removeTask = (taskId) => {
    fetch(`${process.env.REACT_APP_API_URL}tasks/${taskId}/`, {
      method: "DELETE",
      credentials: "include",
    })
      .then(() => {
        setTasks((prev) => prev.filter((t) => t.id !== taskId));
      })
      .catch(console.error);
  };

  return (
    <div className="column">
      <div className="column-header">
        <h4>{column.title}</h4>

        {/* Кнопка удаления колонки видна только владельцу */}
        {isOwner && removeColumn && (
          <button
            className="remove-column-btn"
            onClick={() => removeColumn(column.id)}
          >
            ×
          </button>
        )}
      </div>

      <div className="tasks">
        {tasks.map((task) => (
          <Task
            key={task.id}
            task={task}
            onDelete={() => removeTask(task.id)}
          />
        ))}
      </div>

      <div className="add-task">
        {!showInput ? (
          <button onClick={() => setShowInput(true)}>＋ Добавить задачу</button>
        ) : (
          <>
            <input
              type="text"
              placeholder="Название задачи"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              autoFocus
            />
            <button onClick={addTask}>Добавить</button>
          </>
        )}
      </div>
    </div>
  );
}

export default Column;
