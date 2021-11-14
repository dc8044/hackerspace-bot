import database as db

db.Base.metadata.create_all(db.engine)

if db.session.query(db.HackerSpace).count() < 1:
    db.HackerSpace(is_open=False).commit()
