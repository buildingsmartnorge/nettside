from html.parser import HTMLParser
import html as H
VOID={'img','br','iframe'}
class N:
    def __init__(s,tag,attrs=None,parent=None): s.tag=tag; s.attrs=dict(attrs or {}); s.kids=[]; s.parent=parent
    def text(s): return ''.join(k if isinstance(k,str) else k.text() for k in s.kids)
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.root=N('root'); s.cur=s.root
    def handle_starttag(s,t,a):
        n=N(t,a,s.cur); s.cur.kids.append(n)
        if t not in VOID: s.cur=n
    def handle_endtag(s,t):
        if t in VOID: return
        c=s.cur
        while c is not s.root and c.tag!=t: c=c.parent
        if c is not s.root: s.cur=c.parent
    def handle_data(s,d): s.cur.kids.append(d)
def parse(h):
    p=P(); p.feed(h); return p.root
