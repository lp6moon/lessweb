from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from ..storage import global_data

__all__ = ["DBModel", "init", "processor", "create_all", "make_session"]


DBModel = declarative_base()


def init(conf):
    if 'dburi' in conf:
        engine = create_engine(conf['dburi'])
    else:
        engine = create_engine(
            '{protocol}://{username}:{password}@{host}:{port}/{entity}'.format(**conf),
            pool_recycle=3600
        )
    engine.echo = conf.get('echo', conf['echo'])
    global_data.db_session_maker = sessionmaker(bind=engine)
    global_data.db_engine = engine


def processor(ctx):
    try:
        ctx.db = global_data.db_session_maker()
        ctx.will_commit = False
        ret = ctx()
        if ctx.will_commit:
            ctx.db.commit()
    except:
        ctx.db.rollback()
        raise
    finally:
        ctx.db.close()
    return ret


def create_all():
    DBModel.metadata.create_all(global_data.db_engine)


@contextmanager
def make_session():
    session = None
    try:
        session = global_data.db_session_maker()
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()