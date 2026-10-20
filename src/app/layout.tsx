import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LP Foundation Demo | ミセミルWeb",
  description: "ミセミルWebのLP制作自動化を検証する架空のデモページです。",
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
