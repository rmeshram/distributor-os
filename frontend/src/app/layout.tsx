import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DistributorOS Operations Dashboard",
  description: "B2B Operational Operating System for India",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased overflow-hidden">{children}</body>
    </html>
  );
}
