// Column.js
import React from 'react';
import Task from './Task';
import './Column.css';

function Column({ column, removeColumn }) {
  return (
    <div className="column">
      <div className="column-header">
        <h4>{column.title}</h4>
        {removeColumn && (
          <button className="remove-column-btn" onClick={() => removeColumn(column.id)}>
            ×
          </button>
        )}
      </div>
      <div className="tasks">
        {column.tasks.map(task => (
          <Task key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}

export default Column;
