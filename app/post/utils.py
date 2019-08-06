from bs4 import BeautifulSoup, Comment
from app import db
from app.post.models import Tag

def visible(element):
    if element.parent.name in \
        ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def html2text(html, sep=' '):
    soup = BeautifulSoup(html, 'html.parser')
    texts = [t.strip() for t in soup.find_all(text=visible)]
    return sep.join(texts)

def make_abstract(content):
    content = html2text(content, ' ')
    if len(content) > 80:
        return content[:80] + ' ...'
    return content

def parse_tags(s, sep=','):
    names = list(set(t.strip() for t in s.split(sep)))
    names = [t for t in names if t != '']
    tags = []
    for name in names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    db.session.commit()
    return tags
