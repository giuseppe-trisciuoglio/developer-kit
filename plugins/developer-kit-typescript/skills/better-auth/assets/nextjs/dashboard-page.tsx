import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { SignOutButton } from '@/components/sign-out-button';

export default async function DashboardPage() {
  const session = await auth();

  if (!session) {
    redirect('/sign-in');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between">
            <div className="flex">
              <div className="flex flex-shrink-0 items-center">
                <h1 className="text-xl font-bold">Your App</h1>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700">
                {session.user.name || session.user.email}
              </span>
              <SignOutButton />
            </div>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Welcome back!</h2>

          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Name</p>
              <p className="text-lg">{session.user.name || 'Not set'}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-500">Email</p>
              <p className="text-lg">{session.user.email}</p>
            </div>

            {session.user.image && (
              <div>
                <p className="text-sm font-medium text-gray-500">Avatar</p>
                <img
                  src={session.user.image}
                  alt="Avatar"
                  className="mt-1 h-16 w-16 rounded-full"
                />
              </div>
            )}

            <div className="pt-4 border-t">
              <p className="text-sm font-medium text-gray-500 mb-2">Session Data</p>
              <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto">
                {JSON.stringify(session, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
