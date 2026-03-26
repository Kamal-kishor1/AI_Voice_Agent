import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alex Foundation",
  description: "Phase 1 dashboard shell for the Alex AI operating system.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
