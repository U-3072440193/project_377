import React from "react";
import {
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

function Task({ task, removeTask, columnId, isMember }) {
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
        {isMember() && removeTask && (
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

export default Task;