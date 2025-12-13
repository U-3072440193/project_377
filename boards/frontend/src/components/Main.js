import React from "react";
import { Link } from "react-router-dom";

function Main({ user }) {
  return (
    <header className="site-header">
      <div className="container">
        <Link to="/" className="logo">
          <img src="http://127.0.0.1:8000/static/images/logo.svg" alt="Shishka Logo" />
        </Link>

        <nav className="main-nav">
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/boards">Boards</Link></li>
            <li><Link to="/tasks">Tasks</Link></li>
            <li><Link to="/users">Users</Link></li>
          </ul>
        </nav>

        <div className="user-menu">
          {user ? (
            <div className="user-info">
              <Link to="/profile" className="user-link">
                <img src={user.avatar || "/default-avatar.png"} alt={user.username} className="avatar" />
                <span className="username">{user.username}</span>
              </Link>
              <Link to="/logout" className="logout-btn">Выйти</Link>
            </div>
          ) : (
            <Link to="/login" className="login-btn">Войти</Link>
          )}
        </div>
      </div>
    </header>
  );
}

export default Main;
