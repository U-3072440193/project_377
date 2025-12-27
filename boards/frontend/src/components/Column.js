
import React, { useState, useEffect } from "react";
import Task from "./Task";
import "./Column.css";

function Column({ column, removeColumn, isOwner, csrfToken }) {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [showInput, setShowInput] = useState(false);

  useEffect(() => {
    setTasks(column.tasks || []);
  }, [column]);

  const addTask = () => {
    if (!newTaskTitle.trim()) return;

    fetch(`${process.env.REACT_APP_API_URL}columns/${column.id}/tasks/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({ title: newTaskTitle }),
    })
      .then(res => res.json())
      .then(data => {
        setTasks(prev => [...prev, data]);
        setNewTaskTitle("");
        setShowInput(false);
      })
      .catch(console.error);
  };

  const removeTask = (taskId) => {
    fetch(`${process.env.REACT_APP_API_URL}tasks/${taskId}/`, {
      method: "DELETE",
      credentials: "include",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then(() => setTasks(prev => prev.filter(t => t.id !== taskId)))
      .catch(console.error);
  };

  return (
    <div className="column">
      <div className="column-header">
        <h4>{column.title}</h4>
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
        {tasks.map(task => (
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