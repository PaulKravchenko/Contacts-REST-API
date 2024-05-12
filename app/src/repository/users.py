from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Asynchronous function that retrieves a user from the database based on their email.

    This function queries the database for a User object whose email matches the provided email. It returns the first User object that matches the query.

    Args:
        email (str): The email of the user to retrieve.
        db (Session): The SQLAlchemy session object.

    Returns:
        User: The User object that matches the query, if it exists. Otherwise, None.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/users/{email}")
        >>> async def read_user(email: str, db: Session = Depends(get_db)):
        >>>     user = await get_user_by_email(email, db)
        >>>     return user
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Asynchronous function that creates a new user in the database.

    This function takes a UserModel object and a SQLAlchemy session as input. It creates a new User object, adds it to the session, commits the session, refreshes the user object, and returns it. It also attempts to get an avatar image from Gravatar using the user's email.

    Args:
        body (UserModel): The UserModel object containing the details of the user to be created.
        db (Session): The SQLAlchemy session object.

    Returns:
        User: The newly created User object.

    Raises:
        Exception: An error occurred while fetching the avatar from Gravatar.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.post("/users/")
        >>> async def create_new_user(body: UserModel, db: Session = Depends(get_db)):
        >>>     user = await create_user(body, db)
        >>>     return user
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def confirmed_email(email: str, db: Session) -> None:
    """
    Asynchronous function that confirms a user's email in the database.

    This function queries the database for a User object whose email matches the provided email. If the user exists, it sets the user's confirmed attribute to True and commits the changes.

    Args:
        email (str): The email of the user to confirm.
        db (Session): The SQLAlchemy session object.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.post("/users/confirm/{email}")
        >>> async def confirm_user_email(email: str, db: Session = Depends(get_db)):
        >>>     await confirmed_email(email, db)
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()



async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Asynchronous function that updates a user's refresh token in the database.

    This function takes a User object, a token string, and a SQLAlchemy session as input. It updates the user's refresh_token attribute with the provided token and commits the changes.

    Args:
        user (User): The User object whose refresh token is to be updated.
        token (str | None): The new refresh token. If None, the refresh token is cleared.
        db (Session): The SQLAlchemy session object.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.post("/users/update_token")
        >>> async def update_user_token(token: str | None, db: Session = Depends(get_db)):
        >>>     await update_token(current_user, token, db)
    """
    user.refresh_token = token
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Asynchronous function that updates a user's avatar in the database.

    This function queries the database for a User object whose email matches the provided email. If the user exists, it updates the user's avatar with the provided URL and commits the changes.

    Args:
        email (str): The email of the user whose avatar is to be updated.
        url (str): The URL of the new avatar.
        db (Session): The SQLAlchemy session object.

    Returns:
        User: The updated User object if it exists, otherwise None.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.put("/users/avatar")
        >>> async def update_user_avatar(email: str, url: str, db: Session = Depends(get_db)):
        >>>     user = await update_avatar(email, url, db)
        >>>     return user
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
