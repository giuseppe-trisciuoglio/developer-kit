import {
  Controller,
  Post,
  Body,
  Get,
  Req,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { AuthService } from './auth.service';
import { AuthGuard } from './auth.guard';

@Controller('auth')
export class AuthController {
  constructor(private authService: AuthService) {}

  @Get('session')
  @HttpCode(HttpStatus.OK)
  async getSession(@Req() req) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    return this.authService.getSession(token);
  }

  @Post('sign-out')
  @UseGuards(AuthGuard)
  @HttpCode(HttpStatus.OK)
  async signOut(@Req() req) {
    // Requires authentication to prevent session enumeration attacks
    return this.authService.revokeSession(req.session.sessionToken);
  }

  @Get('sessions')
  @UseGuards(AuthGuard)
  async getSessions(@Req() req) {
    return this.authService.getUserSessions(req.user.id);
  }

  @Post('sessions/revoke-all')
  @UseGuards(AuthGuard)
  @HttpCode(HttpStatus.OK)
  async revokeAll(@Req() req) {
    return this.authService.revokeAllSessions(req.user.id);
  }

  @Post('verify-email')
  @HttpCode(HttpStatus.OK)
  async sendVerificationEmail(@Body() body: { email: string }) {
    return this.authService.sendVerificationEmail(body.email);
  }

  @Post('reset-password')
  @HttpCode(HttpStatus.OK)
  async resetPassword(
    @Body() body: { token: string; newPassword: string }
  ) {
    // IMPORTANT: Token must be a cryptographically secure random string
    // sent to the user's email address via a forgot-password flow
    return this.authService.resetPassword(body.token, body.newPassword);
  }
}
