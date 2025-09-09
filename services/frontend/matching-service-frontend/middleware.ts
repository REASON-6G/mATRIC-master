import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Pages that require login
const protectedRoutes = [
  "/topics",
  "/publishers",
  "/subscribers",
  "/emulators",
  "/data",
  "/users",
  "/config",
];

export function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();

  // Example: get token from cookies
  const token = req.cookies.get("auth_token")?.value;

  // User info could also be stored in JWT, decode if needed
  // For simplicity, let's assume token means logged in
  const isLoggedIn = !!token;

  // For admin routes
  const adminRoutes = ["/users", "/config"];

  if (protectedRoutes.some((path) => url.pathname.startsWith(path))) {
    if (!isLoggedIn) {
      // Not logged in -> redirect to home
      url.pathname = "/";
      return NextResponse.redirect(url);
    }

    // For admin routes, check role
    if (adminRoutes.some((path) => url.pathname.startsWith(path))) {
      const role = req.cookies.get("user_role")?.value; // must be set by your login API
      if (role !== "admin") {
        url.pathname = "/";
        return NextResponse.redirect(url);
      }
    }
  }

  return NextResponse.next();
}
