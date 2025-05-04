import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,

  // if using cookies for authentication, set withCredentials to true
  withCredentials: true 
});

export default api;
