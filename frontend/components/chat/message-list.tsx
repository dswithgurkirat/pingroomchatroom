"use client";

import { useEffect, useRef } from "react";
import { Message } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ScrollArea } from "@/components/ui/scroll-area";
import { format } from "date-fns";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const { user } = useAuth();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-sm text-muted-foreground">Loading messages...</span>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">No messages yet</p>
          <p className="text-sm text-muted-foreground">Be the first to say something!</p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 px-4">
      <div className="space-y-4 py-4">
        {messages.map((message) => {
          const isCurrentUser = message.user_id === user?.id;
          const timestamp = new Date(message.created_at);
          const formattedTime = format(timestamp, "HH:mm");
          const formattedDate = format(timestamp, "MMM d, yyyy");

          return (
            <div
              key={message.id}
              className={`flex ${isCurrentUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[70%] ${
                  isCurrentUser ? "order-2" : "order-1"
                }`}
              >
                <div className={`flex items-baseline gap-2 mb-1 ${isCurrentUser ? "justify-end" : "justify-start"}`}>
                  <span className="text-xs font-medium text-muted-foreground">
                    {isCurrentUser ? "You" : message.username}
                  </span>
                </div>
                <div
                  className={`rounded-2xl px-4 py-2 ${
                    isCurrentUser
                      ? "bg-primary text-primary-foreground rounded-br-md"
                      : "bg-muted text-foreground rounded-bl-md"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">{message.message}</p>
                </div>
                <div className={`mt-1 flex items-center gap-1 text-xs text-muted-foreground ${isCurrentUser ? "justify-end" : "justify-start"}`}>
                  <span>{formattedTime}</span>
                  <span>·</span>
                  <span>{formattedDate}</span>
                </div>
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
