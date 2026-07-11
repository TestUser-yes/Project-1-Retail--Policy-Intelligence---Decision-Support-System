'use client';

import { useEffect, ReactNode } from 'react';
import { initializeTokens } from '@/app/lib/api';

export function RootProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    // Initialize authentication tokens on app startup
    // Tokens are stored as secure httpOnly cookies for all subsequent requests
    initializeTokens().catch((err) => {
      console.error('Failed to initialize authentication:', err);
    });
  }, []);

  return <>{children}</>;
}
