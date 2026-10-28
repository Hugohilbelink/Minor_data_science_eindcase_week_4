# CO2 en welvaart

[Open het dashboard](https://minor-data-science-co2-welvaart.streamlit.app/)

Individuele eindopdracht IDS 2026–2027 van Hugo Hilbelink. Casus 5, richting A: welke landen combineren economische groei met een absolute daling van CO2, en waar daalt alleen de uitstoot per eenheid bbp?

## Starten op je eigen laptop

Op Hugo's laptop kun je in VS Code klikken op **Run → Start Debugging**. Kies **Start dashboard** als er meerdere startinstellingen zijn. Dit werkt met de map `dashboard` of de hoofdmap `Minor Data Science` geopend. De lokale startinstellingen staan in de verborgen map `.vscode` en hoeven niet naar GitHub of Brightspace.

De browser opent de lokale app via `localhost`. Laat de automatisch geopende terminal draaien. Pas de code aan in `app.py`, sla op met **Ctrl+S** en klik zo nodig op **Rerun** in de browser.

Voor een nieuwe installatie op een andere computer zijn dit de commando's vanuit deze map:

```bash
pip install -r requirements.txt
streamlit run app.py
```

De meegeleverde `data/bronnen.zip` is voldoende. Het dashboard doet geen API-aanroepen en de kaart gebruikt lokale geometrie zonder externe kaarttegels. Houd het archief ingepakt.

## Wat heb je nodig voor welk onderdeel

De lokale eindopdrachtmap heeft drie onderdelen:

| Map | Waarvoor gebruik je deze? |
| --- | --- |
| `dashboard` | De werkende app, code, data en je oefenmateriaal. Deze map is aan GitHub gekoppeld. |
| `opdracht` | De oorspronkelijke uitleg van de docent, casusbeschrijving, rubric en oefenset. Deze blijven lokaal als naslag. |
| `inleveren` | Het ZIP-bestand dat je op Brightspace inlevert. |

| Bestand in dashboard | Waarvoor nodig? | In het Brightspace-pakket? |
| --- | --- | --- |
| `app.py` | Dashboard tonen en live code aanpassen tijdens het assessment. | Ja |
| `teksten.py` | De vaste schermteksten en opmaak laden. Dit bestand hoort bij app.py. | Ja |
| `data/bronnen.zip` | Lokale data voor het dashboard; niet uitpakken of verwijderen. | Ja |
| `data_ophalen.py` | Laten zien hoe je de data hebt verzameld. Tijdens het assessment hoef je dit niet uit te voeren. | Ja |
| `requirements.txt` | Vastleggen welke Python-pakketten nodig zijn om de app te installeren. | Ja |
| `documentatie/data_verantwoording.md` | Uitleg over bronnen, ophalen, koppelen en ontbrekende gegevens. | Ja, in de ZIP heet dit `data_verantwoording.md`. |
| `documentatie/Spreektekst_case_5_8_minuten.docx` | Je presentatie oefenen met tijdschema en klikroute. | Nee, voor jezelf |
| `documentatie/Oefenen_live_coding_case_5.docx` | De 32 live-codingoefeningen met uitleg en antwoorden oefenen. | Nee, voor jezelf |
| `README.md` | Dit overzicht en de gebruiksaanwijzing teruglezen. | Nee |
| `.gitignore` | Tijdelijke bestanden en lokale instellingen buiten GitHub houden. | Nee, wel bewaren |
| `.vscode/launch.json` | De klikbare startinstelling op jouw laptop gebruiken. | Nee, lokaal bewaren |
| `.git` | De koppeling en versiegeschiedenis met GitHub bewaren. | Nee, lokaal bewaren |

Voor Brightspace gebruik je **`inleveren/Case_5A_Hugo_Hilbelink.zip`** in de bovenliggende eindopdrachtmap. Het bevat de vijf vereiste onderdelen, verdeeld over zes bestanden: de dashboardcode bestaat uit `app.py` en `teksten.py`. Je levert de spreektekst en oefeningen niet mee in. Als je code, data of data-verantwoording verandert, moet het inleverpakket opnieuw worden bijgewerkt.

Voor de online versie blijven app, data, ophaalscript, verantwoording en requirements in GitHub staan. De online app start automatisch; je lokale VS Code-startinstelling is daarvoor niet nodig.

In de grote schoolmap `Minor Data Science` staat ook `.venv`: dat is de Python-omgeving waarmee je lokale app draait. Laat die map en de `.vscode`-map van die hoofdmap staan.

## Bestanden

- `app.py`: het volledige dashboard met genummerde blokken, van inlezen en samenvoegen tot filters, grafieken en statistiek.
- `teksten.py`: alleen vaste schermteksten, labels en opmaak. Alle berekeningen, filters en grafieklogica blijven in `app.py`.
- `data_ophalen.py`: apart ophaalscript met requests en paginering; schrijft een lokale snapshot.
- `data/bronnen.zip`: oorspronkelijke CO2-data en codeboek, Wereldbankdata en metadata, kaartvlakken en bronverantwoording met SHA256-controlesommen.
- `documentatie/data_verantwoording.md`: korte verantwoording voor het inleveren.
- `documentatie/Oefenen_live_coding_case_5.docx`: 32 aangepaste oefeningen, hints, oplossingen en presentatievoorbereiding.
- `documentatie/Spreektekst_case_5_8_minuten.docx`: spreektekst in de ik-vorm met tijdschema, klikroute en aparte naslag voor vragen.
- `requirements.txt`: benodigde Python-pakketten. Python 3.12 of 3.13 aanbevolen voor Streamlit Community Cloud.

## Data opnieuw ophalen

```bash
python data_ophalen.py
python data_ophalen.py --vernieuw
```

Het eerste commando bewaart een bestaande snapshot. Het tweede vervangt bewust de snapshot door nieuwe bronversies; uitkomsten kunnen daardoor veranderen. Maak eerst een kopie als je de huidige inzendversie wilt bewaren.

## Analyse

### De code leren lezen

De code sluit aan op de basis uit Introduction to Python, Intermediate Python, Data Manipulation with pandas, Cleaning Data in Python en de Plotly- en functieonderwerpen in je DataCamp-overzicht. De concrete voorbeelden voor koppelen en filters komen ook uit je werkcolleges.

Begin met **blok 6** (filters) en **blok 7** (KPI's). Daarna lees je **blok 3**: `dropna` sluit ontbrekende meetwaarden uit, gewone vergelijkingen controleren de startwaarden, en nieuwe kolommen berekenen groei en intensiteit. **Blok 2** leest de bestanden en koppelt met `merge`.

`puntenwolk(data, y_kolom)` maakt één puntenwolk; `toon_grafiek(fig)` toont een grafiek met dezelfde opmaak. De tijdlijn gebruikt een jaartabel met een `left` merge en `px.line` met drie kolommen. De regressielijn heeft alleen twee eindpunten nodig. NumPy, `melt` en de keten `set_index → reindex → reset_index` zijn daarvoor niet meer nodig.

De statistische bibliotheekfuncties `linregress` en `t.ppf`, de Streamlit-cache en de kaartinstellingen blijven nodig voor deze opdracht. In het oefendocument staat wat je over de uitkomsten, cache en bronkeuzes moet kunnen uitleggen. De elf genummerde blokken en alle analyse-uitkomsten zijn behouden.

De app koppelt op ISO-landcode **en jaar**, controleert een-op-eenrelaties en sluit regionale totalen uit. Ontbrekende meetwaarden blijven ontbreken. De standaardvergelijking is 2000–2023; het eindjaar is bewust niet het coronajaar 2020. Via de filters zijn andere periodes, regio's en landen te onderzoeken.

Absolute ontkoppeling: reëel bbp groeit en totale territoriale CO2 daalt. Alleen relatieve ontkoppeling: reëel bbp groeit en CO2 per eenheid bbp daalt, terwijl de totale uitstoot niet daalt. Landen zonder bbp-groei krijgen een aparte categorie. De hoofdmaat is territoriale CO2, exclusief landgebruik; consumptiegebaseerde uitstoot dient als controle voor verplaatsing van productie.

Een eenvoudige regressie tussen landen toont helling, R², p-waarde en een klassiek 95%-interval. Dit is een beschrijving van samenhang, geen causaal bewijs. De landentijdlijn voorkomt dat alleen twee eindpunten als een voortdurende trend worden voorgesteld.

## Bronnen en code

- [Our World in Data CO2 dataset en bronlicenties](https://github.com/owid/co2-data). Global Carbon Budget 2025 en andere bronproducenten; zie het meegeleverde codeboek voor definities en attributie.
- [Wereldbank GDP constant 2015 US dollars](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD), World Development Indicators, CC BY 4.0.
- [Wereldbank API](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures).
- [Natural Earth landenkaart 1 op 110 miljoen](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson), publiek domein. Kleine landen kunnen ontbreken; zie de melding in het dashboard.
- [Streamlit Plotly](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart), [pandas merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html), [SciPy linregress](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html).

Dashboard en oefenmateriaal zijn gemaakt met hulp van Codex. AI is alleen toegestaan tijdens het bouwen; oefen de aanpassingen zelfstandig. De cursus-PDF's worden niet in deze repository opnieuw gepubliceerd.

## Streamlit Community Cloud

Koppel deze repository, branch `main`, met hoofdbestand `app.py`. De app leest de data uit dezelfde repository. Lokaal draaien blijft verplicht voor het assessment.
