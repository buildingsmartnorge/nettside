"""bSNK-konferansen (tidligere bsnk.no) som egen side under buildingsmart.no."""
import json, re, html

def lag(IMG, WS, en):
    d = json.load(open('kilde/bsnk.json'))['2026']
    pdf = json.load(open('kilde/pdfmap.json'))
    def bilde(u):
        k = u.split('/images/')[-1]
        return WS + IMG[k] if k in IMG else u
    def pdflenke(u):
        k = u.split('/assets/')[-1]
        return pdf.get(k, u)
    # --- program ---
    prog = d[d.index('<h1>Programmet</h1>') + len('<h1>Programmet</h1>'):d.index('<a id="speakers">')]
    tokens = re.findall(r'<(p|h5|h6)>(.*?)</\1>', prog, re.S)
    rader, cur = [], None
    for tag, inner in tokens:
        tekst = inner.strip()
        if tag == 'p' and re.fullmatch(r'\d\d:\d\d\s*-\s*\d\d:\d\d', re.sub('<[^>]+>', '', tekst).strip()):
            cur = {'tid': re.sub('<[^>]+>', '', tekst).strip().replace(' - ', '–'), 'tittel': '', 'tekst': [], 'lenke': None, 'talere': [], 'type': 'punkt'}
            rader.append(cur); continue
        if cur is None: continue
        if tag == 'h5':
            cur['tittel'] = tekst; cur['type'] = 'del' if tekst.upper().startswith('DEL ') else 'pause'
        elif tag == 'h6':
            cur['talere'].append(re.sub(r'<br>', '', tekst))
        else:
            m = re.search(r'<a href="([^"]+)">', tekst)
            if m: cur['lenke'] = pdflenke(m.group(1)); continue
            if 'Last ned presentasjonen' in tekst:
                # disse lenkene lå på et span-element i Framer og kom ikke med i uttrekket
                ekstra = {'13:00–13:15': 'KDfd2bLUflTKjKbd351w1jPkQBc.pdf', '13:15–13:30': '0ZBgnfxO7yPcY5lGBVujY282cI.pdf', '13:30–13:50': 'vPzxEE3imB3fMmfQIx8TaQ2f4U.pdf',
                         '14:25–14:45': 'vTOXeurwsY53TaivnWUZDj3Y2Nw.pdf', '14:45–15:05': 'YeB318sYDHSb5lNpmmebiYVMtN0.pdf'}
                if cur['tid'] in ekstra: cur['lenke'] = pdf[ekstra[cur['tid']]]
                continue
            if not cur['tittel']: cur['tittel'] = tekst
            else: cur['tekst'].append(tekst)
    # første rad (registrering) har tittel i p
    prog_html = []
    for r in rader:
        if r['type'] == 'del':
            prog_html.append(f'<div class="bk-del"><span>{r["tid"]}</span><h3>{r["tittel"]}</h3></div>')
        elif r['type'] == 'pause' or (not r['tekst'] and not r['talere']):
            prog_html.append(f'<div class="bk-pause"><span>{r["tid"]}</span><p>{r["tittel"]}</p></div>')
        else:
            last = f'<a class="last" href="{r["lenke"]}" target="_blank" rel="noopener">Last ned presentasjonen ↓</a>' if r['lenke'] else ''
            talere = ''.join(f'<p class="taler">{t}</p>' for t in r['talere'])
            prog_html.append(f'<div class="bk-punkt"><span>{r["tid"]}</span><div><h4>{r["tittel"]}</h4>' + ''.join(f'<p>{t}</p>' for t in r['tekst']) + talere + last + '</div></div>')
    # --- foredragsholdere ---
    fh = d[d.index('<h1>Foredragsholdere</h1>'):d.index('<a id="date">')]
    personer = re.findall(r'<img src="([^"]+)" alt="[^"]*"><h3>(.*?)</h3><p>(.*?)</p>(?:<p>(.*?)</p>)?', fh)
    pers_html = ''.join(f'<div class="person"><img loading="lazy" src="{bilde(s)}" alt="{html.escape(n)}"><p class="navn">{n}</p><p class="rolle">{(r or "").strip()}</p><p>{o.strip()}</p></div>' for s, n, o, r in personer)
    # --- sponsorer og bilder ---
    topp = d[:d.index('<a id="intro">')]
    sponsorer = re.findall(r'<img src="([^"]+)"', topp[topp.index('sponsorer og utstillere'):])
    spons_html = ''.join(f'<img loading="lazy" src="{bilde(s)}" alt="">' for s in sponsorer)
    karusell = []
    for s in re.findall(r'<li><img src="([^"]+)"', d[d.index('<a id="intro">'):d.index('<p>Om konferansen</p>')]):
        if s not in karusell: karusell.append(s)
    bilder_html = ''.join(f'<img loading="lazy" src="{bilde(s)}" alt="">' for s in karusell)
    b25 = json.load(open('kilde/bsnk.json'))['2025']
    bilder25 = ''.join(f'<img loading="lazy" src="{bilde(s)}" alt="bSNK 2025">' for s in re.findall(r'<img src="(https://framerusercontent[^"]+)" alt="">', b25))
    billett = 'https://event.checkin.no/195802/buildingsmart-norge-konferansen-2026-bsnk26'
    sponsor = 'https://event.checkin.no/216235/sponsor-utstiller-pamelding-buildingsmart-norge-konferansen'
    logo = WS + IMG['qeIPWxt6zpkWKMr5GLpivL7w1c.png']
    body = f'''<section class="bk-helt"><div class="wrap">
<img class="bk-logo" src="{logo}" alt="bSNK26">
<p class="bk-under">buildingSMART Norge-konferansen 2026</p>
<p class="bk-dato">15. april 2026</p>
<p>Clarion Hotel Oslo<br>Dronning Eufemias gate 15</p>
<nav class="bk-snarvei"><a href="#program">Program</a><a href="#foredragsholdere">Foredragsholdere</a><a href="https://buildingsmartnorge.box.com/s/3r5pe5nr9z2ksfu8e85onihuj465367h" target="_blank" rel="noopener">Bilder</a><a href="#tidligere">2025</a></nav>
</div></section>
<section class="wrap bk-spons"><p class="overtittel">Våre sponsorer og utstillere</p><div>{spons_html}</div></section>
<section class="wrap bk-om">
<div class="bk-bilder">{bilder_html}</div>
<div><p class="overtittel">Om konferansen</p><p class="ingress">buildingSMART Norge-konferansen er den årlige fagkonferansen til buildingSMART Norge. Konferansen er en sentral møteplass for digitalisering i bygg-, anlegg- og eiendomsbransjen, med særlig vekt på åpenBIM og åpne standarder.</p>
<p class="bk-knapper"><a class="knapp mork" href="{billett}" target="_blank" rel="noopener">Kjøp billett<span class="pil">→</span></a><a class="knapp enkel" style="border:1px solid var(--linje)" href="{sponsor}" target="_blank" rel="noopener">Bli sponsor eller utstiller</a></p></div>
</section>
<section class="seksjon lys" id="program"><div class="wrap"><h2>Programmet</h2><div class="bk-program">{''.join(prog_html)}</div></div></section>
<section class="seksjon" id="foredragsholdere"><div class="wrap"><h2>Foredragsholdere</h2><div class="personer">{pers_html}</div></div></section>
<section class="seksjon lys" id="tidligere"><div class="wrap"><h2>buildingSMART Norge-konferansen 2025</h2><div class="bk-bilder to">{bilder25}</div></div></section>'''
    return body
