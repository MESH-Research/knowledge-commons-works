import axios from "axios";

const apiClient = axios.create({
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

apiClient.interceptors.request.use((config) => {
  let csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
  if (!csrfToken) {
    const match = document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'));
    if (match) {
      csrfToken = match[2];
    }
  }
  if (csrfToken) {
    config.headers["X-CSRFToken"] = csrfToken;
  }
  return config;
});

export default apiClient;