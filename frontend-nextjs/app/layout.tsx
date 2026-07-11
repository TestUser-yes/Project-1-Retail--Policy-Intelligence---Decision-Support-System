import type { Metadata } from 'next';
import Navbar from './components/Navbar';
import { RootProvider } from './providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'Retail Policy Intelligence',
  description: 'AI-powered retail policy compliance system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <RootProvider>
          <Navbar />
          <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
            {children}
          </main>
        </RootProvider>
      </body>
    </html>
  );
}
