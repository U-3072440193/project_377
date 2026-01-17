// Task.js - полная версия с комментариями внизу
import React, { useState, useEffect } from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import TipTap from "./TipTap";

function Task({
  task,
  removeTask,
  columnId,
  isMember,
  updateTask,
  csrfToken,
  addCommentToTask,
}) {
  const [showEditor, setShowEditor] = useState(false);
  const [description, setDescription] = useState(task.description || "");
  const [showFiles, setShowFiles] = useState(false);
  const [showDescriptionOverlay, setShowDescriptionOverlay] = useState(false);
  const [files, setFiles] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [newCommentTitle, setNewCommentTitle] = useState("");
  const [showComments, setShowComments] = useState(false);

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

  const [showPriority, setShowPriority] = useState(false);
  const [priority, setPriority] = useState(task.priority || "low");

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    marginBottom: "8px",
  };

  useEffect(() => {
    fetchFiles();
  }, [task.id]);

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

  // Загрузка файла
  async function uploadFile(taskId, file) {
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

  // Удаление файла
  const deleteFile = async (fileId) => {
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

  // Изменение файла
  async function handleFileChange(e) {
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

  // Функция для сохранения описания
  const saveDescription = (htmlContent) => {
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
      
      // Автоматически показываем комментарии после добавления
      if (!showComments) {
        setShowComments(true);
      }
    } catch (err) {
      console.error("Ошибка добавления комментария:", err);
      alert("Не удалось добавить комментарий: " + err.message);
    }
  };
    // Функция для изменения приоритета
  const changePriority = async (newPriority) => {
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

  // Функция для получения цвета фона кнопки приоритета
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

  // Функция для получения названия приоритета
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

  return (
    <>
      <div className="task-container" style={style}>
        {/* Зеленое поле с названием и крестиком */}
        <div
          ref={setNodeRef}
          className="sortable-task task-header"
          style={{
            cursor: isDragging ? "grabbing" : "grab",
            backgroundColor: getPriorityColor(priority), // Изменяем фон на цвет приоритета
          }}
        >
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

        {/* Белая область с кнопками */}
        <div className="task-content">
          <div className="task-content-main">
            {/* Кнопки для описания и файлов */}
            <div className="task-buttons-row">
              <button
                className="description-btn"
                onClick={() => {
                  if (description) {
                    setShowDescriptionOverlay(true);
                  } else {
                    setShowEditor(true);
                  }
                }}
                title="Показать/редактировать описание"
              >
                {description ? "Описание" : "+ Добавить описание"}
              </button>

              <button
                className={`files-btn ${files.length > 0 ? "has-files" : ""}`}
                onClick={() => setShowFiles(!showFiles)}
                title="Показать/скрыть файлы"
              >
                Файлы {files.length > 0 && `(${files.length})`}
                <span className={`files-arrow ${showFiles ? "open" : ""}`}>
                  {showFiles ? "▲" : "▼"}
                </span>
              </button>

              {/* Кнопка комментариев */}
              {task.comments && task.comments.length > 0 && (
                <button
                  className={`comments-btn ${showComments ? "active" : ""}`}
                  onClick={() => setShowComments(!showComments)}
                  title="Показать/скрыть комментарии"
                >
                  Комментарии {task.comments.length}
                  <span className={`comments-arrow ${showComments ? "open" : ""}`}>
                    {showComments ? "▲" : "▼"}
                  </span>
                </button>
              )}

              {/* Кнопка приоритета */}
              <div className="priority-container">
                <button
                  className="priority-btn"
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

            {/* Поле добавления комментария */}
            {isMember() && (
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

            {/* Выпадающий список файлов */}
            {showFiles && (
              <div className="files-dropdown">
                <div className="files-dropdown-content">
                  {/* Кнопка загрузки файла */}
                  <label className="file-upload-label">
                    <input
                      type="file"
                      onChange={handleFileChange}
                      style={{ display: "none" }}
                    />
                    <span className="upload-file-btn">+ Загрузить файл</span>
                  </label>

                  {/* Список файлов */}
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
                            title={`Загружено: ${formatDate(
                              file.uploaded_at
                            )}\n${file.uploaded_by_username}`}
                          >
                            <span className="file-icon">
                              📎
                            </span>
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
          </div>

          {/* Список комментариев - ВНИЗУ ТАСКА */}
          {task.comments && task.comments.length > 0 && showComments && (
            <div className="comments-section">
              <div className="comments-section-header">
                <span className="comments-count">Комментарии ({task.comments.length})</span>
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

      {/* Модальное окно с редактором */}
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

      {/* Оверлей с описанием  */}
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