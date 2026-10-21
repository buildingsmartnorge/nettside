"""Bygger buildingsmart.no som statiske filer fra innholdet hentet fra Framer-siden.
Kjør: python3 build/gen.py  (fra mappen bsn/). Resultat i site/."""
import json, re, os, shutil, html, urllib.parse

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROT)
D = json.load(open('kilde/pages_all.json'))
META = json.load(open('kilde/meta.json'))
IMG = json.load(open('kilde/imgmap.json'))
UT = 'site'
WS = 'https://static.wixstatic.com/media/'
LOGO = WS + IMG['mddfgWQuyR7T1LqJB00SouqZZE.png']
BSNK = WS + IMG['qeIPWxt6zpkWKMr5GLpivL7w1c.png']
POFINLOGO = WS + IMG['vPuU8EETl3PodADi626ilOwcmio.png']
POFINSTOR = WS + IMG['blKOc2xBa5Hq3FT4JsdTU0Phlhg.png']
HELT = WS + IMG['bLa7wqRp1CEUZDYIBjoE6RgSk.jpg']
OG = WS + IMG['1dx4XoztHb4wpflcqCuw4j72t8.png']
POFIN_ZIP = 'https://buildingsmartnorge.box.com/s/i4ew2sp5z1vcgkatkut4s86gcxmlfk1u'
# Avpublisert etter ønske (innholdet ligger fortsatt i kilde/ og kan tas inn igjen ved å fjerne linjene her)
SKIP = {'/standarder/internasjonale-standarder', '/en/standards/international-standards',
        '/om-oss/hvagjorvi2', '/en/om-oss/hvagjorvi2', '/en/home-testing', '/home-testing'}

# ---------- stier ----------
def translit(s):
    s = urllib.parse.unquote(s).lower()
    for a, b in (('æ', 'ae'), ('ø', 'o'), ('å', 'a'), ('–', '-'), ('—', '-'), ('(', ''), (')', '')):
        s = s.replace(a, b)
    s = re.sub(r'[^a-z0-9/-]+', '-', s)
    s = re.sub(r'-{2,}', '-', s)
    return '/'.join(p.strip('-') for p in s.split('/'))

# EN-sider som har eget navn i Framer -> tilsvarende norsk sti
EN_ALIAS = {
    '/en/standards/consultation': '/standarder/h%C3%B8ring',
    '/en/standards/international-standards': '/standarder/internasjonale-standarder',
    '/en/standards/kort-forklart': '/standarder/kort-forklart',
    '/en/standards/publications-and-guides': '/standarder/publikasjoner-og-veiledninger',
    '/en/standards/standardiseringsarbeid': '/standarder/standardiseringsarbeid',
    '/en/om-oss/contact': '/om-oss/kontakt',
    '/en/nyheter/consultation-of-new-guide---ifc-for-beginners': '/nyheter/h%C3%B8ring-av-ny-veileder---ifc-for-begynnere',
}

def no_sti(framer):
    """Framer-sti (NO eller EN) -> norsk Framer-sti."""
    framer = framer.split('#')[0].split('?')[0]
    if framer in ('/en', '/en/'): return '/'
    if framer.startswith('/en/'):
        return EN_ALIAS.get(framer, framer[3:])
    return framer or '/'

def fil(framer_no, en=False):
    """Norsk Framer-sti -> filsti i den nye siden (uten ledende /)."""
    t = translit(framer_no).strip('/')
    base = 'index.html' if not t else t + '.html'
    return ('en/' + base) if en else base

def url(framer_no, en=False):
    f = fil(framer_no, en)
    if f == 'index.html': return '/'
    if f == 'en/index.html': return '/en/'
    return '/' + f

# ---------- navigasjon ----------
NAV = [
    ('Om oss', 'About us', [
        ('Ta kontakt', 'Contact us', '/om-oss/kontakt'), ('Hva gjør vi?', 'What do we do?', '/om-oss/hvagjorvi'),
        ('Medlemskap', 'Membership', '/om-oss/medlemskap'), ('Vårt økosystem', 'Our ecosystem', '/om-oss/okosystemet'),
        ('Vedtekter', 'Statutes', '/om-oss/vedtekter'), ('Strategi og årsmøte', 'Strategy and annual meeting', '/om-oss/strategi'),
        ('Bærekraftsprofil', 'Sustainability profile', '/om-oss/baerekraftsprofil'),
        ('Personvernerklæring', 'Privacy policy', '/om-oss/personvernserklaering')]),
    ('Standarder', 'Standards', [
        ('POFIN', 'POFIN', '/pofin'), ('Publikasjoner', 'Publications', '/standarder/publikasjoner-og-veiledninger'),
        ('Standardiseringsarbeid', 'Standardisation work', '/standarder/standardiseringsarbeid'),
        ('Kort forklart', 'Briefly explained', '/standarder/kort-forklart'), ('Høring', 'Consultation', '/standarder/h%C3%B8ring')]),
    ('Fagnettverk', 'Network', [
        ('Domener', 'Domains', '/fagnettverk/fagnettverket', 'grp'),
        ('Produktdomene', 'Product domain', '/fagnettverk/produktdomene', 'inn'),
        ('Teknisk domene', 'Technical domain', '/fagnettverk/teknisk-domene', 'inn'),
        ('Infrastrukturdomene', 'Infrastructure domain', '/fagnettverk/infradomene', 'inn'),
        ('Bærekraftdomene', 'Sustainability domain', '/fagnettverk/b%C3%A6rekraft-domene', 'inn'),
        ('Juridisk domene', 'Legal domain', '/fagnettverk/juridisk-domene', 'inn'),
        ('Endringsledelsesdomene', 'Change management domain', '/fagnettverk/endringsledelsesdomene', 'inn'),
        ('Byggherre og eierdomene', 'Builder and owner domain', '/fagnettverk/byggherre-og-eierdomene', 'inn'),
        ('Arbeidsgrupper', 'Working groups', '/fagnettverk/arbeidsgrupper', 'grp'),
        ('Armeringsgruppen', 'Reinforcement group', '/fagnettverk/arbeidsgrupper/armeringsgruppen', 'inn'),
        ('VA-gruppen', 'Water and sewage group', '/fagnettverk/arbeidsgrupper/va-gruppen', 'inn'),
        ('Høyspentgruppen', 'High-voltage group', '/fagnettverk/arbeidsgrupper/h%C3%B8yspentgruppen', 'inn'),
        ('Medlemmer', 'Members', '/fagnettverk/medlemmer', 'grp'),
        ('Faglig Onsdag', 'Faglig Onsdag webinars', '/fagnettverk/faglig-onsdag', 'grp'),
        ('BIMpraten', 'BIMpraten podcast', '/fagnettverk/bimpraten', 'grp'),
        ('Ressurser', 'Resources', '/fagnettverk/ressurser', 'grp')]),
    ('Hva skjer', "What's on", [
        ('Kalender', 'Calendar', '/arrangementer'), ('Nyheter', 'News', '/nyheter'), ('bSNK', 'bSNK', 'https://bsnk.no')]),
]

def nav_html(en, framer_no):
    li = []
    for i, (no, eng, items) in enumerate(NAV):
        bred = ''
        lenker = []
        for it in items:
            tekst = it[1] if en else it[0]
            href = it[2] if it[2].startswith('http') else url(it[2], en)
            kl = f' class="{it[3]}"' if len(it) > 3 else ''
            lenker.append(f'<li><a{kl} href="{href}">{html.escape(tekst)}</a></li>')
        li.append(f'<li><button aria-expanded="false">{eng if en else no}</button><ul class="under{bred}">{"".join(lenker)}</ul></li>')
        if i == 1:
            li.append(f'<li><a href="https://www.bsnk.no/" title="buildingSMART Norge Kompetanse"><img src="{BSNK}" alt="bSNK"></a></li>')
            li.append(f'<li><a href="{url("/pofin", en)}" title="POFIN"><img src="{POFINLOGO}" alt="POFIN"></a></li>')
    annen = url(framer_no, not en)
    return f'''<header class="topp"><div class="wrap">
<a class="logo" href="{url('/', en)}"><img src="{LOGO}" alt="buildingSMART Norge" width="178" height="40"></a>
<ul class="meny">{''.join(li)}</ul>
<div class="hoyre"><a class="knapp mork" href="{url('/bli-medlem', en)}">{'Become a member' if en else 'Bli medlem'}<span class="pil">→</span></a>
<div class="sprak"><button aria-label="{'Language' if en else 'Språk'}">{'EN' if en else 'NO'}</button><ul>
<li><a href="{url(framer_no, False)}" lang="no"{' aria-current="true"' if not en else ''}>Norsk</a></li>
<li><a href="{url(framer_no, True)}" lang="en"{' aria-current="true"' if en else ''}>English</a></li></ul></div>
<button class="burger" aria-label="Meny"><span></span><span></span><span></span></button></div>
</div></header>'''

def bunn_html(en):
    return f'''<footer class="bunn"><div class="wrap">
<div><img src="{LOGO}" alt="buildingSMART Norge"><p style="margin-top:14px">{'Open standards for the lifecycle of buildings' if en else 'Åpne standarder for byggets livsløp'}</p></div>
<div><h4>Faktura / Invoice</h4><p>Elektronisk faktura, EHF / E-invoice: 889821302</p><p>Faktura på PDF / Invoice on PDF: 889821302-NO@azetsinvoice.com</p></div>
<div><h4>{'Contact' if en else 'Kontakt'}</h4><p><a href="mailto:administrasjonen@buildingsmart.no">administrasjonen@buildingsmart.no</a></p><p><a href="tel:+4792846995">(+47) 928 46 995</a></p>
<p style="margin-top:10px"><a href="{url('/om-oss/personvernserklaering', en)}">{'Privacy policy' if en else 'Personvernerklæring'}</a></p></div>
<p class="copy">Copyright © 2026 buildingSMART Norge</p>
</div></footer>'''

ROLLEVEILEDER = '''<iframe id="rv-modal" src="https://thorkildrs.github.io/Veileder-frontpage/rolleveileder-embed.html" style="position:fixed;inset:0;width:100%;height:100%;border:none;background:transparent;pointer-events:none;z-index:9999;" allowtransparency="true" title="Rolleveileder"></iframe>
<script>
  window.addEventListener('message', function(e) {
    var frame = document.getElementById('rv-modal');
    if (e.data === 'openRolleveileder') {
      document.querySelectorAll('iframe').forEach(function(f) {
        try { f.contentWindow.postMessage('openRolleveileder', '*'); } catch(err) {}
      });
    }
    if (e.data === 'rolleveileder_opened' && frame) { frame.style.pointerEvents = 'auto'; }
    if (e.data === 'rolleveileder_closed' && frame) { frame.style.pointerEvents = 'none'; }
  });
</script>'''

def side(tittel, beskrivelse, body, en, framer_no, ekstra_head=''):
    t = html.escape(tittel)
    b = html.escape(beskrivelse or '')
    kanon = 'https://buildingsmart.no' + url(framer_no, en)
    return f'''<!doctype html>
<html lang="{'en' if en else 'no'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{b}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{b}">
<meta property="og:image" content="{OG}">
<meta property="og:type" content="website">
<link rel="canonical" href="{kanon}">
<link rel="alternate" hreflang="no" href="https://buildingsmart.no{url(framer_no, False)}">
<link rel="alternate" hreflang="en" href="https://buildingsmart.no{url(framer_no, True)}">
<link rel="icon" href="https://static.wixstatic.com/media/fab2f5_3e92e232dfee410a8e5461b650eab47a~mv2.png/v1/fit/w_64,h_64/ikon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/stil.css">
{ekstra_head}</head>
<body>
{nav_html(en, framer_no)}
<main>
{body}
</main>
{bunn_html(en)}
<script src="/assets/bsn.js" defer></script>
{ROLLEVEILEDER}
</body>
</html>
'''

# ---------- innholdsrensing ----------
def bytt_bilde(m):
    src = m.group(1)
    if 'framerusercontent.com/images/' in src:
        k = src.split('/images/')[1]
        if k in IMG: src = WS + IMG[k]
    return f'<img loading="lazy" src="{src}" alt="{m.group(2)}">'

def bytt_lenke(m, en):
    href = html.unescape(m.group(1))
    if href.startswith('https://buildingsmart.no'):
        rest = href[len('https://buildingsmart.no'):] or '/'
        sti, _, anker = rest.partition('#')
        if sti.startswith('/arrangementer/'): sti = '/arrangementer'
        if sti.startswith('/nyheter/') or sti.startswith('/en/nyheter/'):
            slug = translit(no_sti(sti).split('/nyheter/')[1])
            ny = ('/en' if en else '') + '/nyheter/innlegg.html?n=' + slug
        else:
            ny = url(no_sti(sti), en)
        if anker: ny += '#' + anker
        return f'<a href="{html.escape(ny)}">'
    ekstern = href.startswith('http')
    return f'<a href="{html.escape(href)}"' + (' target="_blank" rel="noopener">' if ekstern else '>')

def yt_knapp(vid):
    return f'<button class="yt" data-id="{vid}" aria-label="Spill av video"><img loading="lazy" src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt=""></button>'

def rens(h, en):
    h = re.sub(r'<img src="([^"]+)" alt="([^"]*)">', bytt_bilde, h)
    h = re.sub(r'<a href="([^"]+)">', lambda m: bytt_lenke(m, en), h)
    # YouTube-miniatyrer -> spillbare videoer
    h = re.sub(r'<img loading="lazy" src="https://i\.ytimg\.com/vi(?:_webp)?/([\w-]{11})/[^"]+" alt="[^"]*">', lambda m: yt_knapp(m.group(1)), h)
    # iframes
    def ifr(m):
        s = m.group(1)
        hoyder = {'podcasts.apple.com': 175, 'Kort-forklart': 680, 'kartlegg.buildingsmart.no': 770, 'bluetail': 2480, '30years': 641}
        hoyde = next((v for k, v in hoyder.items() if k in s), 700)
        kl = 'podkast' if 'podcasts.apple.com' in s else 'bred-ramme'
        return f'<iframe src="{s}" class="{kl}" style="height:{hoyde}px" loading="lazy" title="Innebygd innhold" allow="clipboard-write; fullscreen"></iframe>'
    h = re.sub(r'<iframe src="([^"]+)"></iframe>', ifr, h)
    # ankere fra Framer (kort-forklart)
    h = re.sub(r'<a id="([^"]+)"></a>', lambda m: f'<span class="anker" id="{m.group(1)}"></span>' if not re.fullmatch(r'[A-Za-z0-9_]{9}|services(-\d)?', m.group(1)) else '', h)
    h = re.sub(r'<p>\s*(<br>\s*)*</p>', '', h)
    h = re.sub(r'<a href="[^"]*"[^>]*>\s*</a>', '', h)
    # dobbel knappetekst fra Framer ("Mer om domenet" x2)
    h = re.sub(r'<p>([^<]{2,40})</p><p>\1</p>', r'<p>\1</p>', h)
    h = h.replace('\n', '')
    return h

def tittel_og_resten(h):
    h = re.sub(r'^\s*(<a id="[^"]+"></a>)+', '', h)
    m = re.match(r'\s*<h4>(.*?)</h4>', h)
    if m: return html.unescape(re.sub('<[^>]+>', '', m.group(1))), h[m.end():]
    m = re.match(r'\s*<h[1-3]>(.*?)</h[1-3]>', h)
    if m: return html.unescape(re.sub('<[^>]+>', '', m.group(1))), h[m.end():]
    return None, h

def innholdsside(framer, h, en):
    framer_no = no_sti(framer)
    tittel, rest = tittel_og_resten(h)
    meta = META.get(framer) or META.get(framer_no) or {}
    tittel = tittel or (meta.get('title') or 'buildingSMART Norge').split(' - ')[0]
    rest = rens(rest, en)
    rest = re.sub(r'<h4>', '<h2>', rest); rest = re.sub(r'</h4>', '</h2>', rest)
    return framer_no, tittel, meta.get('desc', ''), rest

# ---------- spesialsider ----------
def mailmojo_skjema(tag, tittel, en, velg=False):
    felt = ''
    if velg:
        valg = [('alle', 'Alle' if not en else 'All'), ('produktdomene', 'Produktdomene'), ('infradomene', 'Infradomene'), ('teknisk domene', 'Teknisk domene'),
                ('juridisk domene', 'Juridisk domene'), ('bærekraftdomene', 'Bærekraftdomene'), ('byggherre og eierdomene', 'Byggherre og eierdomene'), ('endringsledelsesdomene', 'Endringsledelsesdomene')]
        felt = (f'<label for="mm-tag">{"Domain – which domain do you want information about?" if en else "Domene – hvilket domene ønsker du informasjon om?"}</label>'
                '<select id="mm-tag" name="tagsadditional">' + ''.join(f'<option value="{v}">{t}</option>' for v, t in valg) + '</select>')
    else:
        felt = f'<input type="hidden" name="tagsadditional" value="{html.escape(tag)}">'
    return f'''<form class="skjema" method="post" action="https://buildingsmart.mailmojo.no/49711/s" target="_blank">
<h3>{html.escape(tittel)}</h3>
<label for="mm-email-{abs(hash(tittel))%9999}">{'Email address' if en else 'E-postadresse'}</label><input id="mm-email-{abs(hash(tittel))%9999}" type="email" name="email" required autocomplete="email">
<label for="mm-name-{abs(hash(tittel))%9999}">{'Name' if en else 'Navn'}</label><input id="mm-name-{abs(hash(tittel))%9999}" type="text" name="name" required autocomplete="name">
{felt}
<button class="knapp mork" type="submit">{'Sign me up' if en else 'Meld meg på'}<span class="pil">→</span></button>
</form>'''

DOMENE_SLUG = {'produktdomene': 'produktdomene', 'teknisk-domene': 'teknisk-domene', 'b%C3%A6rekraft-domene': 'baerekraft-domene',
               'juridisk-domene': 'juridisk-domene', 'infradomene': 'infradomene', 'byggherre-og-eierdomene': 'byggherre-og-eierdomene',
               'endringsledelsesdomene': 'endringsledelsesdomene'}
DOMENE_TAG = {'produktdomene': ('produktdomene', 'Produktdomenet'), 'teknisk-domene': ('teknisk domene', 'Teknisk domene'),
              'baerekraft-domene': ('bærekraftdomene', 'Bærekraftdomene'), 'juridisk-domene': ('juridisk domene', 'Juridisk domene'),
              'infradomene': ('infradomene', 'Infradomene'), 'byggherre-og-eierdomene': ('byggherre og eierdomene', 'Byggherre- og eierdomene'),
              'endringsledelsesdomene': ('endringsledelsesdomene', 'Endringsledelsesdomene')}

def domeneside(framer, h, en):
    framer_no, tittel, besk, rest = innholdsside(framer, h, en)
    slug = DOMENE_SLUG[framer_no.rsplit('/', 1)[1]]
    # fjern Framer-lederkortet (bilde + rolle + navn + e-post/LinkedIn) og "Kommende møter"-delen
    rest = re.split(r'<h2>(Kommende møter|Upcoming meetings|Upcoming events)</h2>', rest)[0]
    rest = re.sub(r'<img loading="lazy" src="[^"]+" alt="">(<p>[^<]*</p>){1,3}(<a [^>]*><p>Linkedin</p></a>|<p>Linkedin</p>)?\s*$', '', rest)
    rest = re.sub(r'<h2>(Passer spesielt|Especially suitable)[^<]*</h2>(<p>[^<.]{1,60}</p>)*', '', rest)
    tag, navn = DOMENE_TAG[slug]
    body = f'''<section class="wrap sidetopp"><h1>{html.escape(tittel)}</h1>
<div class="domenetags" data-wix="domenetags" data-domene="{slug}"></div></section>
<section class="wrap domeneside"><div class="innhold">{rest}</div>
<aside class="ledersokkel" data-wix="domeneleder" data-domene="{slug}"></aside></section>
<section class="wrap innhold" style="padding-top:0">
<div>{mailmojo_skjema(tag, ('Join ' if en else 'Meld deg inn i ') + navn, en)}</div>
<h2 style="margin-top:56px">{'Upcoming meetings' if en else 'Kommende møter'}</h2>
<div class="kort-rad" data-wix="arrangementer" data-domene="{slug}"><p class="laster">…</p></div>
</section>'''
    return framer_no, tittel, besk, body

def personkort(rest):
    """Gjør Framer-personkort (bilde + korte avsnitt + LinkedIn) om til et rutenett."""
    blokker = re.split(r'(<h2>.*?</h2>)', rest)
    ut = []
    for b in blokker:
        if b.startswith('<h2>'): ut.append(b); continue
        deler = re.split(r'(?=<img loading="lazy")', b)
        intro = deler[0]; kort = []
        for k in deler[1:]:
            m = re.match(r'<img loading="lazy" src="([^"]+)" alt="[^"]*">(.*)', k)
            if not m: intro += k; continue
            src, resten = m.groups()
            ps = re.findall(r'<p>(.*?)</p>', re.sub(r'<a [^>]*><p>Linkedin</p></a>', '', resten))
            li = re.search(r'<a href="([^"]+)"[^>]*><p>Linkedin</p></a>', resten)
            linje = ''
            if ps: linje += f'<p class="rolle">{ps[0]}</p>'
            if len(ps) > 1: linje += f'<p class="navn">{ps[1]}</p>'
            for x in ps[2:]:
                if '@' in x: linje += f'<p><a href="mailto:{x.strip()}">{x}</a></p>'
                elif re.match(r'^\+?[\d ]+$', x.strip()): linje += f'<p><a href="tel:{x.replace(" ", "")}">{x}</a></p>'
                else: linje += f'<p>{x}</p>'
            if li and li.group(1).rstrip('/') != 'https://www.linkedin.com': linje += f'<p><a href="{li.group(1)}" target="_blank" rel="noopener">LinkedIn</a></p>'
            kort.append(f'<div class="person"><img loading="lazy" src="{src}" alt="">{linje}</div>')
        ut.append(intro + (f'<div class="personer">{"".join(kort)}</div>' if kort else ''))
    return ''.join(ut)

def kf_bokser(h):
    i = h.find('<p>Oversikt</p>')
    if i < 0: i = h.find('<p>Overview</p>')
    if i < 0: return h
    j = h.find('<h4>', i)
    seg = h[i:j]
    ut = []
    grupper = re.split(r'<p>([^<]+)</p>(?=<a href)', seg)
    # grupper: [forord, kat1, innhold1, kat2, innhold2, ...]
    for k in range(1, len(grupper), 2):
        kat, innh = grupper[k].strip(), grupper[k + 1]
        bokser = []
        for href, inner in re.findall(r'<a href="[^"#]*#([^"]+)">(.*?)</a>', innh):
            deler = [html.unescape(x).strip() for x in re.findall(r'<p>(.*?)</p>', inner)]
            hoved, under = '', ''
            for d in deler:
                if d.startswith('('): under = d.strip('() ')
                elif hoved.endswith(('-', '/')): hoved += d
                else: hoved = (hoved + ' ' + d).strip()
            bokser.append(f'<a class="kf-boks" href="#{href}"><span>{html.escape(hoved)}</span>' + (f'<small>({html.escape(under)})</small>' if under else '') + '</a>')
        bred = ' bred' if any(len(re.sub('<[^>]+>', '', b)) > 26 for b in bokser) else ''
        ut.append(f'<h3 class="kf-gruppe">{html.escape(html.unescape(kat))}</h3><div class="kf-bokser{bred}">' + ''.join(bokser) + '</div>')
    return h[:i] + '<div class="kf-oversikt">' + ''.join(ut) + '</div>' + h[j:]

def publikasjoner(rest, en):
    intro_slutt = rest.find('</p>') + 4
    intro, resten = rest[:intro_slutt], rest[intro_slutt:]
    kort = []
    for m in re.finditer(r'<p>(.*?)</p><p>(.*?)</p><img loading="lazy" src="([^"]+)" alt="[^"]*">((?:<a href="[^"]+"[^>]*>(?:<p>.*?</p>)+</a>)*)', resten):
        tittel, tekst, bilde, lenker = m.groups()
        ll = ''.join(f'<a class="last" href="{a}" target="_blank" rel="noopener">{re.findall(r"<p>(.*?)</p>", inner)[0]} <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 10l5 5 5-5M4 19h16"/></svg></a>' for a, inner in re.findall(r'<a href="([^"]+)"[^>]*>((?:<p>.*?</p>)+)</a>', lenker))
        kort.append(f'<article class="pub"><div><h2>{tittel}</h2><p>{tekst}</p><div class="pub-lenker">{ll}</div></div><img loading="lazy" src="{bilde}" alt="{html.escape(re.sub("<[^>]+>", "", tittel))}"></article>')
    return intro + ''.join(kort)

def generell(framer, h, en):
    if no_sti(framer) == '/standarder/kort-forklart': h = kf_bokser(h)
    framer_no, tittel, besk, rest = innholdsside(framer, h, en)
    if framer_no == '/standarder/publikasjoner-og-veiledninger':
        body = f'<section class="wrap sidetopp"><h1>{html.escape(tittel)}</h1></section>\n<section class="wrap innhold bred">{publikasjoner(rest, en)}</section>'
        return framer_no, tittel, besk, body
    if framer_no == '/pofin': tittel = 'POFIN'
    bred = ''
    if framer_no == '/om-oss/kontakt':
        rest = personkort(rest); bred = ' bred'
    if framer_no == '/fagnettverk/medlemmer':
        intro = re.match(r'(<p>.*?</p>)', rest).group(1)
        rest = intro + '<ul class="navneliste" data-wix="medlemmer"><li class="laster">…</li></ul>'
        bred = ' bred'
    if framer_no in ('/fagnettverk/faglig-onsdag', '/pofin'):
        rest = re.sub(r'((?:<button class="yt".*?</button>)+)', r'<div class="video-rad">\1</div>', rest)
    if framer_no == '/fagnettverk/arbeidsgrupper':
        rest = re.sub(r'<p>(Mer om arbeidsgruppen|More about the working group)</p>', r'\1 →', rest)
    if framer_no == '/fagnettverk/fagnettverket':
        # erstatt den statiske domenelisten med den redigerbare fra Wix
        rest = re.split(r'<h2>(Aktive domener|Active domains)</h2>', rest)[0]
        rest += f'<h2>{"Active domains" if en else "Aktive domener"}</h2></section><section class="wrap" style="padding-bottom:80px"><div class="domener" data-wix="domener"><p class="laster">…</p></div>'
        bred = ''
    body = f'<section class="wrap sidetopp"><h1>{html.escape(tittel)}</h1></section>\n<section class="wrap innhold{bred}">{rest}</section>'
    return framer_no, tittel, besk, body

def arrangementer(framer, h, en):
    framer_no = '/arrangementer'
    tittel = 'Calendar' if en else 'Kalender'
    body = f'''<section class="wrap sidetopp"><h1>{tittel}</h1></section>
<section class="wrap innhold bred">
<div id="checkin_event_index"></div>
<script>
document.customerId = 12624;
document.calendarConfig = {{
	openRegistrationModal: false,
	view: 'TILE',
	showSearch: true,
	showTopics: true,
	showViewToggle: true,
	showOnlyForm: false,
	showAdditionalCourseDetails: true,
	language: '{'en' if en else 'nb'}',
	topics: null,
	style: {{
		searchButtonBgColor: 'rgba(31, 109, 187, 1)',
		searchButtonTextColor:  'rgba(255, 255, 255, 1)',
		searchButtonBorderRadius:  3,
		topicBadgeBgColor: 'rgba(252, 26, 7, 1)',
		topicBadgeTextColor: 'rgba(255, 255, 255, 1)',
		topicBadgeBorderRadius: 3,
		headerTextColor: 'rgba(28, 43, 57, 1)',
		bodyTextColor: 'rgba(28, 43, 57, 1)',
		backgroundColor: 'rgba(255, 255, 255, 1)',
		eventTileColor: 'rgba(28, 43, 57, 0)'
	}}
}}
</script>
<script async src="https://static.checkin.no/loaders/eventindex/loader.js"></script>
</section>'''
    return framer_no, tittel, ('Calendar of events from buildingSMART Norway' if en else 'Kalender over arrangementer i buildingSMART Norge'), body

def nyhetsliste(en):
    t = 'News' if en else 'Nyheter'
    body = f'''<section class="wrap sidetopp"><h1>{t}</h1></section>
<section class="wrap" style="padding-bottom:80px"><div class="kort-rad" data-wix="nyheter" data-antall="24"><p class="laster">…</p></div>
<p class="sentrert" style="margin-top:32px"><button class="knapp mork enkel" data-wix-mer="nyheter" hidden>{'Show more' if en else 'Vis flere'}</button></p></section>'''
    return '/nyheter', t, ('News from buildingSMART Norway' if en else 'Nyheter fra buildingSMART Norge'), body

def innlegg(en):
    body = f'''<section class="wrap sidetopp"><a class="tilbake" href="{url('/nyheter', en)}">← {'Back to the overview' if en else 'Tilbake til oversikten'}</a></section>
<article class="wrap innhold" data-wix="innlegg"><p class="laster">…</p></article>'''
    return body

def forside(h, en):
    E = en
    vid = re.findall(r'i\.ytimg\.com/vi(?:_webp)?/([\w-]{11})/', h)
    sett = []
    for v in vid:
        if v not in sett: sett.append(v)
    pod = re.search(r'<iframe src="(https://embed\.podcasts\.apple\.com[^"]+)"', h)
    kart = 'https://kartlegg.buildingsmart.no/'
    body = f'''<section class="helt"><div class="wrap"><div class="helt-kort">
<div><h1>{'Open standards for the lifecycle of buildings' if E else 'Åpne standarder for byggets livsløp'}</h1>
<p>{'buildingSMART Norway improves digital information flow in the construction and facilities management industry through open international standards.' if E else 'buildingSMART Norge forbedrer digital informasjonsflyt i BAE-næringen gjennom åpne internasjonale standarder.'}</p>
<div class="helt-knapper"><a class="knapp lys" href="{url('/bli-medlem', E)}">{"Let's talk" if E else 'Uforpliktende prat'}<span class="pil">→</span></a>
<a class="lenke" href="{url('/fagnettverk/fagnettverket', E)}">{'About the network' if E else 'Om nettverket'}</a></div></div>
<div class="helt-bilde"><img src="{HELT}" alt="" fetchpriority="high">
<a class="kartlegg" href="{kart}" target="_blank" rel="noopener"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#4aabff" stroke-width="1.6" stroke-linejoin="round"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z"/><path d="M9 4v14M15 6v14"/></svg>
<span>{'Map the openBIM maturity<br>of your project' if E else 'Kartlegg åpenBIM modenheten<br>i ditt prosjekt'}</span></a></div>
</div></div></section>

<section class="logoer"><div class="wrap"><p>{'Some of our members' if E else 'Noen av våre medlemmer'}</p>
<div class="rulle"><div class="rulle-spor" data-wix="logoer"></div></div></div></section>

<section class="seksjon"><div class="wrap pofin">
<div class="pofin-tittel"><h2>{'BIM made easy with' if E else 'BIM gjort enkelt med'}</h2><img src="{POFINSTOR}" alt="POFIN"></div>
<a class="pofin-last" href="{POFIN_ZIP}" target="_blank" rel="noopener"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 10l5 5 5-5M4 19h16"/></svg>{'Download POFIN here' if E else 'Last ned POFIN her'}</a>
<p class="ingress">{"POFIN is buildingSMART Norway's national framework for openBIM.<br>An industry standard that makes it easier to set the right requirements, agree on information deliveries<br>and follow up on deliveries in both projects and management" if E else 'POFIN er buildingSMART Norge sitt nasjonale rammeverk for åpenBIM.<br>En bransjestandard som gjør det enklere å stille riktige krav, avtale informasjonsleveranser<br>og følge opp leveranser i både prosjekt og forvaltning'}</p>
</div></section>

<section class="seksjon lys"><div class="wrap">
<div class="toppseksjon"><h2>{'Upcoming events' if E else 'Kommende arrangementer'}</h2><a class="merlenke" href="{url('/arrangementer', E)}">{'See the entire calendar here' if E else 'Se hele kalenderen her'} →</a></div>
<div class="kort-rad" data-wix="arrangementer" data-antall="3"><p class="laster">…</p></div>
</div></section>

<section class="seksjon"><div class="wrap">
<p class="overtittel">{'The network' if E else 'Nettverket'}</p>
<div class="toppseksjon"><h2>{'Explore our domains' if E else 'Utforsk våre domener'}</h2><a class="merlenke" href="{url('/fagnettverk/fagnettverket', E)}">{'About the network' if E else 'Om nettverket'} →</a></div>
<div class="domener karusell" data-wix="domener"><p class="laster">…</p></div>
</div></section>

<section class="seksjon lys"><div class="wrap">
<p class="overtittel">{'Stay updated' if E else 'Hold deg oppdatert'}</p>
<div class="toppseksjon"><h2>{'Latest news' if E else 'Siste nyheter'}</h2><a class="merlenke" href="{url('/nyheter', E)}">{'All news' if E else 'Alle nyheter'} →</a></div>
<div class="nyheter-rad" data-wix="nyheter" data-antall="3"><p class="laster">…</p></div>
{f'<div class="podkast"><iframe src="{pod.group(1)}" loading="lazy" title="BIMpraten" allow="autoplay *; encrypted-media *; clipboard-write"></iframe></div>' if pod else ''}
</div></section>

<section class="seksjon"><div class="wrap">
{mailmojo_skjema('', 'Stay updated – subscribe to the mailing list' if E else 'Hold deg oppdatert – meld deg på mailinglisten', E, velg=True).replace('class="skjema"', 'class="skjema sentrert"')}
</div></section>

<section class="seksjon lys"><div class="wrap">
<p class="overtittel">{"What's on?" if E else 'Hva skjer?'}</p>
<h2>{'Previous open meetings' if E else 'Tidligere åpne møter'}</h2>
<div class="video-rad">{''.join(yt_knapp(v) for v in sett)}</div>
</div></section>'''
    return body

# ---------- bygg ----------
def skriv(sti, innhold):
    p = os.path.join(UT, sti)
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    open(p, 'w').write(innhold)

def main():
    if os.path.exists(UT): shutil.rmtree(UT)
    shutil.copytree('site_src', UT)
    filer = []
    for framer, h in D.items():
        if framer in SKIP: continue
        en = framer.startswith('/en')
        fn = no_sti(framer)
        if fn.startswith('/nyheter/') or fn.startswith('/arrangementer/'): continue
        if fn == '/':
            body = forside(h, en)
            tittel = 'buildingSMART Norge' if not en else 'buildingSMART Norway'
            besk = META.get(framer, {}).get('desc') or ''
            skriv(fil('/', en), side(tittel, besk, body, en, '/'))
            filer.append(fil('/', en)); continue
        if fn == '/arrangementer':
            framer_no, tittel, besk, body = arrangementer(framer, h, en)
        elif fn == '/nyheter':
            framer_no, tittel, besk, body = nyhetsliste(en)
        elif fn.startswith('/fagnettverk/') and fn.rsplit('/', 1)[1] in DOMENE_SLUG and fn.count('/') == 2:
            framer_no, tittel, besk, body = domeneside(framer, h, en)
        else:
            framer_no, tittel, besk, body = generell(framer, h, en)
        doc = side(f'{tittel} – buildingSMART Norge', besk, body, en, framer_no)
        skriv(fil(framer_no, en), doc); filer.append(fil(framer_no, en))
    for en in (False, True):
        skriv(fil('/nyheter/innlegg', en), side('Nyheter – buildingSMART Norge', '', innlegg(en), en, '/nyheter'))
        filer.append(fil('/nyheter/innlegg', en))
    print(len(filer), 'sider')
    tot = 0
    for r, _, fs in os.walk(UT):
        for f in fs: tot += os.path.getsize(os.path.join(r, f))
    print('totalt', tot, 'byte')

if __name__ == '__main__':
    main()
