from upshared.extensions import db
from datetime import datetime

# 文件
class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)

    name = db.Column(db.String(50),unique=True) # 文件名
    type = db.Column(db.String(50))   # 后缀
    remarks = db.Column(db.String(255)) # 备注