import { Menu, User as UserIcon, Settings, LogOut, ChevronDown } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { useAuth } from "@/hooks/useAuth";

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logoutUser } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-4 md:justify-end md:px-6 relative">
      <Button variant="ghost" size="icon" onClick={onMenuClick} className="md:hidden">
        <Menu className="h-5 w-5" />
        <span className="sr-only">Open menu</span>
      </Button>

      <div className="flex items-center gap-4">
        <ThemeToggle />
        
        {user && (
          <div className="relative" ref={dropdownRef}>
            <Button 
              variant="ghost" 
              className="flex items-center gap-2 pl-2 pr-1"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                <UserIcon className="h-4 w-4 text-primary" />
              </div>
              <span className="text-sm font-medium hidden sm:inline-block">
                {user.display_name || user.email.split('@')[0]}
              </span>
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </Button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-md border bg-popover text-popover-foreground shadow-md z-50 animate-in fade-in slide-in-from-top-2">
                <div className="px-3 py-2 border-b">
                  <p className="text-sm font-medium truncate">{user.display_name}</p>
                  <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                </div>
                <div className="p-1">
                  <Link to="/settings" onClick={() => setDropdownOpen(false)}>
                    <Button variant="ghost" className="w-full justify-start text-sm h-9">
                      <Settings className="mr-2 h-4 w-4" />
                      Settings
                    </Button>
                  </Link>
                  <Button 
                    variant="ghost" 
                    className="w-full justify-start text-sm h-9 text-destructive hover:bg-destructive/10 hover:text-destructive"
                    onClick={() => {
                      setDropdownOpen(false);
                      logoutUser();
                    }}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
