import Sidebar from '@/components/Sidebar';
import TopBar from '@/components/TopBar';
import { AuthProvider } from "@/context/AuthContext";
import { ToastProvider } from "@/context/ToastContext";
import './globals.css';
import { Inter, Roboto_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
});

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
});

export const metadata = {
  title: 'mATRIC Dashboard',
  description: 'Admin and monitoring dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${robotoMono.variable}`}>
      <body className="flex flex-col min-h-screen bg-gray-50">
        <AuthProvider>
          <ToastProvider>
            <TopBar />
            <div className="flex flex-1 overflow-hidden">
              <Sidebar />
              <main className="flex-1 p-4 overflow-auto">{children}</main>
            </div>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
