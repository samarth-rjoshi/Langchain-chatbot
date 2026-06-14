import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Thread {
  thread_id: string;
  headline: string;
  timestamp: string;
}

export interface UserThreadsResponse {
  userId: string;
  threads: Thread[];
}

export interface ThreadHistoryResponse {
  question: string[];
  generation: string[];
  timestamp?: string;
  error?: string;
}

export interface QueryResponse {
  answer: string;
  headline?: string;
  error?: string;
}

export interface Conversation {
  id: string;
  name: string;
  timestamp: Date;
  messages: Message[];
}

export interface Message {
  sender: 'user' | 'bot';
  text: string;
  time: string;
  isLoading?: boolean;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly apiBase = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  async getUserThreads(): Promise<UserThreadsResponse> {
    return firstValueFrom(
      this.http.get<UserThreadsResponse>(`${this.apiBase}/user_threads`, { withCredentials: true })
    );
  }

  async getThreadHistory(threadId: string): Promise<ThreadHistoryResponse> {
    return firstValueFrom(
      this.http.post<ThreadHistoryResponse>(`${this.apiBase}/thread_history`, { thread_id: threadId }, { withCredentials: true })
    );
  }

  async sendQuery(question: string, threadId: string): Promise<QueryResponse> {
    return firstValueFrom(
      this.http.post<QueryResponse>(`${this.apiBase}/query`, { question, thread_id: threadId }, { withCredentials: true })
    );
  }

  async deleteThread(threadId: string): Promise<any> {
    return firstValueFrom(
      this.http.post<any>(`${this.apiBase}/delete_thread`, { thread_id: threadId }, { withCredentials: true })
    );
  }
}
