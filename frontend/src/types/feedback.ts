// Feedback types matching backend models
export interface Feedback {
  paper_id: string;
  feedback_type: 'like' | 'dislike';
  timestamp?: string;
}

export interface FeedbackResponse {
  status: string;
  paper_id: string;
  feedback_type: string;
}
