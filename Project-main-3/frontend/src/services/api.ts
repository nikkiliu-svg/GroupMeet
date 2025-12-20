/**
 * API client for GroupMeet backend.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import { Submission, Match, Feedback, SubmissionData, FeedbackData } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for auth errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: () => {
    window.location.href = `${API_URL}/auth/login`;
  },
  logout: () => {
    window.location.href = `${API_URL}/auth/logout`;
  },
  getStatus: async () => {
    const response = await api.get('/auth/status');
    return response.data;
  },
};

// Submissions API
export const submissionsAPI = {
  create: async (data: SubmissionData): Promise<Submission> => {
    const response = await api.post<Submission>('/api/submissions', data);
    return response.data;
  },
  get: async (): Promise<Submission[]> => {
    const response = await api.get<Submission[]>('/api/submissions');
    return response.data;
  },
  getById: async (id: string): Promise<Submission> => {
    const response = await api.get<Submission>(`/api/submissions/${id}`);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/submissions/${id}`);
  },
};

// Matches API
export const matchesAPI = {
  get: async (course?: string): Promise<Match | null> => {
    const params = course ? { course } : {};
    try {
      const response = await api.get<Match>('/api/matches', { params });
      return response.data;
    } catch (error) {
      if ((error as AxiosError).response?.status === 404) {
        return null;
      }
      throw error;
    }
  },
  getById: async (id: string): Promise<Match> => {
    const response = await api.get<Match>(`/api/matches/${id}`);
    return response.data;
  },
  trigger: async (courseId: string): Promise<any> => {
    const response = await api.post('/api/matches/trigger', { course_id: courseId });
    return response.data;
  },
};

// Feedback API
export const feedbackAPI = {
  create: async (data: FeedbackData): Promise<Feedback> => {
    const response = await api.post<Feedback>('/api/feedback', data);
    return response.data;
  },
  get: async (matchId?: string): Promise<Feedback[]> => {
    const params = matchId ? { match_id: matchId } : {};
    const response = await api.get<Feedback[]>('/api/feedback', { params });
    return response.data;
  },
};

export default api;

