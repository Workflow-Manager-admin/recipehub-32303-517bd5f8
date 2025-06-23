import { redirect } from "@remix-run/node";
import { tokenCookie } from "~/utils/session";

// POST to this route to log out
export async function action() {
  return redirect("/login", {
    headers: {
      "Set-Cookie": await tokenCookie.serialize("", { maxAge: 0 }),
    },
  });
}
