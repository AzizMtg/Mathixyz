import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    if (error.response?.status === 404) {
      throw new Error('Resource not found');
    } else if (error.response?.status === 500) {
      throw new Error('Server error occurred');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out');
    } else if (!error.response) {
      throw new Error('Network error - please check if the backend is running');
    }
    
    throw new Error(error.response?.data?.detail || error.message || 'An error occurred');
  }
);

export interface UploadResponse {
  job_id: string;
  message: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  created_at: string;
  ocr_done: boolean;
  llm_done: boolean;
  lesson_built: boolean;
  lesson_id?: string;
  error?: string;
}

export interface LessonResponse {
  lesson_id: string;
  title: string;
  summary?: string;
  total_steps: number;
  steps: any[];
  created_at: string;
  job_id: string;
}

export const uploadImages = async (formData: FormData): Promise<UploadResponse> => {
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getJobStatus = async (jobId: string): Promise<JobStatusResponse> => {
  const response = await api.get(`/status/${jobId}`);
  return response.data;
};

export const getLesson = async (lessonId: string): Promise<LessonResponse> => {
  const response = await api.get(`/lesson/${lessonId}`);
  return response.data;
};

export default api;
