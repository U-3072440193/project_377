<div align="center" style="
  background: linear-gradient(#040607 0%, #333 50%, #2a2a2a 100%);
  padding: 50px 20px;
  border-radius: 0 0 20px 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  color: white;
  margin-bottom: 40px;
">

<h1 style="
  font-size: 3em;
  margin: 0 0 10px 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
">
  
  <img src="https://raw.githubusercontent.com/U-3072440193/project_377/master/shishka/static/images/logo.svg" 
       alt="Logo" 
       style="height: 60px; width: auto; filter: drop-shadow(0 0 8px rgba(76, 175, 80, 0.3));">
  <span style="color: #4caf50;">Project 377</span>
</h1>

<p style="
  font-size: 1.2em;
  opacity: 0.9;
  margin: 15px 0 30px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
">
  <strong>Project 377</strong> — учебно-практический fullstack-проект для управления задачами по методологии Kanban.
Проект разрабатывается как единое приложение на Django + React с упором на работу с API, ролями пользователей и real-time взаимодействием.
</p>

<div style="
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
">
  <span style="background: rgba(76, 175, 80, 0.2); padding: 6px 15px; border-radius: 20px; border: 1px solid rgba(76, 175, 80, 0.3);">
    🚀 Django 4 + React 19
  </span>
  <span style="background: rgba(33, 150, 243, 0.2); padding: 6px 15px; border-radius: 20px; border: 1px solid rgba(33, 150, 243, 0.3);">
    ⚡ WebSocket Real-time
  </span>
  <span style="background: rgba(156, 39, 176, 0.2); padding: 6px 15px; border-radius: 20px; border: 1px solid rgba(156, 39, 176, 0.3);">
    🎨 TipTap Editor
  </span>
</div>

</div>

## ✨ Ключевые возможности

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px,1fr)); gap: 20px; margin: 30px 0;">

<div style="background:#f8f9fa;padding:20px;border-radius:12px;color:#333;">
<h3>📋 Управление задачами</h3>
<ul>
<li>Kanban-доски с колонками и задачами</li>
<li>Drag-and-drop перемещение</li>
<li>Rich-text редактор задач (TipTap)</li>
<li>Загрузка файлов в задачи</li>
</ul>
</div>

<div style="background:#f8f9fa;padding:20px;border-radius:12px;color:#333;">
<h3>👥 Пользователи</h3>
<ul>
<li>Роли: владелец / участник</li>
<li>Комментарии к задачам</li>
<li>Подготовка real-time чата</li>
<li>Аутентификация пользователей</li>
</ul>
</div>

</div>

---

## 🛠 Технологический стек

<div style="display:flex;flex-wrap:wrap;gap:20px;margin:30px 0;">

<div style="flex:1;min-width:260px;background:white;padding:20px;border-radius:14px;color:#333;">
<h3>🎯 Frontend</h3>
<ul>
<li>React</li>
<li>@dnd-kit</li>
<li>TipTap</li>
<li>Axios</li>
<li>WebSocket API</li>
<li>CSS Modules</li>
</ul>
</div>

<div style="flex:1;min-width:260px;background:white;padding:20px;border-radius:14px;color:#333;">
<h3>⚙️ Backend</h3>
<ul>
<li>Django</li>
<li>Django REST Framework</li>
<li>Django Channels</li>
<li>Redis</li>
<li>SQLite (временно)</li>
</ul>
<p style="font-size:.9em;background:#fff8e1;padding:8px;border-radius:6px;">
Планируется переход на PostgreSQL
</p>
</div>

</div>

## 🚀 Запуск проекта локально

```bash
git clone https://github.com/U-3072440193/project_377.git
cd project_377

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

```

# backend
```
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

# frontend
```
cd frontend
npm install
npm run build
```
# запуск
```
cd ..
python manage.py runserver
```

<div style="flex:1;min-width:260px;background:white;padding:20px;border-radius:14px;color:#333;">
<h3>⚠️ Статус проекта</h3>
<ul>
<li>Фронтенд требует рефакторинга</li>
<li>WebSocket-функционал реализован частично (учебная реализация)</li>
<li>Дизайн не является финальным</li>
<li>Тесты пока отсутствуют</li>
</ul>
<div> ⚠️ <strong>Проект используется как учебно-практический и демонстрационный.
Основная цель — исследование архитектуры fullstack-приложения и интеграции
Django + React + WebSocket с дальнейшим развитием до production-уровня. </strong></div>
</div>

<div style="display:flex;flex-wrap:wrap;gap:20px;margin:30px 0;">

<div style="flex:1;min-width:260px;background:white;padding:20px;border-radius:14px;color:#333;">
<h3>📈 Планы развития</h3>
<ul>
<li>Рефакторинг backend- и frontend-архитектуры</li>
<li>Добавление unit-тестов</li>
<li>Внедрение TypeScript</li>
<li>Настройка CI/CD</li>
<li>Улучшение UI/UX</li>

</ul>
</div>

 Проект разрабатывается одним разработчиком в свободное время.

