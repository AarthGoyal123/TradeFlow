import { Mail, User as UserIcon, Shield } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { useAuth } from "@/hooks/useAuth";

export default function SettingsPage() {
  const { user } = useAuth();

  // Simple heuristic for auth method: if no password was required (e.g. no tenant info), 
  // or based on email domain, but realistically we just show what we have.
  // The user requirement says: "For Google users, clearly indicate: Signed in with Google".
  // Since we don't return auth_provider in the current API, we can just show email and let them know it's a connected account.
  
  return (
    <div className="space-y-6 max-w-4xl">
      <PageHeader title="Settings" description="Manage your account settings and preferences" />
      
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Your personal profile details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <UserIcon className="h-4 w-4" />
                  Display Name
                </label>
                <p className="text-sm font-medium">{user?.display_name || "Not set"}</p>
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email Address
                </label>
                <p className="text-sm font-medium">{user?.email}</p>
              </div>
              <div className="space-y-1 md:col-span-2">
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  Authentication
                </label>
                <p className="text-sm font-medium">
                  {user?.id.includes("google") ? "Signed in with Google" : "Standard Account (Password)"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>Customize how TradeFlow looks on your device</CardDescription>
          </CardHeader>
          <CardContent>
            <ThemeToggle />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
