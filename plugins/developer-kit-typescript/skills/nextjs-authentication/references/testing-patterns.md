# Testing Authentication Patterns

Testing strategies for Next.js authentication with Vitest and Playwright.

## Unit Testing with Vitest

### Setup

```bash
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom
```

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
});
```

```typescript
// tests/setup.ts
import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  redirect: vi.fn(),
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    refresh: vi.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock next/headers
vi.mock("next/headers", () => ({
  cookies: () => ({
    get: vi.fn(),
    set: vi.fn(),
  }),
  headers: () => new Headers(),
}));
```

### Testing Auth Module

```typescript
// tests/auth/auth.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { auth } from "@/auth";

vi.mock("@/auth", () => ({
  auth: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
}));

describe("Authentication", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Session Verification", () => {
    it("should return null when user is not authenticated", async () => {
      vi.mocked(auth).mockResolvedValue(null);

      const session = await auth();

      expect(session).toBeNull();
    });

    it("should return session when user is authenticated", async () => {
      const mockSession = {
        user: {
          id: "user-1",
          email: "test@example.com",
          name: "Test User",
          role: "user",
        },
        expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      };

      vi.mocked(auth).mockResolvedValue(mockSession);

      const session = await auth();

      expect(session).toEqual(mockSession);
      expect(session?.user?.id).toBe("user-1");
    });
  });

  describe("Role-Based Access", () => {
    it("should identify admin users", async () => {
      const adminSession = {
        user: {
          id: "admin-1",
          email: "admin@example.com",
          role: "admin",
        },
      };

      vi.mocked(auth).mockResolvedValue(adminSession);

      const session = await auth();

      expect(session?.user?.role).toBe("admin");
    });
  });
});
```

### Testing DAL Functions

```typescript
// tests/auth/dal.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { verifySession, requireAuth, requireRole } from "@/lib/dal";
import { auth } from "@/auth";
import { redirect } from "next/navigation";

vi.mock("@/auth", () => ({
  auth: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  redirect: vi.fn(),
}));

describe("Data Access Layer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("verifySession", () => {
    it("should return session for authenticated user", async () => {
      const mockSession = {
        user: { id: "1", email: "test@example.com", role: "user" },
      };
      vi.mocked(auth).mockResolvedValue(mockSession);

      const result = await verifySession();

      expect(result).toEqual(mockSession);
    });

    it("should return null for unauthenticated user", async () => {
      vi.mocked(auth).mockResolvedValue(null);

      const result = await verifySession();

      expect(result).toBeNull();
    });
  });

  describe("requireAuth", () => {
    it("should return session when authenticated", async () => {
      const mockSession = {
        user: { id: "1", email: "test@example.com" },
      };
      vi.mocked(auth).mockResolvedValue(mockSession);

      const result = await requireAuth();

      expect(result).toEqual(mockSession);
    });

    it("should redirect to login when not authenticated", async () => {
      vi.mocked(auth).mockResolvedValue(null);

      await requireAuth();

      expect(redirect).toHaveBeenCalledWith("/login");
    });
  });

  describe("requireRole", () => {
    it("should return session for correct role", async () => {
      const mockSession = {
        user: { id: "1", email: "admin@example.com", role: "admin" },
      };
      vi.mocked(auth).mockResolvedValue(mockSession);

      const result = await requireRole("admin");

      expect(result).toEqual(mockSession);
    });

    it("should redirect to unauthorized for wrong role", async () => {
      const mockSession = {
        user: { id: "1", email: "user@example.com", role: "user" },
      };
      vi.mocked(auth).mockResolvedValue(mockSession);

      await requireRole("admin");

      expect(redirect).toHaveBeenCalledWith("/unauthorized");
    });
  });
});
```

### Testing Server Actions

```typescript
// tests/actions/todo.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { createTodo } from "@/app/actions/todo";
import { auth } from "@/auth";

vi.mock("@/auth", () => ({
  auth: vi.fn(),
}));

vi.mock("next/cache", () => ({
  revalidatePath: vi.fn(),
}));

vi.mock("@/lib/db", () => ({
  db: {
    todo: {
      create: vi.fn(),
    },
  },
}));

describe("Todo Actions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("createTodo", () => {
    it("should throw error when user is not authenticated", async () => {
      vi.mocked(auth).mockResolvedValue(null);

      const formData = new FormData();
      formData.append("title", "Test Todo");

      await expect(createTodo(formData)).rejects.toThrow("Unauthorized");
    });

    it("should create todo for authenticated user", async () => {
      const mockSession = {
        user: { id: "user-1", email: "test@example.com", role: "user" },
      };
      vi.mocked(auth).mockResolvedValue(mockSession);

      const formData = new FormData();
      formData.append("title", "Test Todo");

      const { db } = await import("@/lib/db");
      vi.mocked(db.todo.create).mockResolvedValue({
        id: "1",
        title: "Test Todo",
        userId: "user-1",
      });

      await createTodo(formData);

      expect(db.todo.create).toHaveBeenCalledWith({
        data: {
          title: "Test Todo",
          userId: "user-1",
        },
      });
    });
  });
});
```

### Testing React Components

```tsx
// tests/components/sign-in-button.test.tsx
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SignInButton } from "@/components/auth/sign-in-button";
import { useSession, signIn, signOut } from "next-auth/react";

vi.mock("next-auth/react", () => ({
  useSession: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
}));

describe("SignInButton", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should show loading state", () => {
    vi.mocked(useSession).mockReturnValue({
      data: null,
      status: "loading",
      update: vi.fn(),
    });

    render(<SignInButton />);

    expect(screen.getByText("Loading...")).toBeDisabled();
  });

  it("should show sign in button when unauthenticated", () => {
    vi.mocked(useSession).mockReturnValue({
      data: null,
      status: "unauthenticated",
      update: vi.fn(),
    });

    render(<SignInButton />);

    const button = screen.getByText("Sign in with GitHub");
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(signIn).toHaveBeenCalledWith("github");
  });

  it("should show sign out button when authenticated", () => {
    vi.mocked(useSession).mockReturnValue({
      data: {
        user: { name: "John Doe", email: "john@example.com" },
        expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      },
      status: "authenticated",
      update: vi.fn(),
    });

    render(<SignInButton />);

    const button = screen.getByText("Sign out John Doe");
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(signOut).toHaveBeenCalled();
  });
});
```

## Integration Testing

### Testing API Routes

```typescript
// tests/api/auth.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { GET } from "@/app/api/user/route";
import { auth } from "@/auth";

vi.mock("@/auth", () => ({
  auth: vi.fn(),
}));

vi.mock("@/lib/db", () => ({
  db: {
    user: {
      findUnique: vi.fn(),
    },
  },
}));

describe("API Routes", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("GET /api/user", () => {
    it("should return 401 when not authenticated", async () => {
      vi.mocked(auth).mockResolvedValue(null);

      const response = await GET();

      expect(response.status).toBe(401);
      expect(await response.json()).toEqual({ error: "Unauthorized" });
    });

    it("should return user data when authenticated", async () => {
      const mockSession = {
        user: { id: "user-1", email: "test@example.com" },
      };
      vi.mocked(auth).mockResolvedValue(mockSession);

      const mockUser = {
        id: "user-1",
        name: "Test User",
        email: "test@example.com",
      };

      const { db } = await import("@/lib/db");
      vi.mocked(db.user.findUnique).mockResolvedValue(mockUser);

      const response = await GET();

      expect(response.status).toBe(200);
      expect(await response.json()).toEqual(mockUser);
    });
  });
});
```

## E2E Testing with Playwright

### Setup

```bash
npm install -D @playwright/test
npx playwright install
```

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

### Auth Fixtures

```typescript
// e2e/fixtures.ts
import { test as base, expect } from "@playwright/test";

export * from "@playwright/test";

export const test = base.extend<{
  login: (user?: { email: string; password: string }) => Promise<void>;
}>({
  login: async ({ page }, use) => {
    await use(async (user) => {
      await page.goto("/login");

      const email = user?.email || "test@example.com";
      const password = user?.password || "password123";

      await page.fill('input[name="email"]', email);
      await page.fill('input[name="password"]', password);
      await page.click('button[type="submit"]');

      await page.waitForURL("/dashboard");
    });
  },
});
```

### Auth Flow Tests

```typescript
// e2e/auth.spec.ts
import { test, expect } from "./fixtures";

test.describe("Authentication Flows", () => {
  test("should redirect to login when accessing protected page", async ({
    page,
  }) => {
    await page.goto("/dashboard");

    await expect(page).toHaveURL("/login?callbackUrl=%2Fdashboard");
  });

  test("should login with credentials", async ({ page }) => {
    await page.goto("/login");

    await page.fill('input[name="email"]', "test@example.com");
    await page.fill('input[name="password"]', "password123");
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("h1")).toContainText("Dashboard");
  });

  test("should show error for invalid credentials", async ({ page }) => {
    await page.goto("/login");

    await page.fill('input[name="email"]', "wrong@example.com");
    await page.fill('input[name="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    await expect(page.locator("text=Invalid credentials")).toBeVisible();
  });

  test("should logout user", async ({ page, login }) => {
    await login();

    await page.click("text=Sign out");

    await expect(page).toHaveURL("/");

    await page.goto("/dashboard");
    await expect(page).toHaveURL("/login");
  });
});

test.describe("Protected Routes", () => {
  test("should allow admin to access admin page", async ({ page, login }) => {
    // Login as admin
    await login({ email: "admin@example.com", password: "admin123" });

    await page.goto("/admin");

    await expect(page.locator("h1")).toContainText("Admin");
  });

  test("should redirect non-admin from admin page", async ({ page, login }) => {
    // Login as regular user
    await login({ email: "user@example.com", password: "user123" });

    await page.goto("/admin");

    await expect(page).toHaveURL("/unauthorized");
  });
});
```

### Storage State for Authenticated Tests

```typescript
// e2e/global-setup.ts
import { chromium, FullConfig } from "@playwright/test";

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Login and save storage state
  await page.goto(`${baseURL}/login`);
  await page.fill('input[name="email"]', "test@example.com");
  await page.fill('input[name="password"]', "password123");
  await page.click('button[type="submit"]');
  await page.waitForURL(`${baseURL}/dashboard`);

  await page.context().storageState({ path: "e2e/.auth/user.json" });

  // Admin login
  await page.goto(`${baseURL}/login`);
  await page.fill('input[name="email"]', "admin@example.com");
  await page.fill('input[name="password"]', "admin123");
  await page.click('button[type="submit"]');
  await page.waitForURL(`${baseURL}/dashboard`);

  await page.context().storageState({ path: "e2e/.auth/admin.json" });

  await browser.close();
}

export default globalSetup;
```

```typescript
// playwright.config.ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  globalSetup: require.resolve("./e2e/global-setup"),
  projects: [
    {
      name: "authenticated",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "e2e/.auth/user.json",
      },
    },
    {
      name: "admin",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "e2e/.auth/admin.json",
      },
    },
  ],
});
```

## Mocking Auth in Stories (Storybook)

```typescript
// .storybook/preview.tsx
import type { Preview } from "@storybook/react";
import { SessionProvider } from "next-auth/react";

const preview: Preview = {
  decorators: [
    (Story, context) => {
      const session = context.parameters.session || null;

      return (
        <SessionProvider session={session}>
          <Story />
        </SessionProvider>
      );
    },
  ],
};

export default preview;
```

```tsx
// components/auth/sign-in-button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { SignInButton } from "./sign-in-button";

const meta: Meta<typeof SignInButton> = {
  component: SignInButton,
};

export default meta;

type Story = StoryObj<typeof SignInButton>;

export const Unauthenticated: Story = {
  parameters: {
    session: null,
  },
};

export const Authenticated: Story = {
  parameters: {
    session: {
      user: {
        name: "John Doe",
        email: "john@example.com",
        image: "https://example.com/avatar.jpg",
      },
      expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    },
  },
};

export const Loading: Story = {
  parameters: {
    session: undefined,
  },
};
```
