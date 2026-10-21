# buildingsmart.no

Kildekoden til nettsiden til buildingSMART Norge. Siden driftes på Wix (Wix Headless).

## Hva ligger hvor

| Mappe / fil | Innhold |
|---|---|
| `site/` | Den ferdige nettsiden: HTML-sider, stilark (`assets/stil.css`) og skript (`assets/bsn.js`). Det er dette som lastes opp til Wix. |
| `site.zip` | Det samme som `site/`, pakket som én fil for opplasting. |
| `site_src/` | Felles filer (stilark og skript) som kopieres inn i `site/` ved bygging. |
| `build/gen.py` | Programmet som lager alle sidene i `site/` ut fra innholdet i `kilde/`. |
| `kilde/` | Innholdet som ble hentet fra den gamle Framer-siden (tekst, bilder og metadata), og startdata for Wix. |

## Hva redigeres hvor

**I Wix sitt kontrollpanel** (uten å røre koden):

- **Nyheter**: Blogg i kontrollpanelet. Nye innlegg vises automatisk på forsiden og på nyhetssiden.
- **Domener**: CMS-samlingen «Domener». Her ligger kort beskrivelse, «Passer for», domeneleder, bilde og LinkedIn.
- **Arrangementer**: Opprettes i Checkin. De dukker automatisk opp i kalenderen, på forsiden og på riktig domeneside (ut fra temaet i Checkin, f.eks. «Teknisk domene»).
- **Medlemmer**: CMS-samlingene «Medlemmer (navneliste)» og «Medlemslogoer (forsiden)».

**Faste sider** (Om oss, Standarder, domenetekster og lignende) endres i koden. Det gjøres enklest ved å be Claude om endringen. Claude oppdaterer filene her og publiserer på nytt.

## Bygge og publisere

```bash
python3 build/gen.py              # lager site/ på nytt
(cd site && zip -qr ../site.zip .)   # pakker for opplasting
```

Siden lastes opp til Wix-nettstedet med ID `d7a09c8e-a36f-45a8-9bb8-72b7f87abfc0`. Hver opplasting erstatter hele filsettet.

## Uavhengighet

Alt innholdet er vanlig HTML, CSS og JavaScript, og kan flyttes til en hvilken som helst webserver. Det redigerbare innholdet (nyheter, domener, arrangementer og medlemmer) ligger i Wix og kan eksporteres derfra.
