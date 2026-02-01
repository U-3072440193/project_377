import React, { useState, useRef, useEffect } from "react";
import "./deadlinebutton.css";
import timeIcon from "../assets/images/time_w.svg";

const DeadlineButton = ({ 
  taskId, 
  initialDeadline, 
  csrfToken, 
  onDeadlineChange,
  readOnly = false,
  customButton,
  showLabel = true
}) => {
  const [deadline, setDeadline] = useState(
    initialDeadline ? new Date(initialDeadline) : null
  );
  const [isOpen, setIsOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [selectedDate, setSelectedDate] = useState("");
  const deadlineRef = useRef(null);

  // Инициализация при монтировании
  useEffect(() => {
    if (deadline) {
      const dateStr = deadline.toISOString().split('T')[0];
      setSelectedDate(dateStr);
    }
  }, [deadline]);

  const handleSave = async () => {
    if (readOnly || isSaving) return;
    
    try {
      setIsSaving(true);
      
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}tasks/${taskId}/deadline/`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          credentials: "include",
          body: JSON.stringify({
            deadline: deadline ? deadline.toISOString() : null,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Ошибка сохранения дедлайна");
      }

      const updatedTask = await response.json();
      
      if (onDeadlineChange) {
        onDeadlineChange(updatedTask);
      }
      
      setIsOpen(false);
    } catch (error) {
      console.error("Ошибка сохранения дедлайна:", error);
      alert("Не удалось сохранить дедлайн");
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemove = async () => {
    if (readOnly || isSaving) return;
    
    if (window.confirm("Удалить дедлайн?")) {
      try {
        setIsSaving(true);
        
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}tasks/${taskId}/deadline/`,
          {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
            credentials: "include",
            body: JSON.stringify({
              deadline: null,
            }),
          }
        );

        if (!response.ok) {
          throw new Error("Ошибка удаления дедлайна");
        }

        const updatedTask = await response.json();
        setDeadline(null);
        setSelectedDate("");
        
        if (onDeadlineChange) {
          onDeadlineChange(updatedTask);
        }
      } catch (error) {
        console.error("Ошибка удаления дедлайна:", error);
        alert("Не удалось удалить дедлайн");
      } finally {
        setIsSaving(false);
      }
    }
  };

  const handleDateChange = (e) => {
    const dateValue = e.target.value;
    setSelectedDate(dateValue);
    
    if (dateValue) {
      const newDate = new Date(dateValue);
      newDate.setHours(12, 0, 0, 0);
      setDeadline(newDate);
    } else {
      setDeadline(null);
    }
  };

  const formatDeadline = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
    });
  };

  const getTodayString = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  // Закрытие попапа при клике вне его
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (deadlineRef.current && !deadlineRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Если передана кастомная кнопка, используем её
  if (customButton) {
    const CustomButtonComponent = customButton;
    const formattedDeadline = deadline ? formatDeadline(deadline) : null;
    
    return (
      <div className="deadline-container" ref={deadlineRef}>
        <div className="deadline-section">
          <CustomButtonComponent
            onClick={() => !readOnly && setIsOpen(!isOpen)}
            title={formattedDeadline ? `Дедлайн: ${formattedDeadline}` : "Установить дедлайн"}
            hasDeadline={!!deadline}
          />
          
          {/* Метка с датой дедлайна */}
          {showLabel && formattedDeadline && (
            <span className="deadline-label">
              {formattedDeadline}
            </span>
          )}
        </div>
        
        {isOpen && !readOnly && (
          <div className="deadline-popup">
            <div className="deadline-popup-content">
              <div className="deadline-popup-header">
                <h4>Установить дедлайн</h4>
                <button 
                  className="close-popup-btn"
                  onClick={() => setIsOpen(false)}
                  aria-label="Закрыть"
                >
                  ×
                </button>
              </div>
              
              <div className="date-input-container">
                <label htmlFor="deadline-date-input">
                  Выберите дату:
                </label>
                <input
                  id="deadline-date-input"
                  type="date"
                  value={selectedDate}
                  onChange={handleDateChange}
                  min={getTodayString()}
                  className="date-input"
                />
              </div>
              
              <div className="date-preview">
                {selectedDate ? (
                  <div className="selected-date-info">
                    <strong>Выбранная дата:</strong><br />
                    {new Date(selectedDate).toLocaleDateString('ru-RU', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                      weekday: 'long'
                    })}
                  </div>
                ) : (
                  <div className="no-date-info">
                    Дата не выбрана
                  </div>
                )}
              </div>
              
              <div className="deadline-popup-actions">
                <button 
                  onClick={handleSave} 
                  disabled={isSaving || !selectedDate}
                  className="save-btn"
                >
                  {isSaving ? "Сохранение..." : "Установить"}
                </button>
                
                {deadline && (
                  <button 
                    onClick={handleRemove} 
                    disabled={isSaving}
                    className="remove-btn"
                  >
                    Удалить
                  </button>
                )}
                
                <button 
                  onClick={() => setIsOpen(false)} 
                  disabled={isSaving}
                  className="cancel-btn"
                >
                  Отмена
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Стандартная кнопка (скрыта, используется только через customButton)
  return (
    <div className="deadline-container" ref={deadlineRef}>
      <button
        className={`deadline-btn ${deadline ? "has-deadline" : ""}`}
        onClick={() => !readOnly && setIsOpen(!isOpen)}
        title={deadline ? `Дедлайн: ${formatDeadline(deadline)}` : "Установить дедлайн"}
        disabled={readOnly}
        style={{ display: 'none' }}
      >
        <img className='timeIcon' src={timeIcon} alt="Дедлайн" /> {deadline ? formatDeadline(deadline) : "Дедлайн"}
      </button>

      {isOpen && !readOnly && (
        <div className="deadline-popup">
          <div className="deadline-popup-content">
            <div className="deadline-popup-header">
              <h4>Установить дедлайн</h4>
              <button 
                className="close-popup-btn"
                onClick={() => setIsOpen(false)}
                aria-label="Закрыть"
              >
                ×
              </button>
            </div>
            
            <div className="date-input-container">
              <label htmlFor="deadline-date-input">
                Выберите дату:
              </label>
              <input
                id="deadline-date-input"
                type="date"
                value={selectedDate}
                onChange={handleDateChange}
                min={getTodayString()}
                className="date-input"
              />
            </div>
            
            <div className="date-preview">
              {selectedDate ? (
                <div className="selected-date-info">
                  <strong>Выбранная дата:</strong><br />
                  {new Date(selectedDate).toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    weekday: 'long'
                  })}
                </div>
              ) : (
                <div className="no-date-info">
                  Дата не выбрана
                </div>
              )}
            </div>
            
            <div className="deadline-popup-actions">
              <button 
                onClick={handleSave} 
                disabled={isSaving || !selectedDate}
                className="save-btn"
              >
                {isSaving ? "Сохранение..." : "Установить"}
              </button>
              
              {deadline && (
                <button 
                  onClick={handleRemove} 
                  disabled={isSaving}
                  className="remove-btn"
                >
                  Удалить
                </button>
              )}
              
              <button 
                onClick={() => setIsOpen(false)} 
                disabled={isSaving}
                className="cancel-btn"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DeadlineButton;