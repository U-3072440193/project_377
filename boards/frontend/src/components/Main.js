import React, { useState, useEffect } from "react";
import Column from "./Column";
import "./main.css";
// ------------- для @dnd-kit старт----------------
import {
  DndContext, //контейнер, который управляет всей логикой drag’n’drop.
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
//import SortableColumn from "./SortableColumn"; // Обернём Column
// ------------- для @dnd-kit енд----------------

function Main({ user, board, csrfToken }) {
  const [columns, setColumns] = useState([]);
  const [newColumnTitle, setNewColumnTitle] = useState("");
  const [showInput, setShowInput] = useState(false);

  console.log("user:", user);
  console.log("csrfToken:", csrfToken);

  useEffect(() => {
    if (board) setColumns(board.columns || []);
  }, [board]);

  // Проверка: текущий пользователь — владелец доски
  

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
      .then((res) => res.json())
      .then((data) => {
        setColumns([...columns, data]);
        setNewColumnTitle("");
        setShowInput(false);
      })
      .catch(console.error);
  };

  const removeColumn = (colId) => {
    fetch(`${process.env.REACT_APP_API_URL}columns/${colId}/`, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrfToken },
      credentials: "include",
    })
      .then(() => setColumns(columns.filter((col) => col.id !== colId)))
      .catch(console.error);
  };

  return (
    <div className="main">
      <div>{user.username}</div>
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
          {columns.map((col) => (
            <Column
              key={col.id}
              column={col}
              removeColumn={removeColumn}
              csrfToken={csrfToken}
            />
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Main;
