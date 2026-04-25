const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface User {
  id: string;       // mapped from user_id
  email: string;
  role: string;
}

export interface Room {
  id: string;
  name: string;
  created_at: string;
}

export interface Message {
  id: string;
  message: string;
  room_id: string;
  user_id: string;
  username: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

class ApiClient {
  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("token");
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "An error occurred" }));
      throw new Error(error.detail || "An error occurred");
    }

    return response.json();
  }

  // Auth endpoints
  // NOTE: backend accepts { email, password, full_name } — username is stored as full_name
  async signup(email: string, username: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, full_name: username, password }),
    });
  }

  async signin(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/signin", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async getMe(): Promise<User> {
    // Backend returns { user_id, email, role } — remap user_id → id
    const data = await this.request<{ user_id: string; email: string; role: string }>("/auth/me");
    return { id: data.user_id, email: data.email, role: data.role };
  }

  // Room endpoints
  async getRooms(): Promise<Room[]> {
    return this.request<Room[]>("/rooms");
  }

  async createRoom(name: string): Promise<Room> {
    return this.request<Room>("/rooms", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }

  async getRoom(roomId: string): Promise<Room> {
    return this.request<Room>(`/rooms/${roomId}`);
  }

  // Message endpoints
  async getMessages(roomId: string): Promise<Message[]> {
    const data = await this.request<{ messages: Message[]; total: number; page: number; page_size: number }>(
      `/messages/room/${roomId}`
    );
    return data.messages;
  }

  async sendMessage(roomId: string, message: string): Promise<Message> {
    return this.request<Message>("/messages", {
      method: "POST",
      body: JSON.stringify({ message, room_id: roomId }),
    });
  }

  // Stats endpoints
  async getStatsOverview(): Promise<{ total_rooms: number; total_messages: number; messages_today: number }> {
    return this.request("/stats/overview");
  }

  async getMessagesPerDay(): Promise<any[]> {
    return this.request("/stats/messages-per-day");
  }

  async getMessagesPerRoom(): Promise<any[]> {
    return this.request("/stats/messages-per-room");
  }
}

export const api = new ApiClient();
