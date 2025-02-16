import os
from abc import abstractmethod

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()


class MysqlConnector:
    db_url = os.environ.get("DB_URL")
    if not db_url:
        db_url = "mysql+pymysql://root:answnsdud1@localhost:3306/mailpocket"
    engine = create_engine(db_url)
    Session = scoped_session(sessionmaker(bind=engine))


class MysqlSession(MysqlConnector):
    def __init__(self) -> None:
        self.session = self.Session()

    def close(self):
        self.session.close()

    def rollback(self):
        self.session.rollback()


class MysqlCRUDTemplate(MysqlSession):
    @abstractmethod
    def execute(self):
        pass

    def run(self):
        try:
            return self.execute()
        except Exception as e:
            self.rollback()
            raise e
        finally:
            self.close()
