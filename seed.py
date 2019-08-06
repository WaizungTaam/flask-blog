from random import choice, sample, randint
from string import capwords
import click
from faker import Faker
from flask import url_for
from sqlalchemy.sql.expression import func
from blog import app
from app import db

fake = Faker()

@app.cli.command('seed')
@click.argument('table')
@click.option('--count', '-c', type=int, default=1)
def seed(table, count):
    if table == 'users':
        seed_users(count)
    elif table == 'posts':
        seed_posts(count)

def seed_users(count):
    from app.user.models import User, Profile
    for _ in range(count):
        while True:
            user = User(fake.user_name(), '123456')
            profile = Profile(
                user=user,
                name=fake.name(),
                gender=choice(['Male', 'Female', 'Others']),
                birthday=fake.date_of_birth(),
                phone=fake.phone_number(),
                email=fake.email(),
                location=fake.city(),
                about=fake.paragraph(),
                avatar='/avatars/default-avatar.png'
            )
            try:
                db.session.add(user)
                db.session.add(profile)
                db.session.commit()
            except:
                db.session.rollback()
            else:
                break
    print('Added {} users'.format(count))

def seed_posts(count):
    from app.post.models import Post, Comment
    from app.post.utils import make_abstract, parse_tags
    from app.user.models import User
    if User.query.count() == 0:
        print('Users required.')
        return
    for _ in range(count):
        title = capwords(fake.sentence()[:-1])
        content = fake.text(max_nb_chars=2000)
        content = '<p>' + content.replace('\n', '</p><p>') + '</p>'
        tags = title.lower().split(' ')
        tags = ' '.join(sample(tags, min(len(tags), randint(1, 5))))
        time = fake.past_datetime()
        post = Post(
            title=title,
            content=content,
            abstract=make_abstract(content),
            author=User.query.order_by(func.rand()).first(),
            tags=parse_tags(tags, ' '),
            ctime=time,
            mtime=time
        )
        db.session.add(post)
        for _ in range(randint(0, 10)):
            comment = Comment(
                content=fake.paragraph(),
                author=User.query.order_by(func.rand()).first(),
                post=post,
                time=fake.date_time_between(start_date=time)
            )
            db.session.add(comment)
    db.session.commit()
    print('Added {} posts'.format(count))
