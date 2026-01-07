const [tasks, setTasks] = useState([]);
// Функция для добавления коммента
  const addCommentToTask = (TaskId, newComment) => {
    setColumns((prev) =>
      prev.map((task) =>
        task.id === TaskId ? { ...task, comments: [...task.comments, newComment] } : task
      )
    );
  };





const [newCommentTitle, setNewCommentTitle] = useState("");

const addCommentHandler = () => {
    if (!newCommentTitle.trim()) return;

    fetch(`${process.env.REACT_APP_API_URL}tasks/${task.id}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
      body: JSON.stringify({ title: newCommentTitle }),
    })
      .then((res) => res.json())
      .then((data) => {
        addTask(column.id, data);
        setNewCommentTitle("");
        setShowInput(false);
      })
      .catch(console.error);
  };