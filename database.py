import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy import or_, create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session

db_url = "sqlite:///bot_db.sqlite"
engine = create_engine(db_url)

# session=sessionmaker(bind=engine)
session = Session(engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(Integer, primary_key=True)
    create_time = Column(DateTime, default=datetime.datetime.now)


class Ad(Base):
    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True)
    category = Column(String(32), index=True)
    title = Column(String(32), index=True, nullable=False, default='Announcement #')
    description = Column(String(255), index=True, nullable=False)
    image = Column(String(255), index=True, nullable=False)
    price = Column(Integer)
    create_time = Column(DateTime, default=datetime.datetime.now)
    author = Column(Integer)


class Favourite(Base):
    __tablename__ = 'favourites'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    ad_id = Column(Integer)
    create_time = Column(DateTime, default=datetime.datetime.now)


Base.metadata.create_all(bind=engine)


def addUser(telegram_id):
    user = User()
    user.telegram_id = telegram_id
    session.add(user)
    session.commit()


def userExists(telegram_id):
    print(dir(User))
    q = session.query(User)
    users = q.filter(User.telegram_id == telegram_id).all()
    if len(users) == 0:
        return False
    else:
        return True


def getAd(ad_id):
    q = session.query(Ad)
    ad = q.filter(Ad.id == ad_id).first()
    return ad


def addAd(category, title, description, image, price, author):
    ad = Ad()
    ad.category = category
    ad.title = title
    ad.description = description
    ad.image = image
    ad.price = price
    ad.author = author
    session.add(ad)
    session.commit()


def addFavourite(telegram_id, ad_id):
    fav = Favourite()
    fav.user_id = telegram_id
    fav.ad_id = ad_id
    session.add(fav)
    session.commit()


def searchAd(text):
    q = session.query(Ad)
    found = q.filter(or_(Ad.title.ilike(f'{text}%'), Ad.description.ilike(f'{text}%'))).all()
    return found


def searchFav(telegram_id):
    q = session.query(Favourite)
    found = q.filter(Favourite.user_id == telegram_id).all()
    return [getAd(f.id) for f in found]


def searchMy(telegram_id):
    q = session.query(Ad)
    found_ads = q.filter(Ad.author == telegram_id).all()
    return found_ads
