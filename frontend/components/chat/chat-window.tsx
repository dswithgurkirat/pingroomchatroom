"use client";

import { useState, useEffect, useCallback } from "react";
import { Room, Message, api } from "@/lib/api";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { Hash, Users } from "lucide-react";

interface ChatWindowProps {
  room: Room | null;
}

export function ChatWindow({ room }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchMessages = useCallback(async () => {
    if (!room) return;

    setIsLoading(true);
    try {
      const data = await api.getMessages(room.id);
      setMessages(data);
    } catch (error) {
      console.error("Failed to fetch messages:", error);
    } finally {
      setIsLoading(false);
    }
  }, [room]);

  useEffect(() => {
    fetchMessages();
    
    // Poll for new messages every 3 seconds
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, [fetchMessages]);

  const handleSendMessage = async (message: string) => {
    if (!room) return;

    const newMessage = await api.sendMessage(room.id, message);
    setMessages((prev) => [...prev, newMessage]);
  };

  if (!room) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">Welcome to PingRoom</h2>
            <p className="mt-1 text-muted-foreground">
              Select a room from the sidebar to start chatting
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col bg-background">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <Hash className="h-5 w-5 text-muted-foreground" />
        <h2 className="text-lg font-semibold text-foreground">{room.name}</h2>
      </div>

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input */}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
}
