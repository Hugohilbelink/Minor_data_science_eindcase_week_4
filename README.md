# CO2 en welvaart

[Open het dashboard](https://minor-data-science-co2-welvaart.streamlit.app/)

Individuele eindopdracht IDS 2026–2027 van Hugo Hilbelink. Casus 5, richting A: welke landen combineren economische groei met een absolute daling van CO2, en waar daalt alleen de uitstoot per eenheid bbp?

## Starten op je eigen laptop

Open een terminal in deze map:

```bash
pip install -r requirements.txt
streamlit run app.py
```

De meegeleverde `data/bronnen.zip` is voldoende. Het dashboard doet geen API-aanroepen en de kaart gebruikt lokale geometrie zonder externe kaarttegels. Houd het archief ingepakt.

## Bestanden

- `app.py`: het volledige dashboard met genummerde blokken, van inlezen en samenvoegen tot filters, grafieken en statistiek.
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
