import { Component, signal, OnInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth';
import { ChatService, Conversation, Message } from '../services/chat';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-chat',
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class Chat implements OnInit {
  messages = signal<Message[]>([]);
  userInput = '';
  isLoading = signal(false);
  conversations = signal<Conversation[]>([]);
  currentConversation = signal<Conversation | null>(null);
  isStreaming = signal(false);
  showPanel = signal(true);
  currentUser = signal('');

  @ViewChild('chatMessages') chatMessagesEl!: ElementRef;

  constructor(
    private authService: AuthService,
    private chatService: ChatService,
    private router: Router,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.currentUser.set(this.authService.getCurrentUser() || '');
    this.initUser();
  }

  async initUser(): Promise<void> {
    try {
      const data = await this.chatService.getUserThreads();
      if (data.threads && data.threads.length > 0) {
        const sorted = [...data.threads].sort((a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );

        const convs: Conversation[] = sorted.map(thread => ({
          id: thread.thread_id,
          name: thread.headline || 'New Conversation',
          timestamp: new Date(thread.timestamp),
          messages: []
        }));

        this.conversations.set(convs);
        this.currentConversation.set(convs[0]);
        this.selectConversation(convs[0]);
      } else {
        this.createNewChat();
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
      this.createNewChat();
    }
  }

  createNewChat(): void {
    const newConversation: Conversation = {
      id: crypto.randomUUID(),
      name: 'New Conversation',
      timestamp: new Date(),
      messages: []
    };

    this.conversations.update(convs => [newConversation, ...convs]);
    this.currentConversation.set(newConversation);

    const greeting = `Hello${this.authService.getCurrentUser() ? ', ' + this.authService.getCurrentUser() : ''}! I'm your Langchain chatbot. How can I help you today?`;
    this.messages.set([{
      sender: 'bot',
      text: greeting,
      time: this.formatTime(new Date())
    }]);
  }

  async selectConversation(conversation: Conversation): Promise<void> {
    this.currentConversation.set(conversation);
    this.isLoading.set(true);

    try {
      const data = await this.chatService.getThreadHistory(conversation.id);
      const msgs: Message[] = [];

      if (!data.error) {
        for (let i = 0; i < data.question.length; i++) {
          msgs.push({
            sender: 'user',
            text: data.question[i],
            time: this.formatTime(new Date(data.timestamp || Date.now()))
          });

          if (i < data.generation.length) {
            msgs.push({
              sender: 'bot',
              text: data.generation[i],
              time: this.formatTime(new Date(data.timestamp || Date.now()))
            });
          }
        }
      }

      if (msgs.length === 0) {
        const greeting = `Hello${this.authService.getCurrentUser() ? ', ' + this.authService.getCurrentUser() : ''}! I'm your Langchain chatbot. How can I help you today?`;
        msgs.push({
          sender: 'bot',
          text: greeting,
          time: this.formatTime(new Date())
        });
      }

      this.messages.set(msgs);
      setTimeout(() => this.scrollToBottom(), 100);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      this.isLoading.set(false);
    }
  }

  async deleteConversation(conversation: Conversation, event: Event): Promise<void> {
    event.stopPropagation();

    if (!confirm('Are you sure you want to delete this conversation?')) return;

    try {
      const response = await this.chatService.deleteThread(conversation.id);
      if (response.success) {
        this.conversations.update(convs => {
          const filtered = convs.filter(c => c.id !== conversation.id);
          return filtered;
        });

        if (this.currentConversation()?.id === conversation.id) {
          const remaining = this.conversations();
          if (remaining.length > 0) {
            this.selectConversation(remaining[0]);
          } else {
            this.createNewChat();
          }
        }
      }
    } catch (error) {
      console.error('Error deleting thread:', error);
    }
  }

  handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }

    // Auto-resize textarea
    const textarea = event.target as HTMLTextAreaElement;
    setTimeout(() => {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }, 0);
  }

  async sendMessage(): Promise<void> {
    if (!this.userInput.trim() || this.isStreaming()) return;

    const userMessageText = this.userInput;
    const userMessage: Message = {
      sender: 'user',
      text: userMessageText,
      time: this.formatTime(new Date())
    };

    this.messages.update(msgs => [...msgs, userMessage]);
    this.userInput = '';

    // Reset textarea height
    setTimeout(() => {
      const textarea = document.querySelector('.chat-input') as HTMLTextAreaElement;
      if (textarea) textarea.style.height = 'auto';
    }, 0);

    this.isLoading.set(true);
    this.isStreaming.set(true);

    setTimeout(() => this.scrollToBottom(), 100);

    // Ensure we have a current conversation
    if (!this.currentConversation()) {
      this.createNewChat();
    }

    const threadId = this.currentConversation()!.id;

    // Create placeholder for bot message
    const botMessage: Message = {
      sender: 'bot',
      text: '',
      time: this.formatTime(new Date()),
      isLoading: true
    };
    this.messages.update(msgs => [...msgs, botMessage]);

    try {
      const data = await this.chatService.sendQuery(userMessageText, threadId);

      this.messages.update(msgs => {
        const updated = [...msgs];
        const lastBot = updated.findLastIndex((m: Message) => m.isLoading);
        if (lastBot !== -1) {
          if (data.answer) {
            updated[lastBot] = { ...updated[lastBot], text: data.answer, isLoading: false };
          } else if (data.error) {
            updated[lastBot] = { ...updated[lastBot], text: 'Error: ' + data.error, isLoading: false };
          }
        }
        return updated;
      });

      this.isStreaming.set(false);

      // Update conversation name if it's new
      if (this.currentConversation()?.name === 'New Conversation' && data.headline) {
        const newName = data.headline;
        this.currentConversation.update(conv => conv ? { ...conv, name: newName } : conv);
        this.conversations.update(convs =>
          convs.map(c => c.id === threadId ? { ...c, name: newName } : c)
        );
      }

      setTimeout(() => this.scrollToBottom(), 100);
    } catch (error) {
      console.error('Error sending message:', error);
      this.messages.update(msgs => {
        const updated = [...msgs];
        const lastBot = updated.findLastIndex((m: Message) => m.isLoading);
        if (lastBot !== -1) {
          updated[lastBot] = {
            ...updated[lastBot],
            text: 'Sorry, I encountered an error. Please try again.',
            isLoading: false
          };
        }
        return updated;
      });
      this.isStreaming.set(false);
      setTimeout(() => this.scrollToBottom(), 100);
    } finally {
      this.isLoading.set(false);
    }
  }

  stopStreaming(): void {
    this.isStreaming.set(false);
  }

  async logout(): Promise<void> {
    await this.authService.logout();
    this.router.navigate(['/login']);
  }

  togglePanel(): void {
    this.showPanel.update(v => !v);
  }

  sanitizeHtml(html: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(html);
  }

  getInitial(): string {
    const user = this.currentUser();
    return user ? user.charAt(0).toUpperCase() : '?';
  }

  hasLoadingMessage(): boolean {
    const msgs = this.messages();
    return msgs.length > 0 && !!msgs[msgs.length - 1].isLoading;
  }

  private formatTime(date: Date): string {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  }

  private scrollToBottom(): void {
    const el = this.chatMessagesEl?.nativeElement;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }
}
