import React, { useState, useEffect } from "react";
import "./task.css";
import "./column.css";
import {
  useDroppable,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

// ---------------------- SortableTask ----------------------
function SortableTask({ task, removeTask, columnId }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ 
      id: task.id,
      data: {
        type: "task",
        task: task,
        columnId: columnId
      }
    });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    marginBottom: "8px",
  };

  return (
    <div className="task-container">
      <div ref={setNodeRef} style={style} className="sortable-task task">
        <div {...attributes} {...listeners} className="drag-handle task-name">
          {task.title}
        </div>
        {removeTask && (
          <button
            className="remove-task-btn"
            onClick={(e) => {
              e.stopPropagation();
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

function Column({ column, removeColumn, csrfToken, updateTasks, addTask, removeTask, updateTask }) {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [showInput, setShowInput] = useState(false);

  const { setNodeRef, isOver } = useDroppable({
    id: column.id,
    data: {
      type: "column",
      column: column
    }
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

  return (
    <div 
      ref={setNodeRef} 
      className={`column ${isOver ? 'column-over' : ''}`}
      style={isOver ? { backgroundColor: 'rgba(0, 200, 0, 0.1)' } : {}}
    >
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
        <SortableContext
          items={tasks.map((task) => task.id)}
          strategy={verticalListSortingStrategy}
        >
          {tasks.map((task) => (
            <SortableTask 
              key={task.id} 
              task={task} 
              removeTask={removeTaskHandler}
              columnId={column.id}
            />
          ))}
        </SortableContext>
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
              onKeyDown={(e) => {
                if (e.key === 'Enter') addTaskHandler();
                if (e.key === 'Escape') setShowInput(false);
              }}
            />
            <button onClick={addTaskHandler}>Добавить</button>
            <button onClick={() => setShowInput(false)}>Отмена</button>
          </>
        )}
      </div>
    </div>
  );
}

export default Column;