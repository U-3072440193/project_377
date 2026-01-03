import React from "react";
import "./task.css";

function Task({ task, removeTask }) {
  return (
    <div className="task-container">
      <div className="task">
        <div className="task-name">{task.title}</div>
        {removeTask && (
          <button
            className="remove-task-btn"
            onClick={() => removeTask(task.id)}
          >
            ×
          </button>
        )}
        {task.description && <div className="task-description">{task.description}</div>}
      </div>
    </div>
  );
}

export default Task;
