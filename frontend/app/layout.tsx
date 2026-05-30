import type { Metadata } from "next";
import Link from "next/link";
import { GlobalLoader } from "@/components/GlobalLoader";
import "./globals.css";

export const metadata: Metadata = {
  title: "Salary Management",
  description: "Salary management dashboard for HR teams",
};

const navigation = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/employees", label: "Employee Management" },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <aside className="sidebar" aria-label="Primary navigation">
            <div className="sidebar-brand">
              <div className="sidebar-kicker">HR Workspace</div>
              <h1 className="sidebar-title">Salary Management</h1>
            </div>
            <nav className="nav-list">
              {navigation.map((item) => (
                <Link className="nav-link" href={item.href} key={item.href}>
                  {item.label}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="main-content">{children}</main>
        </div>
        <GlobalLoader />
      </body>
    </html>
  );
}
