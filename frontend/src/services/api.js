import axios from "axios";

/**
 * Pre-configured Axios instance for all backend API requests.
 * In development the Vite proxy forwards /api/* to FastAPI on port 8000.
 */
const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
