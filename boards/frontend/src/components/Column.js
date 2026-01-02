import React, { useState, useEffect } from "react";
import "./task.css";
import "./column.css";
//------для днд-кит старт
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";

import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";

import { CSS } from "@dnd-kit/utilities"; // Для корректного позиционирования перетаскиваемого элемента

//------для днд-кит енд
// ----------------------  объявляем SortableTask ----------------------
function SortableTask({ task, removeTask }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    marginBottom: "8px",
  };

  return (
    <div className="task-container">
      <div ref={setNodeRef} style={style} className="sortable-task task">
        {/* Задача для drag */}
        <div {...attributes} {...listeners} className="drag-handle task-name">
          {task.title}
        </div>

        {/* Кнопка удаления вне drag-хендла */}
        {removeTask && (
          <button
            className="remove-task-btn"
            onClick={(e) => {
              e.stopPropagation(); //   чтобы клик не шел в drag
              removeTask(task.id);
            }}
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

function Column({ column, removeColumn, isOwner, csrfToken }) {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [showInput, setShowInput] = useState(false);
  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (!over) return; // если отпустили не над элементом
    if (active.id !== over.id) {
      const oldIndex = tasks.findIndex((task) => task.id === active.id);
      const newIndex = tasks.findIndex((task) => task.id === over.id);

      setTasks((tasks) => arrayMove(tasks, oldIndex, newIndex));
    }
  };

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
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
      .then(() => setTasks((prev) => prev.filter((t) => t.id !== taskId)))
      .catch(console.error);
  };

  return (
    <div className="column">
      <div className="column-header">
        <div className="column-inner">
          <div className="col-name">{column.title}</div>
          {removeColumn && (
            <button
              className="remove-column-btn"
              onClick={() => removeColumn(column.id)}
            >
              ×
            </button>
          )}
        </div>
      </div>

      <div className="tasks">
        <DndContext
          sensors={useSensors(useSensor(PointerSensor))}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={tasks.map((task) => task.id)}
            strategy={verticalListSortingStrategy}
          >
            {tasks.map((task) => (
              <SortableTask key={task.id} task={task} removeTask={removeTask} />
            ))}
          </SortableContext>
        </DndContext>
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
