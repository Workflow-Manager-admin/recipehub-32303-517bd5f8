import { Link } from "@remix-run/react";

type RecipeCardProps = {
  id: number;
  title: string;
  description?: string;
  image_url?: string | null;
  author?: string;
  created_at?: string;
};

export default function RecipeCard({
  id,
  title,
  description,
  image_url,
  author,
  created_at,
}: RecipeCardProps) {
  return (
    <div className="bg-white rounded-lg shadow flex flex-col h-full hover:shadow-lg transition">
      <Link to={`/recipes/${id}`} className="block flex-1">
        {image_url ? (
          <img
            src={image_url}
            alt={title}
            className="w-full h-36 object-cover rounded-t"
          />
        ) : (
          <div className="w-full h-36 bg-gray-200 rounded-t flex items-center justify-center text-gray-400 text-4xl">
            🥗
          </div>
        )}
        <div className="p-4 flex flex-col gap-2">
          <div className="font-bold text-lg text-[#8BC34A]">{title}</div>
          <div className="text-sm text-gray-700 line-clamp-2 mb-1">
            {description}
          </div>
          {author && (
            <div className="text-xs text-gray-500">
              By {author}
              {created_at && (
                <> • {new Date(created_at).toLocaleDateString()}</>
              )}
            </div>
          )}
        </div>
      </Link>
    </div>
  );
}
