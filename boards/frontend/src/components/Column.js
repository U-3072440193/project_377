import React, { useState, useEffect } from "react";
import "./task.css";
import "./column.css";
import Task from "./Task";
import { useDroppable } from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import renameIcon from "../assets/images/rename_w.svg";

function Column({
  column,
  removeColumn,
  csrfToken,
  updateTasks,
  addTask,
  removeTask,
  updateTask,
  forPermit,
  isMember,
  addCommentToTask,
  user,
  username,
  updateColumn,
  updateTaskTitle
}) {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [showInput, setShowInput] = useState(false);

  // Состояние для переименования колонки
  const [isRenaming, setIsRenaming] = useState(false);
  const [newColumnTitle, setNewColumnTitle] = useState(column.title);

  const { setNodeRef, isOver } = useDroppable({
    id: column.id,
    data: {
      type: "column",
      column: column,
    },
  });

  useEffect(() => {
    setTasks(column.tasks || []);
  }, [column.tasks]);

  const addTaskHandler = () => {
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
      .then((res) => res.json())
      .then((data) => {
        addTask(column.id, data);
        setNewTaskTitle("");
        setShowInput(false);
      })
      .catch(console.error);
  };

  const removeTaskHandler = (taskId) => {
    fetch(`${process.env.REACT_APP_API_URL}tasks/${taskId}/`, {
      method: "DELETE",
      credentials: "include",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then(() => {
        removeTask(column.id, taskId);
      })
      .catch(console.error);
  };
  
  // Для переименовывания колонки
  const handleRename = () => {
    if (newColumnTitle.trim() && newColumnTitle !== column.title) {
      updateColumn(column.id, newColumnTitle);
    }
    setIsRenaming(false);
  };

  const cancelRename = () => {
    setNewColumnTitle(column.title);
    setIsRenaming(false);
  };

  return (
    <div
      ref={setNodeRef}
      className={`column ${isOver ? "column-over" : ""}`}
      style={isOver ? { backgroundColor: "rgba(0, 200, 0, 0.1)" } : {}}
    >
      <div className="column-header">
        <div className="column-inner">
          {isRenaming ? (
            // Поле ввода для переименования
            <div className="rename-input-container">
              <input
                type="text"
                value={newColumnTitle}
                onChange={(e) => setNewColumnTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleRename();
                  if (e.key === 'Escape') cancelRename();
                }}
                autoFocus
                className="rename-input"
              />
              <button onClick={handleRename} className="rename-confirm-btn">
                ✓
              </button>
              <button onClick={cancelRename} className="rename-cancel-btn">
                ✕
              </button>
            </div>
          ) : (
            // Отображение названия колонки
            <>
              <div className="col-name">{column.title}</div>
              {forPermit && updateColumn && (
                <div className="column-header-buttons">
                  <button
                    className="rename-column-btn"
                    onClick={() => setIsRenaming(true)}
                    title="Переименовать"
                  >
                    <img className='renameIcon' src={renameIcon} alt="Переименовать"/>
                  </button>
                  {forPermit && removeColumn && (
                    <button
                      className="remove-column-btn"
                      onClick={() => removeColumn(column.id)}
                      title="Удалить колонку"
                    >
                      ×
                    </button>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div className="tasks">
        <SortableContext
          items={tasks.map((task) => task.id)}
          strategy={verticalListSortingStrategy}
        >
          {tasks.map((task) => (
            <Task
              key={task.id}
              task={task}
              removeTask={removeTaskHandler}
              columnId={column.id}
              isMember={isMember}
              updateTask={updateTask}
              csrfToken={csrfToken}
              addCommentToTask={addCommentToTask}
              user={user}
              username={username}
              updateTaskTitle={updateTaskTitle}
            />
          ))}
        </SortableContext>
      </div>

      {isMember() && (
        <div className="add-task">
          {!showInput ? (
            <button onClick={() => setShowInput(true)}>
              ＋ Добавить задачу
            </button>
          ) : (
            <>
              <input
                type="text"
                placeholder="Название задачи"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") addTaskHandler();
                  if (e.key === "Escape") setShowInput(false);
                }}
              />
              <button onClick={addTaskHandler}>Добавить</button>
              <button onClick={() => setShowInput(false)}>Отмена</button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default Column;