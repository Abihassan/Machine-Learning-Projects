export interface SourceReference {
  pmid: string;
  title: string;
  snippet: string;
}

export interface QueryResponse {
  answer: string;
  sources: SourceReference[];
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  sources?: SourceReference[];
  error?: boolean;
}