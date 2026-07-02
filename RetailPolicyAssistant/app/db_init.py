from app.database.session import Base, engine
import app.models


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


if __name__ == "__main__":
    init_db()