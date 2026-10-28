"""Vaste schermteksten en opmaak. Alle berekeningen en filters staan in app.py."""

OPMAAK = """<style>
.stApp{background:#f5f7fa;color:#173044} [data-testid="stSidebar"]{background:#eaf0f4}
.block-container{max-width:1450px;padding-top:2.5rem}
h1,h2,h3{letter-spacing:-.025em} [data-testid="stMetric"]{background:white;border:1px solid #dce4e9;border-radius:12px;padding:16px}
</style>"""

INLEIDING = (
    'Een schonere economie kan toch méér CO₂ uitstoten. Vergelijk daarom de totale uitstoot én '
    'de uitstoot per eenheid bbp.'
)

KAART_UITLEG = (
    'Bekijk of landen met dezelfde ontwikkeling ruimtelijk bij elkaar liggen. Gebruik de regio-'
    ' en periodefilters om het patroon te vergelijken.'
)

PUNTEN_UITLEG = (
    'Rechts onder nul: absolute ontkoppeling. Rechts boven nul maar onder de stippellijn y = x:'
    ' alleen relatieve ontkoppeling. Links van nul groeit het bbp niet. Elk punt is één land; '
    'assen kunnen een verschillend schaalbereik hebben.'
)

REGRESSIE_UITLEG = (
    'Een eenvoudige regressie vergelijkt bbp-verandering met CO₂-verandering tussen landen in '
    'dezelfde selectie. Dit toetst samenhang; het verklaart niet waarom landen ontkoppelen.'
)

OORDEEL = (
    'Voor de klimaatvraag is de verandering in totale CO₂ de hoofdmaat: een lagere intensiteit '
    'kan samengaan met meer uitstoot. CO₂ per eenheid reëel bbp laat wel zien of productie '
    'schoner wordt. Toon beide naast elkaar. Territoriale uitstoot mist emissies die via import'
    ' worden uitbesteed; controleer daarom waar mogelijk ook consumptiegebaseerde uitstoot. '
    'Absolute ontkoppeling zegt op zichzelf niets over een eerlijke uitstootverdeling of een '
    'voldoende snelle daling.'
)

TABEL_UITLEG = (
    'Tien landen met de sterkste procentuele daling of kleinste stijging van totale CO₂ binnen '
    'je selectie.'
)

BRONNEN = (
    '- **Uitstoot:** [Our World in Data](https://github.com/owid/co2-data), jaarlijkse '
    'territoriale CO₂ uit fossiele brandstoffen en industrie; exclusief landgebruik. Eenheid: '
    'miljoen ton.\n- **Economie:** [Wereldbank '
    'NY.GDP.MKTP.KD](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD), totaal bbp in '
    'constante dollars van 2015.\n- **Kaart:** Natural Earth op schaal 1:110 miljoen, lokaal '
    'bewaard; grenzen zijn schematisch.\n- **Sleutel:** ISO-code plus jaar. Een landnaam kan '
    'verschillen; alleen een landcode koppelen zou alle jaren vermenigvuldigen.\n- **Ontbrekende'
    ' waarden:** geen nul, gemiddelde of interpolatie. Alleen geldige, positieve startwaarden '
    'en bbp-eindwaarden; CO₂-eindwaarde mag nul zijn.\n- **Definitie:** bbp > 0% en CO₂ < 0% = '
    'absoluut; bbp > 0%, CO₂ ≥ 0% en intensiteit < 0% = alleen relatief. Zonder bbp-groei volgt'
    ' een aparte categorie.'
)

KOPPELING_UITLEG = (
    'De tabel hieronder telt de koppeling van alle land-jaren vóór het analysefilter op '
    '1960–2024. Een gekoppelde rij kan nog ontbrekende meetwaarden bevatten.'
)

SLOT = (
    'De app leest uitsluitend lokale bestanden. Het ophaalscript en de data-verantwoording '
    'staan in de repository. Gebouwd met hulp van Codex; de gebruiker moet de code zelfstandig '
    'kunnen uitleggen en aanpassen.'
)

INLEES_HULP = (
    'Controleer of data/bronnen.zip naast app.py staat. Herstel de meegeleverde bestanden.'
)

HANDEL_ONTBREEKT = (
    'Voor dit land ontbreken geldige consumptiegebaseerde eindpunten. Verplaatsing van '
    'productie naar het buitenland is hier niet te controleren.'
)

REGRESSIE_BEPERKING = (
    'Elk land weegt even zwaar. Het interval veronderstelt onafhankelijke fouten met constante '
    'variantie; landen beïnvloeden elkaar en uitschieters kunnen de uitkomst sturen. Dit is '
    "modelonzekerheid, geen meetonzekerheid van CO₂. Vergelijk regio's en andere periodes om de"
    ' gevoeligheid te onderzoeken.'
)

REGRESSIE_TE_WEINIG = (
    'Voor regressie zijn minimaal vijf landen en variatie in beide grootheden nodig. Verruim de'
    ' selectie.'
)

ASSEN = {
    "bbp_groei": "Verandering re?el bbp (%)",
    "co2_groei": "Verandering totale CO? (%)",
    "intensiteit_groei": "Verandering CO? per eenheid bbp (%)",
}
