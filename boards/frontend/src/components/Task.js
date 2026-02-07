import React, { useState, useEffect, useRef } from "react";
import "./task.css";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import axios from "axios";
import TipTap from "./TipTap";
import renameIcon from "../assets/images/rename_w.svg";
import textIcon from "../assets/images/text.svg";
import commentIcon from "../assets/images/comment.svg";
import fileIcon from "../assets/images/file.svg";
import timeIcon from "../assets/images/time_w.svg";
import userIcon from "../assets/images/user.svg";
import DeadlineButton from "./DeadlineButton";

function Task({
  task,
  removeTask,
  columnId,
  isMember,
  updateTask,
  csrfToken,
  addCommentToTask,
  user,
  username,
  updateTaskTitle,
  readOnly = false,
  members: boardMembers, 
  serverUrl, 
  board, 
  isOwner
}) {
  const [showEditor, setShowEditor] = useState(false);
  const [description, setDescription] = useState(task.description || "");
  const [showFiles, setShowFiles] = useState(false);
  const [showDescriptionOverlay, setShowDescriptionOverlay] = useState(false);
  const [files, setFiles] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [newCommentTitle, setNewCommentTitle] = useState("");
  const [showComments, setShowComments] = useState(false);
  const [showPriority, setShowPriority] = useState(false);
  const [priority, setPriority] = useState(task.priority || "low");

  const [isRenaming, setIsRenaming] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState(task.title);
  const [taskMembers, setTaskMembers] = useState(task.responsible || []);
  const [showMember, setShowMember] = useState(false);

  // Реф для позиционирования выпадающего меню
  const memberButtonRef = useRef(null);
  const dropdownRef = useRef(null);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: task.id,
    data: {
      type: "task",
      task: task,
      columnId: columnId,
    },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    marginBottom: "8px",
  };

  useEffect(() => {
    fetchFiles();
  }, [task.id]);

  // Закрытие выпадающего меню при клике вне его
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target) &&
          memberButtonRef.current && !memberButtonRef.current.contains(event.target)) {
        setShowMember(false);
      }
    };

    if (showMember) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showMember]);

  const fetchFiles = async () => {
    try {
      setLoadingFiles(true);
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}tasks/${task.id}/files/`,
        {
          method: "GET",
          credentials: "include",
        }
      );

      if (response.ok) {
        const data = await response.json();
        setFiles(data);
      } else {
        console.error("Ошибка загрузки файлов:", response.status);
      }
    } catch (error) {
      console.error("Ошибка загрузки файлов:", error);
    } finally {
      setLoadingFiles(false);
    }
  };

  const handleRename = () => {
    if (readOnly) return;
    if (newTaskTitle.trim() && newTaskTitle !== task.title) {
      if (updateTaskTitle) {
        updateTaskTitle(task.id, newTaskTitle);
      } else {
        console.error("updateTaskTitle функция не передана!");
      }
    }
    setIsRenaming(false);
  };

  const cancelRename = () => {
    setNewTaskTitle(task.title);
    setIsRenaming(false);
  };

  async function uploadFile(taskId, file) {
    if (readOnly) return;
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      `${process.env.REACT_APP_API_URL}tasks/${taskId}/files/upload/`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `Ошибка ${response.status}: ${response.statusText}`
      );
    }

    return response.json();
  }

  const deleteFile = async (fileId) => {
    if (readOnly) return;
    if (!window.confirm("Удалить этот файл?")) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}files/${fileId}/`,
        {
          method: "DELETE",
          credentials: "include",
          headers: {
            "X-CSRFToken": csrfToken,
          },
        }
      );

      if (response.ok) {
        setFiles(files.filter((file) => file.id !== fileId));
      } else {
        alert("Не удалось удалить файл");
      }
    } catch (error) {
      console.error("Ошибка удаления файла:", error);
      alert("Ошибка удаления файла");
    }
  };

  async function handleFileChange(e) {
    if (readOnly) return;
    const file = e.target.files[0];
    if (!file) return;

    try {
      await uploadFile(task.id, file);
      fetchFiles();
      alert("Файл успешно загружен");
    } catch (err) {
      console.error(err);
      alert("Ошибка загрузки файла");
    } finally {
      e.target.value = "";
    }
  }

  const saveDescription = (htmlContent) => {
    if (readOnly) return;
    fetch(`${process.env.REACT_APP_API_URL}tasks/${task.id}/description/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({
        description: htmlContent,
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Ошибка сохранения описания");
        return res.json();
      })
      .then((updatedTask) => {
        setDescription(updatedTask.description);
        if (updateTask) updateTask(columnId, updatedTask);
        setShowEditor(false);
      })
      .catch((err) => {
        console.error(err);
        alert("Не удалось сохранить описание");
      });
  };

  const formatDate = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const addCommentHandler = async () => {
    if (readOnly) return;
    if (!newCommentTitle.trim()) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}tasks/${task.id}/comments/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          credentials: "include",
          body: JSON.stringify({
            text: newCommentTitle,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Ошибка ${response.status}`);
      }

      const data = await response.json();

      if (addCommentToTask) addCommentToTask(task.id, data);
      setNewCommentTitle("");

      if (!showComments) {
        setShowComments(true);
      }
    } catch (err) {
      console.error("Ошибка добавления комментария:", err);
      alert("Не удалось добавить комментарий: " + err.message);
    }
  };

  const deleteCommentHandler = async (commentId) => {
    if (readOnly) return;
    if (!window.confirm("Удалить этот комментарий?")) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}comments/${commentId}/delete/`,
        {
          method: "DELETE",
          credentials: "include",
          headers: {
            "X-CSRFToken": csrfToken,
          },
        }
      );

      if (response.ok) {
        const updatedComments = task.comments.filter(
          (comment) => comment.id !== commentId
        );

        const updatedTask = {
          ...task,
          comments: updatedComments,
        };

        if (updateTask) {
          updateTask(columnId, updatedTask);
        }
      } else {
        alert("Не удалось удалить комментарий");
      }
    } catch (error) {
      console.error("Ошибка удаления комментария:", error);
      alert("Ошибка удаления комментария");
    }
  };

  const changePriority = async (newPriority) => {
    if (readOnly) return;
    if (!isMember()) return;

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}tasks/${task.id}/priority/`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          credentials: "include",
          body: JSON.stringify({
            priority: newPriority,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Ошибка изменения приоритета");
      }

      const updatedTask = await response.json();
      setPriority(newPriority);
      if (updateTask) updateTask(columnId, updatedTask);
      setShowPriority(false);
    } catch (err) {
      console.error("Ошибка изменения приоритета:", err);
      alert("Не удалось изменить приоритет");
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "low":
        return "#4CAF50";
      case "average":
        return "#FFC107";
      case "high":
        return "#FF9800";
      case "maximal":
        return "#F44336";
      default:
        return "#6c757d";
    }
  };

  const getPriorityName = (priority) => {
    switch (priority) {
      case "low":
        return "Низкий";
      case "average":
        return "Средний";
      case "high":
        return "Высокий";
      case "maximal":
        return "Максимум";
      default:
        return "Не указан";
    }
  };

  // Обработка дедлайна
  const handleDeadlineChange = (updatedTask) => {
    if (updateTask) {
      updateTask(columnId, updatedTask);
    }
  };

  // Новая функция для кнопки дедлайна
  const DeadlineIconButton = ({ onClick, title, hasDeadline = false }) => (
    <button
      className={`deadline-icon-btn ${hasDeadline ? "has-deadline" : ""}`}
      onClick={onClick}
      title={title}
      disabled={readOnly}
    >
      <img className='timeIcon' src={timeIcon} alt="Дедлайн" />
    </button>
  );

  //Добавление мембера к таску
  const addMemberToTask = (userId) => {
    if (readOnly || !isMember()) return;
    
    axios
      .post(
        `${serverUrl}api/tasks/${task.id}/add-responsible/`,
        { user_id: userId },
        {
          withCredentials: true,
          headers: {
            "X-CSRFToken": csrfToken,
          }
        }
      )
      .then((res) => {
        const newMember = boardMembers.find(m => m.id === userId);
        if (newMember) {
          const updatedTaskMembers = [...taskMembers, newMember];
          setTaskMembers(updatedTaskMembers);
          
          const updatedTask = {
            ...task,
            responsible: updatedTaskMembers
          };
          if (updateTask) updateTask(columnId, updatedTask);
        }
      })
      .catch((err) => {
        console.error("Ошибка добавления участника:", err);
        alert("Не удалось добавить участника");
      });
  };

  // Удаление мембера из таска
  const removeMemberFromTask = (userId) => {
    if (readOnly || !isMember()) return;
    
    axios
      .post(
        `${serverUrl}api/tasks/${task.id}/remove-responsible/`,
        { user_id: userId },
        {
          withCredentials: true,
          headers: {
            "X-CSRFToken": csrfToken,
          }
        }
      )
      .then((res) => {
        const updatedTaskMembers = taskMembers.filter(m => m.id !== userId);
        setTaskMembers(updatedTaskMembers);
        
        const updatedTask = {
          ...task,
          responsible: updatedTaskMembers
        };
        if (updateTask) updateTask(columnId, updatedTask);
      })
      .catch((err) => {
        console.error("Ошибка удаления участника:", err);
        alert("Не удалось удалить участника");
      });
  };

  // Позиционирование выпадающего меню
  const getDropdownPosition = () => {
    if (!memberButtonRef.current) return {};
    
    const rect = memberButtonRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const dropdownHeight = 400; // примерная высота
    
    // Определяем, где больше места - сверху или снизу
    const spaceBelow = viewportHeight - rect.bottom;
    const spaceAbove = rect.top;
    
    let top, transformOrigin;
    
    if (spaceBelow >= dropdownHeight || spaceBelow >= spaceAbove) {
      // Показываем снизу
      top = rect.bottom + 8;
      transformOrigin = "top center";
    } else {
      // Показываем сверху
      top = rect.top - dropdownHeight - 8;
      transformOrigin = "bottom center";
    }
    
    return {
      position: 'fixed',
      top: `${top}px`,
      left: `${rect.left + rect.width / 2}px`,
      transform: 'translateX(-50%)',
      transformOrigin: transformOrigin
    };
  };

  return (
    <>
      <div className="task-container" style={style}>
        <div
          ref={setNodeRef}
          className="sortable-task task-header"
          style={{
            cursor: isDragging ? "grabbing" : "grab",
            backgroundColor: getPriorityColor(priority),
          }}
        >
          {isRenaming ? (
            <div className="task-rename-container" onClick={(e) => e.stopPropagation()}>
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleRename();
                  if (e.key === 'Escape') cancelRename();
                }}
                autoFocus
                className="task-rename-input"
              />
              <button onClick={handleRename} className="rename-confirm-btn">
                ✓
              </button>
              <button onClick={cancelRename} className="rename-cancel-btn">
                ✕
              </button>
            </div>
          ) : (
            <div className="task-header-inner">
              <div {...attributes} {...listeners} className="drag-handle task-name">
                {task.title}
              </div>

              <div className="task-header-buttons">
                {isMember() && updateTaskTitle && (
                  <button
                    className="rename-task-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsRenaming(true);
                    }}
                    title="Переименовать задачу"
                  >
                    <img className='renameIcon' src={renameIcon} alt="Переименовать" />
                  </button>
                )}

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
          )}
        </div>

        <div className="task-content">
          {/* Первая строка: круглые кнопки */}
          <div className="task-buttons-row-first">
            <button
              className="task-btn-circle description-btn"
              onClick={() => {
                if (description) {
                  setShowDescriptionOverlay(true);
                } else {
                  setShowEditor(true);
                }
              }}
              title="Показать/редактировать описание"
            >
              <img className='textIcon' src={textIcon} alt="Описание" />
            </button>

            <button
              className={`task-btn-circle files-btn ${files.length > 0 ? "has-files" : ""}`}
              onClick={() => setShowFiles(!showFiles)}
              title="Показать/скрыть файлы"
            >
              <img className='fileIcon' src={fileIcon} alt="Файлы" />
              {files.length > 0 && <span className="files-badge">{files.length}</span>}
            </button>

            {/* Кнопка комментариев всегда показывается */}
            <button
              className={`task-btn-circle comments-btn ${showComments ? "active" : ""} ${task.comments?.length > 0 ? "has-comments" : ""}`}
              onClick={() => setShowComments(!showComments)}
              title={task.comments?.length > 0 ? `Комментарии (${task.comments.length})` : "Добавить комментарий"}
            >
              <img className='commentIcon' src={commentIcon} alt="Комментарии" />
              {task.comments?.length > 0 && <span className="comments-badge">{task.comments.length}</span>}
            </button>

            {/* Кнопка ответственных */}
            <div className="task-btn-circle-container">
              <button
                ref={memberButtonRef}
                className={`task-btn-circle members-btn ${taskMembers.length > 0 ? "has-members" : ""}`}
                onClick={() => setShowMember(!showMember)}
                title={taskMembers.length > 0 ? `Ответственные (${taskMembers.length})` : "Добавить ответственного"}
              >
                <img className='userIcon' src={userIcon} alt="Ответственные" />
                {taskMembers.length > 0 && <span className="members-badge">{taskMembers.length}</span>}
              </button>
            </div>
          </div>

          {/* Вторая строка: дедлайн и приоритет */}
          <div className="task-buttons-row-second">
            <div className="deadline-section">
              <div className="deadline-icon-container">
                <DeadlineButton
                  taskId={task.id}
                  initialDeadline={task.deadline}
                  csrfToken={csrfToken}
                  onDeadlineChange={handleDeadlineChange}
                  readOnly={readOnly}
                  customButton={DeadlineIconButton}
                  showLabel={true}
                />
              </div>
            </div>

            <div className="priority-container">
              <button
                className="task-btn priority-btn"
                onClick={() => isMember() && setShowPriority(!showPriority)}
                title="Изменить приоритет"
                style={{
                  backgroundColor: getPriorityColor(priority),
                  color: priority === "average" ? "#212529" : "white",
                  border: "none",
                }}
              >
                {getPriorityName(priority)}
                <span className={`priority-arrow ${showPriority ? "open" : ""}`}>
                  {showPriority ? "▲" : "▼"}
                </span>
              </button>

              {showPriority && isMember() && (
                <div className="priority-dropdown">
                  <button
                    className={`priority-item low ${priority === "low" ? "active" : ""}`}
                    onClick={() => changePriority("low")}
                  >
                    Низкий
                  </button>
                  <button
                    className={`priority-item average ${priority === "average" ? "active" : ""}`}
                    onClick={() => changePriority("average")}
                  >
                    Средний
                  </button>
                  <button
                    className={`priority-item high ${priority === "high" ? "active" : ""}`}
                    onClick={() => changePriority("high")}
                  >
                    Высокий
                  </button>
                  <button
                    className={`priority-item maximal ${priority === "maximal" ? "active" : ""}`}
                    onClick={() => changePriority("maximal")}
                  >
                    Максимум
                  </button>
                </div>
              )}
            </div>
          </div>

          {showFiles && (
            <div className="files-dropdown">
              <div className="files-dropdown-content">
                <label className="file-upload-label">
                  <input
                    type="file"
                    onChange={handleFileChange}
                    style={{ display: "none" }}
                  />
                  <span className="upload-file-btn">+ Загрузить файл</span>
                </label>

                {loadingFiles ? (
                  <div className="loading-files">Загрузка файлов...</div>
                ) : files.length > 0 ? (
                  <div className="files-list">
                    {files.map((file) => (
                      <div key={file.id} className="file-item">
                        <a
                          href={file.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="file-link"
                          title={`Загружено: ${formatDate(file.uploaded_at)}\n${file.uploaded_by_username}`}
                        >
                          <span className="file-icon">📎</span>
                          <span className="file-name">
                            {file.file_name || file.file.split("/").pop()}
                          </span>
                        </a>

                        {isMember() && (
                          <button
                            className="delete-file-btn"
                            onClick={() => deleteFile(file.id)}
                            title="Удалить файл"
                          >
                            ×
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-files">Файлы отсутствуют</div>
                )}
              </div>
            </div>
          )}

          {/* Поле добавления комментария - только если комменты открыты */}
          {isMember() && showComments && (
            <div className="add-comment">
              <input
                type="text"
                placeholder="Добавить комментарий..."
                value={newCommentTitle}
                onChange={(e) => setNewCommentTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") addCommentHandler();
                }}
              />
              <button onClick={addCommentHandler}>Отправить</button>
            </div>
          )}

          {task.comments && task.comments.length > 0 && showComments && (
            <div className="comments-section">
              <div className="comments-section-header">
                <span className="comments-count">
                  Комментарии ({task.comments.length})
                </span>
              </div>
              <div className="comments-list">
                {task.comments.map((comment) => (
                  <div key={comment.id} className="comment-item">
                    <div className="comment-avatar">
                      {comment.user_username?.charAt(0) || "А"}
                    </div>
                    <div className="comment-content">
                      <div className="comment-header">
                        <strong className="comment-author">
                          {comment.user_username || comment.user?.username || "Аноним"}
                        </strong>
                        <span className="comment-date">
                          {formatDate(comment.created)}
                        </span>
                        {username && comment.user_username === username && (
                          <button
                            className="delete-comment-btn"
                            onClick={() => deleteCommentHandler(comment.id)}
                            title="Удалить комментарий"
                          >
                            ×
                          </button>
                        )}
                      </div>
                      <div className="comment-text">{comment.text}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Выпадающее меню ответственных - ВНЕ task-container */}
      {showMember && isMember() && (
        <div 
          ref={dropdownRef}
          className="members-dropdown"
          style={getDropdownPosition()}
        >
          <div className="members-dropdown-content">
            <div className="current-members">
              <h4>Ответственные:</h4>
              {taskMembers.length > 0 ? (
                <div className="task-members-list">
                  {taskMembers.map((member) => (
                    <div key={member.id} className="task-member-item">
                      <img
                        src={`${serverUrl}${member.avatar}`}
                        alt={member.username}
                        width={32}
                        height={32}
                        style={{ borderRadius: "50%" }}
                      />
                      <span>{member.username}</span>
                      <button
                        className="remove-task-member-btn"
                        onClick={() => removeMemberFromTask(member.id)}
                        title="Удалить"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-members">Нет ответственных</div>
              )}
            </div>
            
            <div className="available-members">
              <h4>Добавить участника:</h4>
              <div className="available-members-list">
                {boardMembers
                  .filter(member => !taskMembers.some(m => m.id === member.id))
                  .map((member) => (
                    <div key={member.id} className="available-member-item">
                      <img
                        src={`${serverUrl}${member.avatar}`}
                        alt={member.username}
                        width={32}
                        height={32}
                        style={{ borderRadius: "50%" }}
                      />
                      <span>{member.username}</span>
                      <button
                        className="add-task-member-btn"
                        onClick={() => addMemberToTask(member.id)}
                        title="Добавить"
                      >
                        +
                      </button>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {isMember() && showEditor && (
        <div
          className="tiptap-modal-overlay"
          onClick={() => setShowEditor(false)}
        >
          <div className="tiptap-modal" onClick={(e) => e.stopPropagation()}>
            <div className="tiptap-header">
              <h3>Редактирование описания: {task.title}</h3>
            </div>
            <TipTap
              initialContent={description}
              onSave={saveDescription}
              onClose={() => setShowEditor(false)}
            />
          </div>
        </div>
      )}

      {showDescriptionOverlay && description && (
        <div
          className="description-overlay"
          onClick={() => setShowDescriptionOverlay(false)}
        >
          <div
            className="description-content"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="description-header">
              <h3>Описание задачи: {task.title}</h3>
              <button
                className="close-description-btn"
                onClick={() => setShowDescriptionOverlay(false)}
              >
                ×
              </button>
            </div>
            <div
              className="description-text"
              dangerouslySetInnerHTML={{ __html: description }}
            />
            <div className="description-actions">
              {isMember() && (
                <button
                  className="edit-description-btn"
                  onClick={() => {
                    setShowDescriptionOverlay(false);
                    setShowEditor(true);
                  }}
                >
                  Редактировать
                </button>
              )}
              <button
                className="close-btn"
                onClick={() => setShowDescriptionOverlay(false)}
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Task;