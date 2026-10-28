"""Casus 5A. Start: streamlit run app.py. Zoek op de genummerde blokken."""
from pathlib import Path
import json
from zipfile import ZipFile

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress, t
import streamlit as st

# 1 INSTELLINGEN
st.set_page_config(page_title="CO2 en welvaart", page_icon="🌍", layout="wide")
BESTAND = Path(__file__).parent / "data" / "bronnen.zip"
KLEUREN = {"Absoluut": "#087f68", "Alleen relatief": "#dd941b",
           "Geen ontkoppeling": "#c44b48", "Geen bbp-groei": "#637387"}
px.defaults.template = "plotly_white"


# 2 DATA INLEZEN EN KOPPELEN
@st.cache_data
def laad_data():
    """Lokale bronbestanden; geen API-aanroepen tijdens het dashboard."""
    with ZipFile(BESTAND) as archief:
        co2 = pd.read_csv(archief.open("owid-co2-data.csv"),
                          usecols=["iso_code", "country", "year", "co2", "consumption_co2"])
        bbp = pd.read_csv(archief.open("worldbank_gdp_constant_2015_usd.csv"))
        landen = pd.read_csv(archief.open("worldbank_country_metadata.csv"))
        kaart = json.loads(archief.read("landen.geojson"))
        bronnen = json.loads(archief.read("data_bronnen_case5.json"))
    # Landcodes zonder waarde en regionale totalen horen niet in de landenanalyse.
    co2 = co2.dropna(subset=["iso_code"])
    bbp = bbp.dropna(subset=["iso_code"])
    landen = landen.loc[~landen["is_aggregate"]].copy()
    co2 = co2.merge(landen[["iso_code", "region"]], on="iso_code", validate="many_to_one")
    bbp = bbp.merge(landen[["iso_code"]], on="iso_code", validate="many_to_one")
    data = co2.merge(bbp[["iso_code", "year", "gdp_constant_2015_usd"]],
                     on=["iso_code", "year"], how="outer", indicator=True,
                     validate="one_to_one")
    controle = data["_merge"].value_counts().rename_axis("Koppeling").reset_index(name="Rijen")
    # Vul alleen beschrijvingen aan, nooit de meetwaarden.
    namen = landen.set_index("iso_code")["country"]
    regios = landen.set_index("iso_code")["region"]
    data["country"] = data["country"].fillna(data["iso_code"].map(namen))
    data["region"] = data["region"].fillna(data["iso_code"].map(regios))
    for kolom in ["co2", "consumption_co2", "gdp_constant_2015_usd"]:
        data[kolom] = pd.to_numeric(data[kolom], errors="coerce")
    data = data.rename(columns={"gdp_constant_2015_usd": "bbp"})
    data = data.loc[data["year"].between(1960, 2024)].copy()
    return data, kaart, bronnen, controle


# 3 AFGELEIDE KOLOMMEN EN CLASSIFICATIE
def vergelijk_jaren(data, startjaar, eindjaar, uitstootkolom="co2"):
    begin = data.loc[data["year"] == startjaar,
                     ["iso_code", "country", "region", uitstootkolom, "bbp"]]
    einde = data.loc[data["year"] == eindjaar, ["iso_code", uitstootkolom, "bbp"]]
    samen = begin.merge(einde, on="iso_code", how="outer", suffixes=("_start", "_eind"),
                        validate="one_to_one")
    # Landen die alleen in het eindjaar voorkomen houden ook hun naam en regio.
    beschrijvingen = data[["iso_code", "country", "region"]].drop_duplicates("iso_code")
    samen = samen.drop(columns=["country", "region"]).merge(
        beschrijvingen, on="iso_code", validate="one_to_one")
    samen = samen.rename(columns={f"{uitstootkolom}_start": "co2_start",
                                  f"{uitstootkolom}_eind": "co2_eind"})
    geldig = (samen[["co2_start", "co2_eind", "bbp_start", "bbp_eind"]].notna().all(axis=1)
              & samen["co2_start"].gt(0) & samen["co2_eind"].ge(0)
              & samen["bbp_start"].gt(0) & samen["bbp_eind"].gt(0))
    uitgesloten = samen.loc[~geldig, ["iso_code", "country", "co2_start", "co2_eind", "bbp_start", "bbp_eind"]]
    samen = samen.loc[geldig].copy()
    samen["bbp_groei"] = (samen["bbp_eind"] / samen["bbp_start"] - 1) * 100
    samen["co2_groei"] = (samen["co2_eind"] / samen["co2_start"] - 1) * 100
    samen["intensiteit_start"] = samen["co2_start"] * 1_000_000_000 / samen["bbp_start"]
    samen["intensiteit_eind"] = samen["co2_eind"] * 1_000_000_000 / samen["bbp_eind"]
    samen["intensiteit_groei"] = (samen["intensiteit_eind"] / samen["intensiteit_start"] - 1) * 100
    samen["status"] = "Geen bbp-groei"
    groei = samen["bbp_groei"] > 0
    samen.loc[groei, "status"] = "Geen ontkoppeling"
    samen.loc[groei & (samen["intensiteit_groei"] < 0), "status"] = "Alleen relatief"
    samen.loc[groei & (samen["co2_groei"] < 0), "status"] = "Absoluut"
    return samen, uitgesloten


# 4 HERBRUIKBARE GRAFIEKOPMAAK
def toon_grafiek(fig):
    fig.update_layout(font=dict(family="Arial", color="#173044", size=13),
                      margin=dict(l=15, r=15, t=35, b=25), legend_title_text="",
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})


# 5 OPSTARTEN
st.markdown("""<style>
.stApp{background:#f5f7fa;color:#173044} [data-testid="stSidebar"]{background:#eaf0f4}
.block-container{max-width:1450px;padding-top:2.5rem}
h1,h2,h3{letter-spacing:-.025em} [data-testid="stMetric"]{background:white;border:1px solid #dce4e9;border-radius:12px;padding:16px}
</style>""", unsafe_allow_html=True)
try:
    data, kaart, bronnen, controle = laad_data()
except (FileNotFoundError, KeyError, ValueError) as fout:
    st.error(f"De lokale data kan niet worden ingelezen: {fout}")
    st.info("Controleer of data/bronnen.zip naast app.py staat. Herstel de meegeleverde bestanden.")
    st.stop()


# 6 FILTERS
with st.sidebar:
    st.title("CO₂ en welvaart")
    st.caption("CASUS 5 · RICHTING A")
    startjaar, eindjaar = st.slider("Vergelijkingsperiode", 1960, 2024, (2000, 2023))
    regio = st.selectbox("Regio", ["Alle regio's"] + sorted(data["region"].dropna().unique()))
    st.caption("De periode vergelijkt twee meetjaren. De tijdlijn laat zien wat ertussen gebeurt.")
    st.divider()
    st.markdown("[GitHub · code en data](https://github.com/Hugohilbelink/Minor_data_science_eindcase_week_4)")

if startjaar == eindjaar:
    st.warning("Kies twee verschillende jaren om verandering te berekenen.")
    st.stop()
regiodata = data if regio == "Alle regio's" else data.loc[data["region"] == regio]
vergelijking, uitgesloten = vergelijk_jaren(regiodata, startjaar, eindjaar)
with st.sidebar:
    landen = st.multiselect("Landen", sorted(vergelijking["country"].unique()),
                            help="Leeg betekent alle landen met complete begin- en eindwaarden binnen de regio.")
    alleen_groei = st.checkbox("Alleen landen met bbp-groei", value=False)

# Alle analyseonderdelen gebruiken dezelfde selectie.
selectie = vergelijking.copy()
if landen:
    selectie = selectie.loc[selectie["country"].isin(landen)]
if alleen_groei:
    selectie = selectie.loc[selectie["bbp_groei"] > 0]


# 7 HOOFDCONCLUSIE EN KPI S
st.caption(f"INDIVIDUELE EINDOPDRACHT · {startjaar}–{eindjaar} · {regio}")
st.title("Wie groeit met minder uitstoot?")
st.write("Een schonere economie kan toch méér CO₂ uitstoten. Vergelijk daarom de totale uitstoot én de uitstoot per eenheid bbp.")
if selectie.empty:
    st.warning("Geen landen met geldige begin- en eindwaarden binnen deze selectie. Pas de filters aan.")
    st.stop()
aantal = len(selectie)
absoluut = int((selectie["status"] == "Absoluut").sum())
relatief = int((selectie["status"] == "Alleen relatief").sum())
st.success(f"{absoluut} van de {aantal} geselecteerde landen combineren bbp-groei met minder totale CO₂. "
           f"Bij {relatief} landen daalt alleen de uitstoot per eenheid bbp terwijl de economie groeit.")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Landen vergeleken", aantal)
k2.metric("Absolute ontkoppeling", absoluut)
k3.metric("Alleen relatief", relatief)
k4.metric("Mediane CO₂-verandering", f"{selectie['co2_groei'].median():+.1f}%")
st.caption(f"{len(uitgesloten)} landen in de gekozen regio vallen buiten de vergelijking wegens ontbrekende of ongeldige eindpunten. "
           "Een geselecteerd land telt één keer; dit is geen percentage van de wereldwijde uitstoot.")

overzicht, verdieping, methode = st.tabs(["Wereldbeeld", "Land en onderbouwing", "Data en methode"])


# 8 KAART EN VERGELIJKING
with overzicht:
    st.subheader("Waar lukt absolute ontkoppeling?")
    st.write("Bekijk of landen met dezelfde ontwikkeling ruimtelijk bij elkaar liggen. Gebruik de regio- en periodefilters om het patroon te vergelijken.")
    # Een lokale GeoJSON en een lege achtergrond: de kaart vraagt geen externe tegels op.
    achtergrond = pd.DataFrame({"id": [f["id"] for f in kaart["features"]]})
    fig = px.choropleth_map(achtergrond, geojson=kaart, locations="id", color_discrete_sequence=["#e2e7eb"],
                            map_style="white-bg", center={"lat": 18, "lon": 5}, zoom=0.7)
    fig.update_traces(hoverinfo="skip", marker_line_width=0.3, marker_line_color="white", showlegend=False)
    kleurenkaart = px.choropleth_map(selectie, geojson=kaart, locations="iso_code", color="status",
                                     color_discrete_map=KLEUREN, hover_name="country",
                                     hover_data={"iso_code": False, "bbp_groei": ":.1f", "co2_groei": ":.1f", "intensiteit_groei": ":.1f"},
                                     labels={"bbp_groei": "Bbp %", "co2_groei": "CO₂ %", "intensiteit_groei": "CO₂ / bbp %"})
    for laag in kleurenkaart.data:
        fig.add_trace(laag)
    fig.update_layout(height=490, legend=dict(orientation="h", y=-0.05))
    toon_grafiek(fig)
    kaartcodes = {f["id"] for f in kaart["features"]}
    zonder_kaart = selectie.loc[~selectie["iso_code"].isin(kaartcodes), "country"].tolist()
    st.caption("Lichtgrijs = buiten selectie of geen geldige vergelijking. De grove wereldkaart bevat niet elk klein land of gebied; de tabel en statistiek wel. "
               f"{len(zonder_kaart)} geselecteerde landen hebben geen eigen kaartvlak.")
    if zonder_kaart:
        with st.expander("Welke landen ontbreken op de kaart?"):
            st.write(", ".join(zonder_kaart))

    st.subheader("Groei is nog geen daling van uitstoot")
    fig = px.scatter(selectie, x="bbp_groei", y="co2_groei", color="status", color_discrete_map=KLEUREN,
                      hover_name="country", hover_data={"intensiteit_groei": ":.1f"},
                      labels={"bbp_groei": "Verandering reëel bbp (%)", "co2_groei": "Verandering totale CO₂ (%)"})
    onder = min(0, selectie["bbp_groei"].min(), selectie["co2_groei"].min())
    boven = max(selectie["bbp_groei"].max(), selectie["co2_groei"].max(), 1)
    fig.add_shape(type="line", x0=onder, y0=onder, x1=boven, y1=boven,
                  line=dict(color="#8798a5", dash="dot"))
    fig.add_hline(y=0, line_color="#8798a5")
    fig.add_vline(x=0, line_color="#8798a5")
    toon_grafiek(fig)
    st.caption("Rechts onder nul: absolute ontkoppeling. Rechts boven nul maar onder de stippellijn y = x: alleen relatieve ontkoppeling. "
               "Links van nul groeit het bbp niet. Elk punt is één land; assen kunnen een verschillend schaalbereik hebben.")


# 9 LANDVERHAAL EN TIJDLIJN
with verdieping:
    st.subheader("Wat zit er achter het oordeel?")
    namen = sorted(selectie["country"].unique())
    land = st.selectbox("Bekijk een land", namen, index=namen.index("Netherlands") if "Netherlands" in namen else 0)
    rij = selectie.loc[selectie["country"] == land].iloc[0]
    st.write(f"**{land}: {rij['status'].lower()}.** Bbp {rij['bbp_groei']:+.1f}%, "
             f"totale CO₂ {rij['co2_groei']:+.1f}% en CO₂ per eenheid bbp {rij['intensiteit_groei']:+.1f}%.")
    tijdlijn = regiodata.loc[(regiodata["iso_code"] == rij["iso_code"]) &
                            regiodata["year"].between(startjaar, eindjaar)].copy()
    # Reindex maakt ontbrekende jaren zichtbaar als onderbreking in de lijn.
    tijdlijn = tijdlijn.set_index("year").reindex(range(startjaar, eindjaar + 1)).rename_axis("year").reset_index()
    tijdlijn["Bbp"] = tijdlijn["bbp"] / rij["bbp_start"] * 100
    tijdlijn["Totale CO₂"] = tijdlijn["co2"] / rij["co2_start"] * 100
    tijdlijn["CO₂ per eenheid bbp"] = (tijdlijn["co2"] * 1_000_000_000 / tijdlijn["bbp"]) / rij["intensiteit_start"] * 100
    lang = tijdlijn.melt(id_vars="year", value_vars=["Bbp", "Totale CO₂", "CO₂ per eenheid bbp"],
                         var_name="Maatstaf", value_name="Index")
    fig = px.line(lang, x="year", y="Index", color="Maatstaf", labels={"year": "Jaar"},
                   color_discrete_map={"Bbp": "#3566a3", "Totale CO₂": "#c44b48", "CO₂ per eenheid bbp": "#087f68"})
    fig.update_traces(connectgaps=False)
    fig.add_hline(y=100, line_dash="dot")
    toon_grafiek(fig)
    st.caption(f"Alle reeksen starten op 100 in {startjaar}. Een eindpuntdaling bewijst geen onafgebroken daling; de tussenliggende jaren blijven zichtbaar.")
    consumptie, _ = vergelijk_jaren(regiodata, startjaar, eindjaar, "consumption_co2")
    alternatief = consumptie.loc[consumptie["iso_code"] == rij["iso_code"]]
    if not alternatief.empty:
        ar = alternatief.iloc[0]
        st.info(f"Controle voor handel: de consumptiegebaseerde CO₂ verandert voor {land} met {ar['co2_groei']:+.1f}%. "
                f"Het oordeel wordt dan: {ar['status'].lower()}. Deze maat rekent uitstoot in geïmporteerde producten mee en die in exportproducten niet.")
    else:
        st.info("Voor dit land ontbreken geldige consumptiegebaseerde eindpunten. Verplaatsing van productie naar het buitenland is hier niet te controleren.")

    # 10 STATISTISCHE ONDERBOUWING
    st.subheader("Hoe sterk is het verband tussen groei en uitstoot?")
    st.write("Een eenvoudige regressie vergelijkt bbp-verandering met CO₂-verandering tussen landen in dezelfde selectie. "
             "Dit toetst samenhang; het verklaart niet waarom landen ontkoppelen.")
    if aantal >= 5 and selectie["bbp_groei"].nunique() > 1 and selectie["co2_groei"].nunique() > 1:
        model = linregress(selectie["bbp_groei"], selectie["co2_groei"])
        marge = t.ppf(0.975, df=aantal - 2) * model.stderr
        a, b, c = st.columns(3)
        a.metric("Landen in regressie", aantal)
        b.metric("R²", f"{model.rvalue ** 2:.2f}")
        c.metric("Helling", f"{model.slope:.2f}")
        st.write(f"10 procentpunt meer bbp-groei hangt samen met **{10 * model.slope:+.1f} procentpunt** CO₂-verandering. "
                 f"Het klassieke 95%-betrouwbaarheidsinterval loopt van {10 * (model.slope - marge):+.1f} tot {10 * (model.slope + marge):+.1f} procentpunt. "
                 f"De tweezijdige p-waarde voor een helling van nul is {model.pvalue:.3g}.")
        x = np.linspace(selectie["bbp_groei"].min(), selectie["bbp_groei"].max(), 100)
        fig = px.scatter(selectie, x="bbp_groei", y="co2_groei", hover_name="country", color="status",
                          color_discrete_map=KLEUREN, labels={"bbp_groei": "Verandering bbp (%)", "co2_groei": "Verandering CO₂ (%)"})
        fig.add_trace(go.Scatter(x=x, y=model.intercept + model.slope * x, mode="lines", name="Regressielijn", line=dict(color="#173044")))
        toon_grafiek(fig)
        st.caption("Elk land weegt even zwaar. Het interval veronderstelt onafhankelijke fouten met constante variantie; landen beïnvloeden elkaar en uitschieters kunnen de uitkomst sturen. "
                   "Dit is modelonzekerheid, geen meetonzekerheid van CO₂. Vergelijk regio's en andere periodes om de gevoeligheid te onderzoeken.")
    else:
        st.info("Voor regressie zijn minimaal vijf landen en variatie in beide grootheden nodig. Verruim de selectie.")

    st.subheader("Welke maat is het eerlijkst?")
    st.write("Voor de klimaatvraag is de verandering in totale CO₂ de hoofdmaat: een lagere intensiteit kan samengaan met meer uitstoot. "
             "CO₂ per eenheid reëel bbp laat wel zien of productie schoner wordt. Toon beide naast elkaar. "
             "Territoriale uitstoot mist emissies die via import worden uitbesteed; controleer daarom waar mogelijk ook consumptiegebaseerde uitstoot. "
             "Absolute ontkoppeling zegt op zichzelf niets over een eerlijke uitstootverdeling of een voldoende snelle daling.")


# 11 TABEL EN DATAVERANTWOORDING
with methode:
    st.subheader("De cijfers naast elkaar")
    top_aantal = 10
    tabel = selectie.sort_values("co2_groei").head(top_aantal)
    kolommen = ["country", "iso_code", "bbp_groei", "co2_groei", "intensiteit_groei", "status"]
    st.caption("Tien landen met de sterkste procentuele daling of kleinste stijging van totale CO₂ binnen je selectie.")
    st.dataframe(tabel[kolommen].rename(columns={"country": "Land", "iso_code": "ISO", "bbp_groei": "Bbp %",
                 "co2_groei": "CO₂ %", "intensiteit_groei": "CO₂ / bbp %", "status": "Oordeel"}),
                 hide_index=True, width="stretch")
    st.download_button("Download alle geselecteerde landen", selectie[kolommen].to_csv(index=False).encode("utf-8-sig"),
                       "ontkoppeling_selectie.csv", "text/csv")
    st.subheader("Bronnen en keuzes")
    st.markdown("- **Uitstoot:** [Our World in Data](https://github.com/owid/co2-data), jaarlijkse territoriale CO₂ uit fossiele brandstoffen en industrie; exclusief landgebruik. Eenheid: miljoen ton.\n"
                "- **Economie:** [Wereldbank NY.GDP.MKTP.KD](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD), totaal bbp in constante dollars van 2015.\n"
                "- **Kaart:** Natural Earth op schaal 1:110 miljoen, lokaal bewaard; grenzen zijn schematisch.\n"
                "- **Sleutel:** ISO-code plus jaar. Een landnaam kan verschillen; alleen een landcode koppelen zou alle jaren vermenigvuldigen.\n"
                "- **Ontbrekende waarden:** geen nul, gemiddelde of interpolatie. Alleen geldige, positieve startwaarden en bbp-eindwaarden; CO₂-eindwaarde mag nul zijn.\n"
                "- **Definitie:** bbp > 0% en CO₂ < 0% = absoluut; bbp > 0%, CO₂ ≥ 0% en intensiteit < 0% = alleen relatief. Zonder bbp-groei volgt een aparte categorie.")
    st.caption(f"Snapshot opgehaald op {bronnen['opgehaald_utc'][:10]}. Wereldbank laatst bijgewerkt: {bronnen['worldbank_metadata']['lastupdated']}. "
               "De vergelijking gebruikt 1960–2024; recentere of oudere bronjaren blijven in het bronarchief beschikbaar.")
    st.write("De tabel hieronder telt de koppeling van alle land-jaren vóór het analysefilter op 1960–2024. Een gekoppelde rij kan nog ontbrekende meetwaarden bevatten.")
    st.dataframe(controle, hide_index=True, width="stretch")
    with st.expander("Uitgesloten landen en ontbrekende eindpunten in deze regio"):
        st.dataframe(uitgesloten, hide_index=True, width="stretch")
    with st.expander("Toon de onderliggende land-jaren"):
        st.dataframe(regiodata.loc[regiodata["iso_code"].isin(selectie["iso_code"]) &
                                   regiodata["year"].between(startjaar, eindjaar)], hide_index=True, width="stretch")
    st.caption("De app leest uitsluitend lokale bestanden. Het ophaalscript en de data-verantwoording staan in de repository. Gebouwd met hulp van Codex; de gebruiker moet de code zelfstandig kunnen uitleggen en aanpassen.")
