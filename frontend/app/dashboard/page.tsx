"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Sidebar } from "@/components/chat/sidebar";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  ChartContainer, 
  ChartTooltip, 
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent
} from "@/components/ui/chart";
import { 
  Area, 
  AreaChart, 
  Bar, 
  BarChart, 
  CartesianGrid, 
  XAxis, 
  YAxis,
  ResponsiveContainer 
} from "recharts";
import { 
  MessageSquare, 
  Users, 
  Zap, 
  Loader2,
  TrendingUp,
  LayoutDashboard
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [overview, setOverview] = useState({ total_rooms: 0, total_messages: 0, messages_today: 0 });
  const [dailyData, setDailyData] = useState([]);
  const [roomData, setRoomData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      const fetchData = async () => {
        try {
          const [ov, daily, rooms] = await Promise.all([
            api.getStatsOverview(),
            api.getMessagesPerDay(),
            api.getMessagesPerRoom()
          ]);
          setOverview(ov);
          setDailyData(daily);
          setRoomData(rooms);
        } catch (error) {
          console.error("Failed to fetch dashboard data:", error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchData();
    }
  }, [isAuthenticated]);

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const chartConfig = {
    messages: {
      label: "Messages",
      color: "hsl(var(--primary))",
    },
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar 
        rooms={[]} 
        activeRoomId={null} 
        onSelectRoom={() => router.push("/chat")} 
        onRoomCreated={() => {}} 
      />
      
      <main className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-7xl space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
              <p className="text-muted-foreground">Welcome to your PingRoom analytics.</p>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
              <TrendingUp className="h-4 w-4" />
              Live Updates
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="relative overflow-hidden border-none bg-gradient-to-br from-primary/10 to-transparent shadow-md">
              <CardHeader className="pb-2">
                <CardDescription className="text-primary/70">Total Messages</CardDescription>
                <CardTitle className="text-4xl font-bold">{overview.total_messages}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xs text-muted-foreground">Across all rooms</div>
              </CardContent>
              <MessageSquare className="absolute -bottom-2 -right-2 h-20 w-20 text-primary/5" />
            </Card>
            
            <Card className="relative overflow-hidden border-none bg-gradient-to-br from-blue-500/10 to-transparent shadow-md">
              <CardHeader className="pb-2">
                <CardDescription className="text-blue-500/70">Total Rooms</CardDescription>
                <CardTitle className="text-4xl font-bold">{overview.total_rooms}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xs text-muted-foreground">Active discussions</div>
              </CardContent>
              <Users className="absolute -bottom-2 -right-2 h-20 w-20 text-blue-500/5" />
            </Card>

            <Card className="relative overflow-hidden border-none bg-gradient-to-br from-orange-500/10 to-transparent shadow-md">
              <CardHeader className="pb-2">
                <CardDescription className="text-orange-500/70">Today's Activity</CardDescription>
                <CardTitle className="text-4xl font-bold">{overview.messages_today}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xs text-muted-foreground">New messages today</div>
              </CardContent>
              <Zap className="absolute -bottom-2 -right-2 h-20 w-20 text-orange-500/5" />
            </Card>
          </div>

          <div className="grid gap-8 md:grid-cols-2">
            {/* Area Chart */}
            <Card className="glass-morphism border border-border/50">
              <CardHeader>
                <CardTitle>Messaging Trends</CardTitle>
                <CardDescription>Messages sent over the last 7 days</CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                <ChartContainer config={chartConfig}>
                  <AreaChart data={dailyData}>
                    <defs>
                      <linearGradient id="colorMsgs" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--color-messages)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="var(--color-messages)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid vertical={false} strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis 
                      dataKey="date" 
                      axisLine={false}
                      tickLine={false}
                      tick={{fill: 'hsl(var(--muted-foreground))', fontSize: 12}}
                    />
                    <YAxis 
                      axisLine={false}
                      tickLine={false}
                      tick={{fill: 'hsl(var(--muted-foreground))', fontSize: 12}}
                    />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Area 
                      type="monotone" 
                      dataKey="messages" 
                      stroke="var(--color-messages)" 
                      fillOpacity={1} 
                      fill="url(#colorMsgs)" 
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Bar Chart */}
            <Card className="glass-morphism border border-border/50">
              <CardHeader>
                <CardTitle>Room Activity</CardTitle>
                <CardDescription>Total messages by room</CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                <ChartContainer config={chartConfig}>
                  <BarChart data={roomData} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid horizontal={false} strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis type="number" hide />
                    <YAxis 
                      dataKey="room" 
                      type="category" 
                      axisLine={false}
                      tickLine={false}
                      tick={{fill: 'hsl(var(--muted-foreground))', fontSize: 12}}
                      width={100}
                    />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar 
                      dataKey="messages" 
                      fill="var(--color-messages)" 
                      radius={[0, 4, 4, 0]} 
                    />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
