'use client';

import { useEffect, useState } from 'react';
import type { Session } from 'better-auth/react';

export function useSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSession() {
      try {
        const response = await fetch('/api/auth/get-session');
        if (response.ok) {
          const data = await response.json();
          setSession(data);
        }
      } catch {
        setSession(null);
      } finally {
        setLoading(false);
      }
    }

    loadSession();
  }, []);

  return { session, loading };
}

export function useUser() {
  const { session, loading } = useSession();
  return { user: session?.user, loading };
}
