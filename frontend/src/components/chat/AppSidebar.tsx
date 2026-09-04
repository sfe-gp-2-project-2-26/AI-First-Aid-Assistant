import { Plus, MessageSquare, LogOut, User as UserIcon, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Link } from "@tanstack/react-router";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
} from "@/components/ui/sidebar";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";

type Conversation = {
  _id: string;
  title: string;
  updated_at: string;
};

interface AppSidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onRename: (id: string, newTitle: string) => void;
  onDelete: (id: string) => void;
}

export function AppSidebar({ conversations, activeId, onSelect, onNewChat, onRename, onDelete }: AppSidebarProps) {
  const { user, logout } = useAuth();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  const handleEditStart = (e: React.MouseEvent, id: string, title: string) => {
    e.stopPropagation();
    setEditingId(id);
    setEditTitle(title);
  };

  const handleEditSubmit = (e: React.FormEvent, id: string) => {
    e.preventDefault();
    if (editTitle.trim()) {
      onRename(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleEditKeyDown = (e: React.KeyboardEvent, id: string) => {
    if (e.key === "Escape") {
      setEditingId(null);
    }
  };

  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <h2 className="text-lg font-semibold tracking-tight">MedAid</h2>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <div className="px-4 py-2">
            <Button onClick={onNewChat} className="w-full justify-start gap-2" variant="outline">
              <Plus className="h-4 w-4" />
              New Chat
            </Button>
          </div>
          
          <SidebarGroupLabel>Recent Conversations</SidebarGroupLabel>
          <SidebarGroupContent>
            {user ? (
              <SidebarMenu>
                {conversations.map((conv) => (
                  <SidebarMenuItem key={conv._id}>
                    <SidebarMenuButton 
                      isActive={activeId === conv._id}
                      onClick={() => onSelect(conv._id)}
                    >
                      <MessageSquare className="mr-2 h-4 w-4 shrink-0" />
                      {editingId === conv._id ? (
                        <form onSubmit={(e) => handleEditSubmit(e, conv._id)} className="flex-1" onClick={e => e.stopPropagation()}>
                          <Input
                            autoFocus
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onKeyDown={(e) => handleEditKeyDown(e, conv._id)}
                            onBlur={(e) => handleEditSubmit(e, conv._id)}
                            className="h-6 text-sm px-1 py-0 w-full"
                          />
                        </form>
                      ) : (
                        <span className="truncate">{conv.title}</span>
                      )}
                    </SidebarMenuButton>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <SidebarMenuAction showOnHover>
                          <MoreHorizontal />
                          <span className="sr-only">More</span>
                        </SidebarMenuAction>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent side="right" align="start">
                        <DropdownMenuItem onClick={(e) => handleEditStart(e, conv._id, conv.title)}>
                          <Pencil className="mr-2 h-4 w-4 text-muted-foreground" />
                          <span>Rename</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onDelete(conv._id); }}>
                          <Trash2 className="mr-2 h-4 w-4 text-destructive" />
                          <span className="text-destructive">Delete</span>
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </SidebarMenuItem>
                ))}
                {conversations.length === 0 && (
                  <div className="px-4 py-2 text-sm text-muted-foreground">
                    No conversations yet.
                  </div>
                )}
              </SidebarMenu>
            ) : (
              <div className="px-4 py-4 text-sm text-muted-foreground flex flex-col gap-4 text-center">
                <p>Log in to save and access your conversation history.</p>
                <Link to="/login">
                  <Button variant="secondary" className="w-full">Login</Button>
                </Link>
                <Link to="/register">
                  <Button variant="outline" className="w-full">Register</Button>
                </Link>
              </div>
            )}
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-4 border-t">
        {user ? (
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2 truncate">
              <UserIcon className="h-4 w-4 shrink-0" />
              <span className="text-sm truncate">{user.email}</span>
            </div>
            <Button variant="ghost" size="icon" onClick={logout} title="Logout">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground text-center">Guest Mode</div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}

