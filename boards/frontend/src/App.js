import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Main from './components/Main';

function Home() {
  return <h1>Джанго шаблон</h1>;
}

function Boards() {
  const [entitiesList, setEntitiesList] = useState([]);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}boards/`)
      .then(response => response.json())
      .then(data => setEntitiesList(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h1>Boards</h1>
      <ul>
        {entitiesList.map(board => (
          <li key={board.id}>
            {board.title} — Владелец: {board.owner.username}
          </li>
        ))}
      </ul>
      <ul>
        {entitiesList.map(board => (
          <li key={board.id}>{board.title}</li>
        ))}
      </ul>
    </div>
  );
}

function App() {
  const user = null;

  return (
    <>
      <Main user={user} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/boards" element={<Boards />} />
      </Routes>
    </>
  );
}

export default App;
