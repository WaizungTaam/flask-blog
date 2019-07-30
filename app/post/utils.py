from bs4 import BeautifulSoup, Comment

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
