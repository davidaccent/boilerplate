from app import db
import sys
from starlette_core.database import Session
from starlette_auth.tables import User

email = sys.argv[1]
first_name = sys.argv[2]
last_name = sys.argv[3]

user = User(email=email, first_name=first_name, last_name=last_name)
user.set_password('password')
session = Session()
session.add(user)
session.commit()
session.close()