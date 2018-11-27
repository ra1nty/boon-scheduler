from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from contextlib import contextmanager
from config import app_config
from sql import ADD_TRIGGER

# configure Session class
Session = sessionmaker()

# create the engine
engine = create_engine(app_config['testing'].SQLALCHEMY_DATABASE_URI)

# associate it with Session class
Session.configure(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def init_trigger():
    """Return a connection item for the main thread to poll on."""
    db = engine.connect()
    db.execute(text(ADD_TRIGGER))
    db.execute(text("LISTEN data;").execution_options(autocommit=True))
    return db.connection
