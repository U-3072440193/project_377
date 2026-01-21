import React, { useState, useEffect } from "react";
import Column from "./Column";
import "./main.css";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay,
  defaultDropAnimationSideEffects,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import userIcon from "../assets/images/user.svg";

function Main({ user, board, csrfToken, members, removeMember, serverUrl, username }) {
  const [columns, setColumns] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [activeTask, setActiveTask] = useState(null);
  const [newColumnTitle, setNewColumnTitle] = useState("");
  const [showInput, setShowInput] = useState(false);
  const [showMember, setShowMember] = useState(false);
  const isOwner = user.id === board.owner.id;
  const isMember = () => {
    return members.some(
      (member) => member.id === user.id || board.owner.id === user.id
    );
  };

  console.log("user:", user);
  console.log("csrfToken:", csrfToken);

  const toggleInput = () => {
    setShowInput(!showInput);
    if (showInput) {
      setNewColumnTitle("");
    }
  };

  const viewMember = () => {
    setShowMember(!showMember);
  };

  useEffect(() => {
    if (board) setColumns(board.columns || []);
  }, [board]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const handleDragStart = (event) => {
    const { active } = event;
    setActiveTask(active.data.current?.task);
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    const activeColumn = columns.find((col) =>
      col.tasks?.some((task) => task.id === activeId)
    );
    const overColumn = columns.find(
      (col) =>
        col.id === overId || col.tasks?.some((task) => task.id === overId)
    );

    if (!activeColumn || !overColumn) return;

    if (activeColumn.id === overColumn.id) {
      const oldIndex = activeColumn.tasks.findIndex(
        (task) => task.id === activeId
      );
      const newIndex = overColumn.tasks.findIndex((task) => task.id === overId);

      if (oldIndex !== newIndex) {
        const newColumns = columns.map((col) => {
          if (col.id === activeColumn.id) {
            return {
              ...col,
              tasks: arrayMove(col.tasks, oldIndex, newIndex),
            };
          }
          return col;
        });
        setColumns(newColumns);
        updateTaskOrder(activeId, newIndex, activeColumn.id);
      }
    }
    else {
      const task = activeColumn.tasks.find((task) => task.id === activeId);

      const newActiveColumn = {
        ...activeColumn,
        tasks: activeColumn.tasks.filter((task) => task.id !== activeId),
      };

      let newOverColumn;

      if (overId !== overColumn.id) {
        const overIndex = overColumn.tasks.findIndex(
          (task) => task.id === overId
        );
        const newTasks = [...overColumn.tasks];
        newTasks.splice(overIndex, 0, { ...task, column: overColumn.id });
        newOverColumn = {
          ...overColumn,
          tasks: newTasks,
        };
      }
      else {
        newOverColumn = {
          ...overColumn,
          tasks: [...overColumn.tasks, { ...task, column: overColumn.id }],
        };
      }

      const newColumns = columns.map((col) => {
        if (col.id === activeColumn.id) return newActiveColumn;
        if (col.id === overColumn.id) return newOverColumn;
        return col;
      });

      setColumns(newColumns);
      updateTaskColumn(activeId, overColumn.id);
    }
  };

  const updateTaskOrder = (taskId, newIndex, columnId) => {
    fetch(`${serverUrl}api/tasks/${taskId}/move/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({ order: newIndex, column: columnId }),
    }).catch(console.error);
  };

  const updateTaskColumn = (taskId, newColumnId) => {
    fetch(`${serverUrl}api/tasks/${taskId}/move/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({ column: newColumnId }),
    }).catch(console.error);
  };

  const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  };

  const updateTaskTitle = (taskId, newTitle) => {
    console.log("Переименование задачи:", taskId, "->", newTitle);

    fetch(`${serverUrl}api/tasks/${taskId}/rename/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({ title: newTitle }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log("Задача успешно переименована:", data);

        setColumns((prev) =>
          prev.map((col) => ({
            ...col,
            tasks: col.tasks.map((task) =>
              task.id === taskId ? { ...task, title: newTitle } : task
            ),
          }))
        );
      })
      .catch((error) => {
        console.error("Error renaming task:", error);
        alert("Ошибка при переименовании задачи: " + error.message);
      });
  };

  const addColumn = () => {
    if (!newColumnTitle.trim()) return;

    fetch(`${serverUrl}api/boards/${board.id}/columns/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
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
    fetch(`${serverUrl}api/columns/${colId}/`, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrfToken },
      credentials: "include",
    })
      .then(() => setColumns(columns.filter((col) => col.id !== colId)))
      .catch(console.error);
  };

  const updateColumnTitle = (columnId, newTitle) => {
    fetch(`${serverUrl}api/columns/${columnId}/rename/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({ title: newTitle }),
    })
      .then((res) => res.json())
      .then((data) => {
        setColumns((prev) =>
          prev.map((col) =>
            col.id === columnId ? { ...col, title: newTitle } : col
          )
        );
      })
      .catch(console.error);
  };

  const updateTasksInColumn = (columnId, newTasks) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId ? { ...col, tasks: newTasks } : col
      )
    );
  };

  const addTaskToColumn = (columnId, newTask) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId ? { ...col, tasks: [...col.tasks, newTask] } : col
      )
    );
  };

  const removeTaskFromColumn = (columnId, taskId) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId
          ? { ...col, tasks: col.tasks.filter((task) => task.id !== taskId) }
          : col
      )
    );
  };

  const updateTaskInColumn = (columnId, updatedTask) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId
          ? {
            ...col,
            tasks: col.tasks.map((task) =>
              task.id === updatedTask.id ? updatedTask : task
            ),
          }
          : col
      )
    );
  };

  const addCommentToTask = (taskId, newComment) => {
    setColumns((prevColumns) =>
      prevColumns.map((col) => ({
        ...col,
        tasks: col.tasks.map((task) =>
          task.id === taskId
            ? { ...task, comments: [...(task.comments || []), newComment] }
            : task
        ),
      }))
    );
  };

  const dropAnimation = {
    sideEffects: defaultDropAnimationSideEffects({
      styles: {
        active: {
          opacity: "0.5",
        },
      },
    }),
  };

  return (
    <div className="main">
      <div className="tool-bar">
        <div className="board-actions">
          <div className="inn-board">
            <h1>{board.title}</h1>
            <p>Дата создания: {new Date(board.created).toLocaleString('ru-RU', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}</p>
          </div>
          {user.id === board.owner.id && (
            <div className="actions">
              <button
                className="add-column-btn"
                onClick={toggleInput}
              >
                {showInput ? "×" : "+"}
              </button>
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
          )}
        </div>
        <div className="member-container">
          <button
            className="member-btn"
            onClick={viewMember}
          >
            {showMember ? "×" : <img className='userIcon' src={userIcon} alt="Пользователи" />}
          </button>
          {showMember && board && members.length > 0 && (
            <div className="members">
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
                    {member.username} ({member.role})
                    {user.id === board.owner.id && (
                      <button
                        className="remove-member-btn"
                        onClick={() => removeMember(member.id)}
                      >
                        ×
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <div className="user">
          <p>Создатель: {board.owner.username}</p>
          <img
            src={`${serverUrl}${board.owner.avatar}`}
            alt="avatar"
            width="50"
            height="50"
          />
        </div>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="columns-container">
          <SortableContext
            items={columns.map((col) => col.id)}
            strategy={horizontalListSortingStrategy}
          >
            {columns.map((col) => (
              <Column
                key={col.id}
                column={col}
                removeColumn={removeColumn}
                csrfToken={csrfToken}
                updateTasks={updateTasksInColumn}
                addTask={addTaskToColumn}
                removeTask={removeTaskFromColumn}
                updateTask={updateTaskInColumn}
                forPermit={isOwner}
                isMember={isMember}
                addCommentToTask={addCommentToTask}
                serverUrl={serverUrl}
                user={user}
                username={username}
                updateColumn={updateColumnTitle}
                updateTaskTitle={updateTaskTitle}
              />
            ))}
          </SortableContext>
        </div>

        <DragOverlay dropAnimation={dropAnimation}>
          {activeTask && (
            <div className="task-overlay">
              <div className="drag-handle task-name">{activeTask.title}</div>
            </div>
          )}
        </DragOverlay>
      </DndContext>
    </div>
  );
}

export default Main;