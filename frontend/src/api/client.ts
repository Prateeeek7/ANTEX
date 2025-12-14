import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// #region agent log
apiClient.interceptors.request.use((config) => {
  fetch('http://127.0.0.1:7242/ingest/1dc984c4-3203-4845-a007-ddc7ab7efb5e',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'client.ts:12',message:'API_REQUEST',data:{method:config.method,url:config.url,baseURL:config.baseURL,hasAuth:!!config.headers?.Authorization},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
  return config;
});
// #endregion

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling (auth disabled)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Auth disabled - no redirect to login
    return Promise.reject(error)
  }
)

export default apiClient


