import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL, // например http://127.0.0.1:8000/api/
  withCredentials: true,                 // важно! отправляем куки вместе с запросами
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;