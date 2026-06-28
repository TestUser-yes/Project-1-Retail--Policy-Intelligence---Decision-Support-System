class BaseRepository:
    """
    Base class for all repositories.
    Provides shared DB session handling.
    """

    def __init__(self, db):
        self.db = db
