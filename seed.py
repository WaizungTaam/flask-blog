from random import choice
import click
from faker import Faker
from flask import url_for
from blog import app
from app import db

fake = Faker()

@app.cli.command('seed')
@click.argument('table')
@click.option('--count', '-c', type=int, default=1)
def seed(table, count):
    if table == 'users':
        seed_users(count)

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
