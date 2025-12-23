/* 
import React, { useState, useEffect } from "react";
import Column from "./Column";
import "./Main.css";

function Main({ user, board }) {
  const [columns, setColumns] = useState([]);
  const [newColumnTitle, setNewColumnTitle] = useState("");
  const [showInput, setShowInput] = useState(false);

  useEffect(() => {
    if (board) setColumns(board.columns || []);
  }, [board]);

  // Проверка: текущий пользователь — владелец доски
  const isOwner = user && board.owner && user.id === board.owner.id;

  const addColumn = () => {
    if (!newColumnTitle.trim()) return;

    fetch(`${process.env.REACT_APP_API_URL}boards/${board.id}/columns/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ title: newColumnTitle }),
    })
      .then(res => res.json())
      .then(data => {
        setColumns([...columns, data]);
        setNewColumnTitle("");
        setShowInput(false);
      })
      .catch(console.error);
  };

  const removeColumn = (colId) => {
    fetch(`${process.env.REACT_APP_API_URL}columns/${colId}/`, {
      method: "DELETE",
      credentials: "include",
    })
      .then(() => setColumns(columns.filter(col => col.id !== colId)))
      .catch(console.error);
  };

  return (
    <div className="main">
      <div className="tool-bar">
        <div className="board-actions">
          <div className="inn-board">
            <h1>{board.title}</h1>
            <p>Дата создания: {board.created}</p>
          </div>
          <div className="actions">
            <img
              src="/icons/add-column.svg"
              alt="Добавить колонку"
              className="add-column-icon"
              onClick={() => setShowInput(true)}
            />
            {showInput && (
              <div className="add-column-form">
                <input
                  type="text"
                  placeholder="Название колонки"
                  value={newColumnTitle}
                  onChange={(e) => setNewColumnTitle(e.target.value)}
                  autoFocus
                />
                <button onClick={addColumn}>Добавить</button>
              </div>
            )}
          </div>
        </div>
        <div className="user">
          <p>Создатель: {board.owner.username}</p>
          <img
            src={`http://127.0.0.1:8000${board.owner.avatar}`}
            alt="avatar"
            width="100"
          />
        </div>
      </div>

      <h3>Колонки:</h3>
      <div className="columns-container">
        <ul>
          {columns.map(col => (
            <Column
              key={col.id}
              column={col}
              removeColumn={removeColumn}
              isOwner={isOwner}
            />
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Main;
 */