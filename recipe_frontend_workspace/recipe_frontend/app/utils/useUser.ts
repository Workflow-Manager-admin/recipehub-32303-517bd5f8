import { useMatches } from "@remix-run/react";

// Hook to get the user data if loaded at the root or by session
export function useOptionalUser():
  | { username: string; email: string }
  | undefined {
  const matches = useMatches();
  const data =
    matches.find((m) => m.id === "root" || m.pathname === "/")?.data as
      | { user?: { username: string; email: string } }
      | undefined;
  return data?.user;
}
