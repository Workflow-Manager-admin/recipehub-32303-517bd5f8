"""
FastAPI backend for RecipeHub: Provides user authentication, recipe CRUD, and search endpoints.

OpenAPI docs: see /docs

Routes:
    - /api/v1/auth: User registration, login, authentication
    - /api/v1/users: User listing & profile (basic MVP)
    - /api/v1/recipes: CRUD for recipe objects
    - /api/v1/search: Search recipes by keyword

All responses are JSON. Auth handled with JWT (in-memory only for MVP).
"""

from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Depends,
    Query,
    APIRouter,
)
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import secrets


# In-memory "database" for demonstration; replace with real DB for production!
USERS = {}
RECIPES = {}


# JWT Auth settings
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token with given data & expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme)):
    """FastAPI dependency: returns username from JWT if token is valid."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in USERS:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return USERS[username]


# ---- Pydantic models ----

class UserRegister(BaseModel):
    """User registration model."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Unique username"
    )
    email: EmailStr = Field(..., description="User's email")
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="User's password (plain text, demo only)"
    )


class UserLogin(BaseModel):
    """User login model."""

    username: str
    password: str


class UserOut(BaseModel):
    """User public info."""

    username: str
    email: EmailStr


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str


class RecipeBase(BaseModel):
    """Base recipe model."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Recipe title"
    )
    description: Optional[str] = Field(
        "",
        max_length=256,
        description="Short recipe description"
    )
    ingredients: List[str] = Field(..., description="List of ingredients")
    steps: List[str] = Field(..., description="Preparation steps")
    image_url: Optional[str] = Field(None, description="Optional image URL")


class RecipeCreate(RecipeBase):
    """For creating a recipe."""
    pass


class RecipeUpdate(BaseModel):
    """For updating recipe fields (all optional)."""

    title: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    image_url: Optional[str] = None


class RecipeOut(RecipeBase):
    """Recipe returned by API."""

    id: int
    author: str
    created_at: datetime


# ---- FastAPI App with Metadata ----

app = FastAPI(
    title="RecipeHub Backend API",
    version="1.0.0",
    description=(
        "Handles user authentication and recipe management for RecipeHub. See /docs."
    ),
    openapi_tags=[
        {"name": "Auth", "description": "User registration, login, JWT authentication"},
        {"name": "Users", "description": "User listing, info"},
        {"name": "Recipes", "description": "Browse, create, edit, delete recipes"},
        {"name": "Search", "description": "Recipe search endpoint"},
    ],
)


# ---- CORS (for local frontend dev etc) ----

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Routers ----

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
user_router = APIRouter(prefix="/api/v1/users", tags=["Users"])
recipes_router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])
search_router = APIRouter(prefix="/api/v1/search", tags=["Search"])


# ---- AUTH ROUTES ----


@auth_router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    summary="Register user",
    description="Register a new user account",
)
# PUBLIC_INTERFACE
def register_user(user: UserRegister):
    """Register a user (username & email must be unique)."""
    if user.username in USERS:
        raise HTTPException(
            status_code=400, detail="Username already registered"
        )
    for u in USERS.values():
        if u["email"] == user.email:
            raise HTTPException(
                status_code=400, detail="Email already registered"
            )
    USERS[user.username] = {
        "username": user.username,
        "email": user.email,
        "password": user.password,  # Never store plain text in production!
        "created_at": datetime.utcnow(),
    }
    return UserOut(username=user.username, email=user.email)


@auth_router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate and get a JWT Bearer token",
)
# PUBLIC_INTERFACE
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return a JWT access token."""
    user = USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password"
        )
    token = create_access_token({"sub": user["username"]})
    return Token(access_token=token, token_type="bearer")


# ---- USER ROUTES ----


@user_router.get(
    "/me",
    response_model=UserOut,
    summary="Get my user info",
    description="Get details of current user.",
)
# PUBLIC_INTERFACE
def get_my_info(current_user: dict = Depends(get_current_user)):
    """Return info for the currently authenticated user."""
    return UserOut(
        username=current_user["username"], email=current_user["email"]
    )


@user_router.get(
    "/",
    response_model=List[UserOut],
    summary="List all users",
    description="Admin: list all users (MVP, no admin check)",
)
# PUBLIC_INTERFACE
def list_users():
    """List all registered users."""
    return [
        UserOut(username=u["username"], email=u["email"])
        for u in USERS.values()
    ]


# ---- RECIPE ROUTES ----


@recipes_router.get(
    "/",
    response_model=List[RecipeOut],
    summary="List recipes",
    description="Browse all recipes.",
)
# PUBLIC_INTERFACE
def list_recipes(skip: int = 0, limit: int = 20):
    """List all recipes with paging."""
    recipes = list(RECIPES.values())
    return recipes[skip: skip + limit]


@recipes_router.post(
    "/",
    response_model=RecipeOut,
    status_code=201,
    summary="Add a new recipe",
    description="Create a new recipe. Requires authentication.",
)
# PUBLIC_INTERFACE
def add_recipe(
    recipe: RecipeCreate, current_user: dict = Depends(get_current_user)
):
    """Create new recipe, tied to current user."""
    recipe_id = len(RECIPES) + 1
    item = RecipeOut(
        id=recipe_id,
        author=current_user["username"],
        created_at=datetime.utcnow(),
        **recipe.dict()
    )
    RECIPES[recipe_id] = item
    return item


@recipes_router.get(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Get recipe details",
    description="View details of a recipe by ID",
)
# PUBLIC_INTERFACE
def get_recipe(recipe_id: int):
    """Get recipe by ID."""
    recipe = RECIPES.get(recipe_id)
    if not recipe:
        raise HTTPException(404, detail="Recipe not found")
    return recipe


@recipes_router.put(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Edit recipe",
    description="Update your recipe by ID. Requires authentication.",
)
# PUBLIC_INTERFACE
def update_recipe(
    recipe_id: int, update: RecipeUpdate, current_user: dict = Depends(get_current_user)
):
    """Update a recipe (must be author)."""
    recipe = RECIPES.get(recipe_id)
    if not recipe:
        raise HTTPException(404, detail="Recipe not found")
    if recipe.author != current_user["username"]:
        raise HTTPException(
            403, detail="You can only edit your own recipes"
        )
    # Update fields
    update_data = update.dict(exclude_unset=True)
    updated_item = recipe.copy(update=update_data)
    RECIPES[recipe_id] = updated_item
    return updated_item


@recipes_router.delete(
    "/{recipe_id}",
    status_code=204,
    summary="Delete recipe",
    description="Delete your recipe by ID. Requires authentication.",
)
# PUBLIC_INTERFACE
def delete_recipe(
    recipe_id: int, current_user: dict = Depends(get_current_user)
):
    """Delete a recipe (must be author)."""
    recipe = RECIPES.get(recipe_id)
    if not recipe:
        raise HTTPException(404, detail="Recipe not found")
    if recipe.author != current_user["username"]:
        raise HTTPException(
            403, detail="You can only delete your own recipes"
        )
    del RECIPES[recipe_id]
    return


# ---- SEARCH ROUTES ----


@search_router.get(
    "/",
    response_model=List[RecipeOut],
    summary="Search recipes",
    description="Search for recipes by keyword (title/ingredients)",
)
# PUBLIC_INTERFACE
def search_recipes(q: str = Query(..., description="Search query")):
    """Basic keyword search in recipe title/ingredients."""
    q_lc = q.lower()
    results = [
        r
        for r in RECIPES.values()
        if q_lc in r.title.lower()
        or any(q_lc in i.lower() for i in r.ingredients)
    ]
    return results


# ---- Register Routers ----

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(recipes_router)
app.include_router(search_router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


# ---- OpenAPI Customization: Real-time/Websocket (Placeholder for future expansion) ----

def custom_openapi():
    """Custom OpenAPI schema to annotate real-time/websocket interface if needed later."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="RecipeHub Backend API",
        version="1.0.0",
        description=(
            "Handles user authentication and recipe management. All API under /api/v1. "
            "Authenticate using JWT Bearer token (see /api/v1/auth/login)."
        ),
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
