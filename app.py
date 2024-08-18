from configs import app, bcrypt, db, login_manager

from forms import *
from validations import *
from models import *
from routes import *
from api import *
from exceptions import *



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


