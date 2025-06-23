import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { Form, useActionData, useNavigation } from "@remix-run/react";
import { tokenCookie } from "~/utils/session";
import { apiRequest } from "~/utils/api";

export async function action({ request }: ActionFunctionArgs) {
  const form = await request.formData();
  const username = form.get("username") as string;
  const password = form.get("password") as string;

  try {
    const response = await apiRequest(
      "/auth/login",
      "POST",
      new URLSearchParams({ username, password })
    );
    const cookie = await tokenCookie.serialize(response.access_token);
    return redirect("/", {
      headers: { "Set-Cookie": cookie },
    });
  } catch (error) {
    return json({ error: error instanceof Error ? error.message : "Login failed" });
  }
}

export default function Login() {
  const actionData = useActionData<typeof action>();
  const nav = useNavigation();
  return (
    <div className="max-w-md mx-auto mt-12 p-8 bg-white rounded-xl shadow flex flex-col gap-6">
      <h2 className="text-2xl font-bold mb-2">Login</h2>
      {actionData?.error && (
        <div className="bg-red-100 text-red-700 px-4 py-2 rounded mb-4">
          {actionData.error}
        </div>
      )}
      <Form method="post" replace className="flex flex-col gap-5">
        <label>
          <div className="mb-1 font-semibold">Username</div>
          <input
            name="username"
            type="text"
            required
            className="w-full px-3 py-2 border rounded"
            // autoFocus removed for accessibility (see lint)
          />
        </label>
        <label>
          <div className="mb-1 font-semibold">Password</div>
          <input
            name="password"
            type="password"
            required
            className="w-full px-3 py-2 border rounded"
          />
        </label>
        <button
          type="submit"
          className="bg-[#8BC34A] text-white rounded px-4 py-2 font-bold hover:bg-[#7FAe36] transition"
          disabled={nav.state === "submitting"}
        >
          {nav.state === "submitting" ? "Logging in…" : "Login"}
        </button>
      </Form>
      <div className="text-center mt-4">
        No account?{" "}
        <a href="/register" className="text-[#8BC34A] hover:underline">
          Register here
        </a>
      </div>
    </div>
  );
}
