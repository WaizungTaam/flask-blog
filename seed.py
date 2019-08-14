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
    elif table == 'followers':
        seed_followers()
    else:
        print('flask seed {users,posts,followers} [-c]')

def seed_users(count):
    from app.user.models import User, Profile
    for _ in range(count):
        while True:
            user = User(
                username=fake.user_name(),
                password=User.make_password('123456')
            )
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
                print('Error')
                db.session.rollback()
            else:
                break
    print('Added {} users'.format(count))

def seed_posts(count):
    from app.post.models import Post, Comment
    from app.post.utils import make_content_text, parse_tags
    from app.user.models import User
    if User.query.count() == 0:
        print('Users required.')
        return
    for _ in range(count):
        title = capwords(fake.sentence()[:-1])
        content = fake.text(max_nb_chars=2000)
        content = '<p>' + content.replace('\n', '</p><p>') + '</p>'
        content_type = 'html'
        tags = title.lower().split(' ')
        tags = ' '.join(sample(tags, min(len(tags), randint(1, 5))))
        time = fake.past_datetime()
        post = Post(
            title=title,
            content=content,
            content_type=content_type,
            content_text=make_content_text(content, content_type),
            author=User.query.order_by(func.rand()).first(),
            tags=parse_tags(tags, ' '),
            ctime=time,
            mtime=time,
            read=randint(0, 1000)
        )
        post.set_related()
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

def seed_followers():
    from app.user.models import User
    for user in User.query.all():
        for i in range(randint(1, 5)):
            u = User.query.order_by(func.rand()).first()
            user.follow(u)
    db.session.commit()
    print('Added followers')
