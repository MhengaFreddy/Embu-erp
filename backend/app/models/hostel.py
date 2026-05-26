from ..extensions import db

class Hostel(db.Model):
    __tablename__ = 'hostels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    block = db.Column(db.String(10))
    rooms = db.relationship('Room', backref='hostel', lazy=True)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'))
    room_number = db.Column(db.String(10))
    capacity = db.Column(db.Integer)
    occupied_beds = db.Column(db.Integer, default=0)
    fee_per_semester = db.Column(db.Numeric(10,2))

    allocations = db.relationship('Allocation', backref='room', lazy=True)

class Allocation(db.Model):
    __tablename__ = 'allocations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date, nullable=True)