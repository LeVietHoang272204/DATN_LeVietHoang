export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  theme: string;
  font_size: number;
  total_score: number;
  created_at: string;
}

export interface Document {
  id: number;
  title: string;
  document_number: string | null;
  document_type: string | null;
  legal_field: string | null;
  issuing_body: string | null;
  effective_date: string | null;
  expired_date: string | null;
  status: string;
  is_scanned: boolean;
  total_pages: number;
  processing_status: string;
  chunk_count: number;
  is_public: boolean;
  created_at: string;
}

export interface ChatSession {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  confidence_score: number | null;
  sources: string | null;
  created_at: string;
}

export interface SourceReference {
  document_title: string;
  document_number: string | null;
  chunk_text: string;
  relevance_score: number;
}

export interface Event {
  id: number;
  title: string;
  description: string | null;
  legal_field: string | null;
  start_time: string;
  end_time: string;
  is_active: boolean;
  max_questions: number;
  question_count: number;
  created_at: string;
}

export interface EventQuestion {
  id: number;
  question_text: string;
  options: string[];
  points: number;
}

export interface Template {
  id: number;
  name: string;
  category: string;
  description: string | null;
  fields: Array<{
    name: string;
    label: string;
    type: string;
    required?: boolean;
  }>;
  is_active: boolean;
  created_at: string;
}

export interface MediaFile {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string | null;
  file_size: number;
  cloudinary_url: string | null;
  processing_status: string;
  is_indexed: boolean;
  created_at: string;
}
