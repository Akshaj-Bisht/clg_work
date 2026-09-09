import type { Metadata } from "next";
import "../components/coursework-dashboard.css";

export const metadata: Metadata = {
  title: "clg_work",
  description: "A private coursework library",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
