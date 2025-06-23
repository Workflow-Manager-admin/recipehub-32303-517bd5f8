import { Link, useLocation } from "@remix-run/react";
import { useOptionalUser } from "~/utils/useUser";

export default function Navbar() {
  const user = useOptionalUser();
  const location = useLocation();

  return (
    <nav className="w-full flex items-center justify-between px-6 py-4 bg-[#8BC34A] text-white shadow-md">
      <div className="flex items-center gap-4">
        <Link to="/" className="font-bold text-xl tracking-tight">
          RecipeHub
        </Link>
        <Link
          to="/recipes"
          className={`ml-2 hover:underline ${
            location.pathname.startsWith("/recipes")
              ? "font-semibold underline"
              : ""
          }`}
        >
          Browse Recipes
        </Link>
        <Link
          to="/search"
          className={`ml-2 hover:underline ${
            location.pathname.startsWith("/search")
              ? "font-semibold underline"
              : ""
          }`}
        >
          Search
        </Link>
        {user && (
          <Link
            to="/recipes/add"
            className={`ml-2 hover:underline ${
              location.pathname === "/recipes/add"
                ? "font-semibold underline"
                : ""
            }`}
          >
            Add Recipe
          </Link>
        )}
      </div>
      <div className="flex items-center gap-2">
        {user ? (
          <>
            <span className="mr-3 hidden sm:inline">
              Hello, {user.username}
            </span>
            <form method="post" action="/logout">
              <button
                type="submit"
                className="px-4 py-1 rounded bg-[#FF9800] hover:bg-[#ffa733] text-white"
              >
                Logout
              </button>
            </form>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="px-3 py-1 rounded bg-white text-[#8BC34A] hover:bg-[#FFEB3B] hover:text-black"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="px-3 py-1 rounded border border-white bg-[#FF9800] text-white hover:bg-[#FFEB3B] hover:text-black"
            >
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
