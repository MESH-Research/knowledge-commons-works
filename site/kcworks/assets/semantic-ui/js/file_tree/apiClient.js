import axios from "axios";

const apiClient = axios.create({
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
  if (csrfToken) {
    config.headers["X-CSRFToken"] = csrfToken;
  }
  return config;
});

export default apiClient;