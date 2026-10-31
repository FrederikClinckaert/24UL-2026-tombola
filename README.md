# De groepstombola van de 24 Urenloop 2026: zo houden we het eerlijk

Vier groepen winnen een groepsprijs, en we kiezen ze zoals bij een tombola. Ook de groepen van de organisatoren doen
mee. Precies daarom hebben we het zo opgezet dat **niemand de uitslag kan sturen, ook de organisatoren niet, en dat
iedereen ze achteraf kan controleren.**

> **De feiten**
>
> | | |
> |---|---|
> | De ticketlijst | [`tombola_tickets.csv`](https://github.com/FrederikClinckaert/24UL-2026-tombola/blob/main/tombola_tickets.csv), bevroren op **29 oktober 2026 om 12:33** |
> | Vingerafdruk van de ticketlijst | `528c6c5b092380e8de2a82df1fed84cb4030fcd5f0612fda9a46fa93867a3cb6` |
> | Het willekeurige getal dat we gebruiken | **drand-ronde 33609412** |
> | Dat getal verschijnt op | **maandag 2 november 2026 om 16:00:00** (Belgische tijd). Vanaf dan staat het [hier](https://api.drand.sh/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971/public/33609412). |
> | De uitslag, met alle details | **[VOLGT NA DE TREKKING]** |
> | Het controleprogramma | [`tombola_draw.py`](https://github.com/FrederikClinckaert/24UL-2026-tombola/blob/main/tombola_draw.py) |
> | Alles staat op | [github.com/FrederikClinckaert/24UL-2026-tombola](https://github.com/FrederikClinckaert/24UL-2026-tombola) |

## De regels

- **Elk punt dat je groep scoorde, is één ticket (een lotje).** Een groep met 150 punten heeft 150 tickets, een
  groep met 20 punten heeft er 20.
- **Je kans is je aantal tickets gedeeld door alle tickets in de trekking.** Met 150 van de 1.000 tickets heb je
  15% kans op de 1e prijs.
- **We trekken de 4 prijzen één voor één, en een groep kan maar één keer winnen.** Wint een groep, dan gaan haar
  tickets uit de trekking. Er blijven minder tickets over, dus de kans van elke andere groep stijgt voor de volgende
  prijs.
- Groepen met 0 punten hebben geen tickets en kunnen dus niet winnen.

## Zo zorgen we dat niemand kan valsspelen

Stel je een tombola voor waarbij elk ticket een nummer heeft, en de winnende nummers uit een openbare lottomachine
komen die niemand in handen heeft. Het werkt in vier stappen:

1. **We bevriezen de ticketlijst.** Vóór de trekking leggen we de lijst van groepen en hun punten vast, en delen we
   die met iedereen: dat is [`tombola_tickets.csv`](tombola_tickets.csv) in deze repository. Daarbij hoort een
   *vingerafdruk*: een lange code die uit de lijst berekend wordt. Verander ook maar één punt, en de vingerafdruk
   wordt compleet anders. Vanaf dan kan niemand de lijst nog aanpassen zonder dat iedereen het ziet.

2. **We kondigen vooraf aan welk willekeurig getal we gebruiken.** Dat getal komt van **drand**, een openbare dienst
   die gerund wordt door onafhankelijke organisaties (Cloudflare en verschillende universiteiten en bedrijven). Elke
   3 seconden publiceert drand een nieuw willekeurig getal, en niemand kan dat getal kennen of beïnvloeden voor het
   verschijnt. Wij kondigen *nu* aan welk getal we gebruiken en wanneer het verschijnt, terwijl het nog niet bestaat.
   Zo kunnen we er geen kiezen dat ons toevallig goed uitkomt.

3. **Dat getal bepaalt de winnaars.** Een vaste regel, vooraf gepubliceerd, zet het willekeurige getal voor elke
   prijs om in een winnend ticketnummer. De groep die dat ticket heeft, wint. Het draaiende rad tijdens de trekking
   toont alleen de uitslag: het stopt op het winnende ticket.

4. **Je kunt het zelf controleren.** Na de trekking kan iedereen ze overdoen met de ticketlijst en het willekeurige
   getal, en dan kom je op dezelfde 4 winnaars uit. Het programma [`tombola_draw.py`](tombola_draw.py) in deze
   repository doet het in één stap (zie *Zelf controleren* hieronder). Je kunt het ook vragen aan iemand die handig
   is met computers.

## Waarom we dus niet kunnen valsspelen

| Wat je zou kunnen vermoeden | Waarom dat niet kan |
|---|---|
| "Ze hebben de punten achteraf aangepast." | De lijst en haar vingerafdruk werden vóór de trekking gedeeld. Elke wijziging geeft een andere vingerafdruk. |
| "Ze hebben een getal gekozen dat hen goed uitkwam." | We kondigden het getal aan voor het bestond. Niemand kende het vooraf, wij ook niet. |
| "Ze hebben getrokken tot hun groep won." | Hetzelfde getal geeft altijd dezelfde winnaars. Opnieuw trekken verandert niets. |
| "Het programma is vervalst." | De regel is gepubliceerd en het controleprogramma kan iedereen lezen. Iedereen kan de trekking overdoen en vergelijken. |

Het enige waar je zelf op moet letten: **de ticketlijst en het drand-getal moeten gedeeld zijn vóór dat getal
verschijnt.** Vergelijk de datum en het uur van onze aankondiging met het tijdstip bij "De feiten" hierboven.

## Wat je ziet tijdens de trekking

Op het scherm draait het rad voor elke prijs, en het stopt op het winnende ticket. De technische details laten we
van het scherm, maar ze komen meteen na de trekking allemaal hier te staan:

- het drand-getal van de aangekondigde ronde;
- voor elke prijs het winnende ticket, welke tickets elke groep had en ieders kans;
- de volledige uitvoer van `tombola_draw.py`, zodat je ze naast je eigen controle kunt leggen.

## Zelf controleren

Je hebt Python nodig. Op een Mac staat het er al op; op Windows installeer je het via
[python.org](https://www.python.org/downloads/). Je hoeft verder niets te installeren.

1. Download deze repository: de groene knop **Code → Download ZIP**, en pak de ZIP uit.
2. Open een terminal in die map en typ:

   ```bash
   python3 tombola_draw.py tombola_tickets.csv 33609412
   ```

   Op Windows typ je `python` in plaats van `python3`.

Het programma toont de vingerafdruk van de ticketlijst (vergelijk ze met die hierboven), haalt het drand-getal op, en
toont voor elke prijs welke tickets elke groep had, het winnende ticket en de winnaar.

Wil je precies weten hoe het willekeurige getal een ticketnummer wordt? Lees
[de technische uitleg](TECHNICAL.md) (in het Engels).
