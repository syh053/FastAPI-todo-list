from sqlmodel import create_engine, Session

mysql_url = "mysql+pymysql://root:1234567890@localhost/todo"

engine = create_engine(mysql_url, echo=True)
  
def get_session():
    with Session(engine) as session:
        yield session