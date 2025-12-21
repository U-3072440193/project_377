import React, { useEffect, useState } from 'react';
import Main from './components/Main';

function App() {
  const user = window.currentUser || null;
  const [board, setBoard] = useState(null); // конкретная доска
  

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}boards/7/`) // обращаемся к Django API
      .then(response => response.json())
      .then(data => {
        console.log(data);  // джесон дя проверки магистрали данных
        setBoard(data);
      })
      .catch(err => console.error(err));
  }, []);
  

  return (
    <div>
      {/* Передаем данные доски и пользователя в Main */}
      <Main user={user} board={board} />
    </div>
  );
}

export default App;
