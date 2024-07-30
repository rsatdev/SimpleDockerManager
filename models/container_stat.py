from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ContainerStat(db.Model):
    __tablename__ = 'container_stats'  # Update table name
    id = db.Column(db.Integer, primary_key=True)
    container_id = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True)
    cpu_percentage = db.Column(db.Float)
    memory_usage = db.Column(db.Integer)

def init_db(app):
    with app.app_context():
        db.create_all()
