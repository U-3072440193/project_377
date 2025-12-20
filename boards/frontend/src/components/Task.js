import React from 'react';
import './Task.css'

function Task({ task }) {
  return (
    <div className="task-container">
        <div className="task">
            <h5>{task.title}</h5>
            
            <li>{task.description}</li>

        </div>
        
    </div>
  
);
}

export default Task;