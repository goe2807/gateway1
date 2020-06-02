from gateway import db
from models import Logs, User

def writelog(action, user_id):
    user = User.query.filter_by(id=user_id).first()
    log = Logs(action=action, user=user.username)
    db.session.add(log)
    db.session.commit()
