import "./globals.css";

import { AppShell } from "../components/AppShell";
import { AuthProvider } from "../components/AuthProvider";
import { NotificationProvider } from "../components/NotificationCenter";

export const metadata = {
  title: "Local Agentic Enterprise Platform",
  description: "Production-grade business automation with local Ollama agents"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <NotificationProvider>
          <AuthProvider>
            <AppShell>{children}</AppShell>
          </AuthProvider>
        </NotificationProvider>
      </body>
    </html>
  );
}
