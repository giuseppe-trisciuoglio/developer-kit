import { auth } from '@/lib/auth';
import { nextMiddleware } from 'better-auth/next-js';

export default nextMiddleware(auth, {
  // Optional: Add custom middleware logic
  async before(request) {
    // Add custom logic here if needed
    return null;
  },
});

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
