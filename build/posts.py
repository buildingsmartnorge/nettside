import json,re,sys,urllib.parse
sys.path.insert(0,'build')
from htmltree import parse,N
d=json.load(open('pages_all.json')); m=json.load(open('imgmap.json'))
MND={'jan':1,'januar':1,'feb':2,'februar':2,'mars':3,'mar':3,'apr':4,'april':4,'mai':5,'juni':6,'jun':6,'juli':7,'jul':7,'aug':8,'august':8,'sep':9,'sept':9,'september':9,'okt':10,'oktober':10,'nov':11,'november':11,'des':12,'desember':12}
def pdate(t):
    mm=re.match(r'\s*(\d+)\.\s*([a-zæøå]+)\.?\s*(\d{4})',t)
    return f"{mm.group(3)}-{MND[mm.group(2)]:02d}-{int(mm.group(1)):02d}T09:00:00Z" if mm else None
def ascii_slug(s):
    s=urllib.parse.unquote(s).lower()
    for a,b in (('æ','ae'),('ø','o'),('å','a'),('–','-'),('(',''),(')','')): s=s.replace(a,b)
    s=re.sub(r'[^a-z0-9-]+','-',s); s=re.sub(r'-{2,}','-',s).strip('-')
    return s
def wixid(src):
    k=src.split('/images/')[-1]; return m.get(k)
cnt=[0]
def nid(): cnt[0]+=1; return f"n{cnt[0]}"
def inline(node,decos,out):
    for k in node.kids:
        if isinstance(k,str):
            t=k
            if t: out.append({'type':'TEXT','id':'','nodes':[],'textData':{'text':t,'decorations':list(decos)}})
        else:
            dd=list(decos)
            if k.tag=='strong': dd.append({'type':'BOLD','fontWeightValue':700})
            elif k.tag=='em': dd.append({'type':'ITALIC','italicData':True})
            elif k.tag=='a' and k.attrs.get('href'):
                href=k.attrs['href']
                dd.append({'type':'LINK','linkData':{'link':{'url':href,'target':'BLANK' if 'buildingsmart.no' not in href else 'SELF'}}})
            if k.tag=='br': out.append({'type':'TEXT','id':'','nodes':[],'textData':{'text':'\n','decorations':[]}}); continue
            inline(k,dd,out)
def para(node):
    kids=[]; inline(node,[],kids)
    # trim
    while kids and kids[-1]['textData']['text'].strip()=='' : kids.pop()
    while kids and kids[0]['textData']['text'].strip()=='' : kids.pop(0)
    if kids:
        kids[0]['textData']['text']=kids[0]['textData']['text'].lstrip()
        kids[-1]['textData']['text']=kids[-1]['textData']['text'].rstrip()
    return kids
def block(node,out):
    for k in node.kids:
        if isinstance(k,str):
            if k.strip(): out.append({'type':'PARAGRAPH','id':nid(),'nodes':[{'type':'TEXT','id':'','nodes':[],'textData':{'text':k.strip(),'decorations':[]}}],'paragraphData':{}})
            continue
        t=k.tag
        if t in('p',):
            kids=para(k)
            if not kids: continue
            out.append({'type':'PARAGRAPH','id':nid(),'nodes':kids,'paragraphData':{}})
        elif t in('h1','h2','h3','h4','h5','h6'):
            kids=para(k)
            if kids: out.append({'type':'HEADING','id':nid(),'nodes':kids,'headingData':{'level':3 if t in('h2','h3') else 4}})
        elif t in('ul','ol'):
            items=[]
            for li in k.kids:
                if isinstance(li,N) and li.tag=='li':
                    inner=[]; block(li,inner)
                    if not inner:
                        kk=para(li)
                        if kk: inner=[{'type':'PARAGRAPH','id':nid(),'nodes':kk,'paragraphData':{}}]
                    inner=[x for x in inner if x['type']=='PARAGRAPH'] or inner
                    if inner: items.append({'type':'LIST_ITEM','id':nid(),'nodes':inner})
            if items: out.append({'type':'BULLETED_LIST' if t=='ul' else 'ORDERED_LIST','id':nid(),'nodes':items,('bulletedListData' if t=='ul' else 'orderedListData'):{'indentation':0}})
        elif t=='img':
            w=wixid(k.attrs.get('src',''))
            if w: out.append({'type':'IMAGE','id':nid(),'nodes':[],'imageData':{'containerData':{'width':{'size':'CONTENT'},'alignment':'CENTER'},'image':{'src':{'id':w}}}})
        elif t=='a' and not k.text().strip():
            continue
        else:
            block(k,out)
posts=[]
for path,h in d.items():
    if not path.startswith('/nyheter/'): continue
    slug=path.split('/nyheter/')[1]
    h=re.sub(r'<p><a href="https://buildingsmart.no/nyheter">Tilbake til oversikten</a></p><a href="https://buildingsmart.no/nyheter"></a>','',h)
    title=re.search(r'<h2>(.*?)</h2>',h).group(1)
    h=h.replace(f'<h2>{title}</h2>','',1)
    dm=re.match(r'\s*<p>([^<]*)</p>',h); date=pdate(dm.group(1)); h=h[dm.end():]
    im=re.match(r'\s*<img src="([^"]+)"[^>]*>',h); cover=wixid(im.group(1)) if im else None
    if im: h=h[im.end():]
    caption=None
    cm=re.match(r'\s*<p>([^<]{0,300})</p>',h)
    if cm and re.search(r'(Foto|Bilde|Illustrasjon|Fra venstre|Fv\.)',cm.group(1)):
        caption=cm.group(1).strip(); h=h[cm.end():]
    cnt[0]=0
    nodes=[]
    if caption: nodes.append({'type':'PARAGRAPH','id':nid(),'nodes':[{'type':'TEXT','id':'','nodes':[],'textData':{'text':caption,'decorations':[{'type':'ITALIC','italicData':True}]}}],'paragraphData':{}})
    block(parse(h),nodes)
    import html as HH
    posts.append({'oldSlug':slug,'seoSlug':ascii_slug(slug),'title':HH.unescape(title),'firstPublishedDate':date,'cover':cover,'richContent':{'nodes':nodes}})
posts.sort(key=lambda p:p['firstPublishedDate'])
for p in posts: print(p['firstPublishedDate'],p['seoSlug'],p['cover'] is not None,len(p['richContent']['nodes']))
json.dump(posts,open('posts.json','w'),ensure_ascii=False)
