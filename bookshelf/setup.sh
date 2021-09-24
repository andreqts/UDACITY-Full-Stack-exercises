pip3 install flask_sqlalchemy
pip3 install flask_cors
pip3 install flask --upgrade
pip3 uninstall flask-socketio -y

su - postgres bash -c "psql < /home/andre-remote/repos/UDACITY-Full-Stack-exercises/bookshelf/backend/setup.sql"
su - postgres bash -c "psql bookshelf < /home/andre-remote/repos/UDACITY-Full-Stack-exercises/bookshelf/backend/books.psql"