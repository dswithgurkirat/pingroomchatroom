"use client";

import { useState } from "react";
import { Room, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import Link from "next/link";
import { Hash, Plus, LogOut, MessageSquare, LayoutDashboard } from "lucide-react";

interface SidebarProps {
  rooms: Room[];
  activeRoomId: string | null;
  onSelectRoom: (roomId: string) => void;
  onRoomCreated: () => void;
}

export function Sidebar({
  rooms,
  activeRoomId,
  onSelectRoom,
  onRoomCreated,
}: SidebarProps) {
  const { user, logout } = useAuth();
  const [newRoomName, setNewRoomName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleCreateRoom = async () => {
    if (!newRoomName.trim()) return;

    setIsCreating(true);
    try {
      await api.createRoom(newRoomName.trim());
      setNewRoomName("");
      setDialogOpen(false);
      onRoomCreated();
    } catch (error) {
      console.error("Failed to create room:", error);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="flex h-full w-64 flex-col bg-sidebar border-r border-sidebar-border">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-sidebar-border p-4">
        <MessageSquare className="h-6 w-6 text-primary" />
        <h1 className="text-xl font-bold text-sidebar-foreground">PingRoom</h1>
      </div>

      {/* Navigation Links */}
      <div className="px-2 py-4 space-y-1">
        <Link href="/chat">
          <Button 
            variant="ghost" 
            className={`w-full justify-start gap-2 ${activeRoomId ? 'text-sidebar-foreground' : 'bg-sidebar-accent text-sidebar-accent-foreground'}`}
          >
            <MessageSquare className="h-4 w-4" />
            Chat
          </Button>
        </Link>
        <Link href="/dashboard">
          <Button variant="ghost" className="w-full justify-start gap-2 text-sidebar-foreground">
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </Button>
        </Link>
      </div>

      {/* Rooms List */}
      <div className="flex-1 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Rooms
          </span>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" size="icon" className="h-6 w-6">
                <Plus className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Room</DialogTitle>
              </DialogHeader>
              <div className="flex gap-2 pt-4">
                <Input
                  placeholder="Room name"
                  value={newRoomName}
                  onChange={(e) => setNewRoomName(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleCreateRoom()}
                />
                <Button onClick={handleCreateRoom} disabled={isCreating}>
                  {isCreating ? "Creating..." : "Create"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <ScrollArea className="h-[calc(100%-48px)]">
          <div className="space-y-1 px-2">
            {rooms.map((room) => (
              <button
                key={room.id}
                onClick={() => onSelectRoom(room.id)}
                className={`flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors ${
                  activeRoomId === room.id
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent/50"
                }`}
              >
                <Hash className="h-4 w-4 shrink-0 text-muted-foreground" />
                <span className="truncate">{room.name}</span>
              </button>
            ))}
            {rooms.length === 0 && (
              <p className="px-3 py-2 text-sm text-muted-foreground">
                No rooms yet. Create one!
              </p>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* User Section */}
      <div className="border-t border-sidebar-border p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
              {user?.email?.charAt(0).toUpperCase() || "U"}
            </div>
            <span className="text-sm font-medium text-sidebar-foreground truncate max-w-[120px]">
              {user?.email || "User"}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={logout}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
