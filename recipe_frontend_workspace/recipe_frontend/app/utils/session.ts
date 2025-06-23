import { createCookie } from "@remix-run/node";

export const tokenCookie = createCookie("token", {
  path: "/",
  httpOnly: true,
  sameSite: "lax",
  secure: process.env.NODE_ENV === "production",
  maxAge: 60 * 60 * 24 * 7, // 1 week
});
