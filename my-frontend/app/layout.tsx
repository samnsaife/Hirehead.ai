import "./global.css";
import { ReactNode } from "react";

export const metadata = {
  title: "Hirehead.ai",
  description: "AI-powered Resume Analyzer",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
