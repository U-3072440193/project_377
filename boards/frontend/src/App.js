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
    .then(data => {
      console.log(data);  // вот тут увидим все поля
      setEntitiesList(data);
    })
    .catch(err => console.error(err));
}, []);

  return (
    <div>
      <h1>Boards</h1>
      {entitiesList.map(board => (
        <div key={board.id} style={{border: '1px solid gray', padding: '10px', marginBottom: '10px'}}>
          <h2>{board.title}</h2>
          <p>Owner: {board.owner.username}</p>
          <p>Created: {board.created}</p>
          <p>Columns:</p>
          <ul>
            {board.columns.map(col => (
              <li key={col.id}>{col.title}</li>
            ))}
          </ul>
          <pre>{JSON.stringify(board, null, 2)}</pre> {/* Полный объект для дебага */}
        </div>
      ))}
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
