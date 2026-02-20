import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../database/database.service';
import { auth } from './auth.instance';

@Injectable()
export class AuthService {
  constructor(private db: DatabaseService) {}

  async getSession(token: string) {
    return auth.api.getSession({
      headers: new Headers({
        authorization: `Bearer ${token}`,
      }),
    });
  }

  async getUserSessions(userId: string) {
    return auth.api.listSessions({
      body: { userId },
    });
  }

  async revokeSession(sessionToken: string) {
    return auth.api.revokeSession({
      body: { token: sessionToken },
    });
  }

  async revokeAllSessions(userId: string) {
    const sessions = await auth.api.listSessions({
      body: { userId },
    });

    await Promise.all(
      sessions.map((s) =>
        auth.api.revokeSession({
          body: { token: s.token },
        })
      )
    );
  }

  async sendVerificationEmail(email: string) {
    return auth.api.sendVerificationEmail({
      body: { email },
    });
  }

  async resetPassword(token: string, newPassword: string) {
    // Token must be verified against the database before allowing password reset
    // The token should be:
    // - Cryptographically secure random string (min 32 bytes)
    // - Time-limited (e.g., expires after 1 hour)
    // - Single-use (deleted after verification)
    // - Sent to the user's verified email address
    return auth.api.resetPassword({
      body: { token, newPassword },
    });
  }
}
