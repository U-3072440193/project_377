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

function Main({ user, board, csrfToken, members, removeMember, serverUrl,username }) {
  const [columns, setColumns] = useState([]);
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
  //const isMemberBool = isMember(); дописать  - для запрета перетаскивания не мемберами

  console.log("user:", user);
  console.log("csrfToken:", csrfToken);
  // При добавлении колонки
  const toggleInput = () => {
    setShowInput(!showInput);
    if (showInput) {
      setNewColumnTitle(""); // Очищаем поле при закрытии
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

  // Обработчик начала перетаскивания
  const handleDragStart = (event) => {
    const { active } = event;
    setActiveTask(active.data.current?.task);
  };

  // Обработчик завершения перетаскивания
  const handleDragEnd = (event) => {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    // Находим исходную и целевую колонки
    const activeColumn = columns.find((col) =>
      col.tasks?.some((task) => task.id === activeId)
    );
    const overColumn = columns.find(
      (col) =>
        col.id === overId || col.tasks?.some((task) => task.id === overId)
    );

    if (!activeColumn || !overColumn) return;

    // Если перетаскивание внутри одной колонки
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
        // Здесь можно отправить обновление на сервер
        updateTaskOrder(activeId, newIndex, activeColumn.id);
      }
    }
    // Если перетаскивание между колонками
    else {
      // Находим задачу
      const task = activeColumn.tasks.find((task) => task.id === activeId);

      // Удаляем задачу из исходной колонки
      const newActiveColumn = {
        ...activeColumn,
        tasks: activeColumn.tasks.filter((task) => task.id !== activeId),
      };

      // Добавляем задачу в целевую колонку
      let newOverColumn;

      // Если перетащили на другую задачу
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
      // Если перетащили на саму колонку
      else {
        newOverColumn = {
          ...overColumn,
          tasks: [...overColumn.tasks, { ...task, column: overColumn.id }],
        };
      }

      // Обновляем состояние
      const newColumns = columns.map((col) => {
        if (col.id === activeColumn.id) return newActiveColumn;
        if (col.id === overColumn.id) return newOverColumn;
        return col;
      });

      setColumns(newColumns);
      // Обновляем задачу на сервере
      updateTaskColumn(activeId, overColumn.id);
    }
  };
  // Функция для обновления задачи на сервере
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
  // Убедитесь, что headers содержат CSRF токен
const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
};

// И проверьте, что boardId правильный
//console.log('Creating column for board:', boardId);
  // Функция для добавления колонки
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

  // Функция для обновления задач в колонке
  const updateTasksInColumn = (columnId, newTasks) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId ? { ...col, tasks: newTasks } : col
      )
    );
  };

  // Функция для добавления задачи
  const addTaskToColumn = (columnId, newTask) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId ? { ...col, tasks: [...col.tasks, newTask] } : col
      )
    );
  };

  // Функция для удаления задачи
  const removeTaskFromColumn = (columnId, taskId) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId
          ? { ...col, tasks: col.tasks.filter((task) => task.id !== taskId) }
          : col
      )
    );
  };

  // Функция для обновления задачи
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
  // Функция для добавления комментария к задаче
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
      <div>{user.username}</div>
      <div className="tool-bar">
        <div className="board-actions">
          <div className="inn-board">
            <h1>{board.title}</h1>
            <p>Дата создания: {board.created}</p>
          </div>
          {user.id === board.owner.id && (
            <div className="actions">
              <button
                className="add-column-icon"
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
            className="add-column-icon"
            onClick={viewMember}
          >
            {showMember ? "×" : "👥"}
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
            width="100"
          />
        </div>
      </div>

      <h3>Колонки:</h3>

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