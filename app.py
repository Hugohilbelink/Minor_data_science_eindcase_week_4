"""Casus 5A. Start: streamlit run app.py. Zoek op de genummerde blokken."""
from pathlib import Path
import json
from zipfile import ZipFile

import pandas as pd
import plotly.express as px
from scipy.stats import linregress, t
import streamlit as st
import teksten

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
    # Gebruik alleen landcodes uit de landenlijst; geen lege codes of regionale totalen.
    landen = landen[landen["is_aggregate"] == False]
    co2 = co2[co2["iso_code"].isin(landen["iso_code"])]
    bbp = bbp[bbp["iso_code"].isin(landen["iso_code"])]
    data = co2.merge(bbp[["iso_code", "year", "gdp_constant_2015_usd"]],
                     on=["iso_code", "year"], how="outer", indicator=True,
                     validate="one_to_one")
    controle = data["_merge"].value_counts().rename_axis("Koppeling").reset_index(name="Rijen")
    # Voeg namen en regio's toe. Alleen een ontbrekende naam wordt aangevuld.
    landen = landen.rename(columns={"country": "landnaam"})
    data = data.merge(landen[["iso_code", "landnaam", "region"]], on="iso_code", validate="many_to_one")
    data["country"] = data["country"].fillna(data["landnaam"])
    data = data.drop(columns="landnaam")
    for kolom in ["co2", "consumption_co2", "gdp_constant_2015_usd"]:
        data[kolom] = pd.to_numeric(data[kolom], errors="coerce")
    data = data.rename(columns={"gdp_constant_2015_usd": "bbp"})
    data = data.loc[data["year"].between(1960, 2024)].copy()
    return data, kaart, bronnen, controle


# 3 AFGELEIDE KOLOMMEN EN CLASSIFICATIE
def vergelijk_jaren(data, startjaar, eindjaar, uitstootkolom="co2"):
    kolommen = ["iso_code", uitstootkolom, "bbp"]
    begin = data[data["year"] == startjaar][kolommen]
    einde = data[data["year"] == eindjaar][kolommen]
    samen = begin.merge(einde, on="iso_code", how="outer", suffixes=("_start", "_eind"),
                        validate="one_to_one")
    # Voeg beschrijvingen toe, ook bij landen met maar één meetjaar.
    beschrijvingen = data[["iso_code", "country", "region"]].drop_duplicates("iso_code")
    samen = samen.merge(beschrijvingen, on="iso_code", validate="one_to_one")
    samen = samen.rename(columns={f"{uitstootkolom}_start": "co2_start",
                                  f"{uitstootkolom}_eind": "co2_eind"})
    metingen = ["co2_start", "co2_eind", "bbp_start", "bbp_eind"]
    geldig = samen.dropna(subset=metingen)
    geldig = geldig[(geldig["co2_start"] > 0) & (geldig["co2_eind"] >= 0)
                    & (geldig["bbp_start"] > 0) & (geldig["bbp_eind"] > 0)]
    uitgesloten = samen[~samen["iso_code"].isin(geldig["iso_code"])][["iso_code", "country"] + metingen]
    samen = geldig.copy()
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


def puntenwolk(data, y_kolom="co2_groei"):
    return px.scatter(data, x="bbp_groei", y=y_kolom, color="status",
                      color_discrete_map=KLEUREN, hover_name="country",
                      hover_data={"intensiteit_groei": ":.1f"}, labels=teksten.ASSEN)


# 5 OPSTARTEN
st.markdown(teksten.OPMAAK, unsafe_allow_html=True)
try:
    data, kaart, bronnen, controle = laad_data()
except (FileNotFoundError, KeyError, ValueError) as fout:
    st.error(f"De lokale data kan niet worden ingelezen: {fout}")
    st.info(teksten.INLEES_HULP)
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
st.write(teksten.INLEIDING)
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
    st.write(teksten.KAART_UITLEG)
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
    fig = puntenwolk(selectie)
    onder = min(0, selectie["bbp_groei"].min(), selectie["co2_groei"].min())
    boven = max(selectie["bbp_groei"].max(), selectie["co2_groei"].max(), 1)
    fig.add_shape(type="line", x0=onder, y0=onder, x1=boven, y1=boven,
                  line=dict(color="#8798a5", dash="dot"))
    fig.add_hline(y=0, line_color="#8798a5")
    fig.add_vline(x=0, line_color="#8798a5")
    toon_grafiek(fig)
    st.caption(teksten.PUNTEN_UITLEG)


# 9 LANDVERHAAL EN TIJDLIJN
with verdieping:
    st.subheader("Wat zit er achter het oordeel?")
    namen = sorted(selectie["country"].unique())
    land = st.selectbox("Bekijk een land", namen, index=namen.index("Netherlands") if "Netherlands" in namen else 0)
    rij = selectie.loc[selectie["country"] == land].iloc[0]
    st.write(f"**{land}: {rij['status'].lower()}.** Bbp {rij['bbp_groei']:+.1f}%, "
             f"totale CO₂ {rij['co2_groei']:+.1f}% en CO₂ per eenheid bbp {rij['intensiteit_groei']:+.1f}%.")
    # Een volledige jaartabel houdt ontbrekende jaren zichtbaar als gaten in de lijnen.
    jaren = pd.DataFrame({"year": range(startjaar, eindjaar + 1)})
    landdata = regiodata[regiodata["iso_code"] == rij["iso_code"]]
    tijdlijn = jaren.merge(landdata, on="year", how="left", validate="one_to_one")
    tijdlijn["Bbp"] = tijdlijn["bbp"] / rij["bbp_start"] * 100
    tijdlijn["Totale CO₂"] = tijdlijn["co2"] / rij["co2_start"] * 100
    tijdlijn["CO₂ per eenheid bbp"] = (tijdlijn["co2"] * 1_000_000_000 / tijdlijn["bbp"]) / rij["intensiteit_start"] * 100
    fig = px.line(tijdlijn, x="year", y=["Bbp", "Totale CO₂", "CO₂ per eenheid bbp"],
                   labels={"year": "Jaar", "value": "Index", "variable": "Maatstaf"},
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
        st.info(teksten.HANDEL_ONTBREEKT)

    # 10 STATISTISCHE ONDERBOUWING
    st.subheader("Hoe sterk is het verband tussen groei en uitstoot?")
    st.write(teksten.REGRESSIE_UITLEG)
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
        x = [selectie["bbp_groei"].min(), selectie["bbp_groei"].max()]
        y = [model.intercept + model.slope * waarde for waarde in x]
        fig = puntenwolk(selectie)
        fig.add_scatter(x=x, y=y, mode="lines", name="Regressielijn", line=dict(color="#173044"))
        toon_grafiek(fig)
        st.caption(teksten.REGRESSIE_BEPERKING)
    else:
        st.info(teksten.REGRESSIE_TE_WEINIG)

    st.subheader("Welke maat is het eerlijkst?")
    st.write(teksten.OORDEEL)


# 11 TABEL EN DATAVERANTWOORDING
with methode:
    st.subheader("De cijfers naast elkaar")
    top_aantal = 10
    tabel = selectie.sort_values("co2_groei").head(top_aantal)
    kolommen = ["country", "iso_code", "bbp_groei", "co2_groei", "intensiteit_groei", "status"]
    st.caption(teksten.TABEL_UITLEG)
    st.dataframe(tabel[kolommen].rename(columns={"country": "Land", "iso_code": "ISO", "bbp_groei": "Bbp %",
                 "co2_groei": "CO₂ %", "intensiteit_groei": "CO₂ / bbp %", "status": "Oordeel"}),
                 hide_index=True, width="stretch")
    st.download_button("Download alle geselecteerde landen", selectie[kolommen].to_csv(index=False).encode("utf-8-sig"),
                       "ontkoppeling_selectie.csv", "text/csv")
    st.subheader("Bronnen en keuzes")
    st.markdown(teksten.BRONNEN)
    st.caption(f"Snapshot opgehaald op {bronnen['opgehaald_utc'][:10]}. Wereldbank laatst bijgewerkt: {bronnen['worldbank_metadata']['lastupdated']}. "
               "De vergelijking gebruikt 1960–2024; recentere of oudere bronjaren blijven in het bronarchief beschikbaar.")
    st.write(teksten.KOPPELING_UITLEG)
    st.dataframe(controle, hide_index=True, width="stretch")
    with st.expander("Uitgesloten landen en ontbrekende eindpunten in deze regio"):
        st.dataframe(uitgesloten, hide_index=True, width="stretch")
    with st.expander("Toon de onderliggende land-jaren"):
        st.dataframe(regiodata.loc[regiodata["iso_code"].isin(selectie["iso_code"]) &
                                   regiodata["year"].between(startjaar, eindjaar)], hide_index=True, width="stretch")
    st.caption(teksten.SLOT)
