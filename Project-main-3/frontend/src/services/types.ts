/**
 * TypeScript interfaces for GroupMeet API.
 */

export interface User {
  pennkey: string;
  email?: string;
  name?: string;
  is_admin?: boolean;
}

export interface AuthStatus {
  authenticated: boolean;
  pennkey?: string;
  is_admin?: boolean;
}

export interface Submission {
  id?: string;
  pennkey: string;
  course: string;
  availability: string[];
  study_style: string;
  goal: string;
  preferred_group_size: number;
  status: 'pending' | 'validated' | 'matched';
  created_at?: string;
  validated_at?: string;
}

export interface Member {
  pennkey: string;
  email: string;
  name?: string;
}

export interface Match {
  match_id?: string;
  group_id: number;
  course: string;
  members: Member[];
  compatibility_score: number;
  suggested_meeting_time: string;
  created_at?: string;
  feedback_sent?: boolean;
  feedback_due_date?: string;
}

export interface Feedback {
  id?: string;
  match_id: string;
  pennkey: string;
  rating: number;
  comments?: string;
  met_with_group: boolean;
  would_meet_again: boolean;
  created_at?: string;
}

export interface SubmissionData {
  course: string;
  availability: string[];
  study_style: string;
  goal: string;
  preferred_group_size: number;
}

export interface FeedbackData {
  match_id: string;
  rating: number;
  comments?: string;
  met_with_group: boolean;
  would_meet_again: boolean;
}

