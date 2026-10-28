"""Start met python data_ophalen.py; voeg --vernieuw toe voor nieuwe bronversies."""
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import hashlib
import json

import pandas as pd
import requests

MAP = Path(__file__).parent / "data"
URLS = {
    "owid-co2-data.csv": "https://owid-public.owid.io/data/co2/owid-co2-data.csv",
    "owid-co2-codebook.csv": "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv",
    "bbp_api": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.KD?format=json&per_page=20000",
    "landen_api": "https://api.worldbank.org/v2/country?format=json&per_page=1000",
    "kaart": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson",
}


def ophalen(url):
    antwoord = requests.get(url, timeout=120)
    antwoord.raise_for_status()
    return antwoord


def alle_paginas(url):
    eerste = ophalen(url).json()
    rijen = list(eerste[1])
    for pagina in range(2, eerste[0]["pages"] + 1):
        rijen.extend(ophalen(f"{url}&page={pagina}").json()[1])
    return eerste[0], rijen


def maak_bbp(records):
    return pd.DataFrame([
        {"iso_code": r["countryiso3code"], "country": r["country"]["value"],
         "year": int(r["date"]), "gdp_constant_2015_usd": r["value"]}
        for r in records
    ])


def maak_landen(records):
    return pd.DataFrame([
        {"iso_code": r["id"], "country": r["name"], "region": r["region"]["value"],
         "is_aggregate": r["region"]["id"] == "NA"}
        for r in records
    ])


def maak_kaart(geojson):
    """Bewaar alleen de kaartgeometrie en labels; geen economische kaartattributen."""
    features = []
    for f in geojson["features"]:
        code = f["properties"]["ISO_A3_EH"]
        if code == "-99":
            code = f["properties"]["ADM0_A3"]
        if code == "ATA":
            continue  # Antarctica heeft geen landenvergelijking.
        features.append({"type": "Feature", "id": code,
                         "properties": {"naam": f["properties"]["NAME_NL"]}, "geometry": f["geometry"]})
    return {"type": "FeatureCollection", "features": features}


def bewaar(bestanden, metadata):
    MAP.mkdir(exist_ok=True)
    metadata["sha256"] = {naam: hashlib.sha256(inhoud).hexdigest() for naam, inhoud in bestanden.items()}
    bestanden["data_bronnen_case5.json"] = json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8")
    # Eerst een nieuw archief schrijven; de bestaande snapshot blijft staan bij een fout.
    tijdelijk = MAP / "bronnen_nieuw.zip"
    with ZipFile(tijdelijk, "w", ZIP_DEFLATED) as archief:
        for naam, inhoud in bestanden.items():
            archief.writestr(naam, inhoud)
    with ZipFile(tijdelijk) as archief:
        assert archief.testzip() is None
    tijdelijk.replace(MAP / "bronnen.zip")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vernieuw", action="store_true")
    args = parser.parse_args()
    if (MAP / "bronnen.zip").exists() and not args.vernieuw:
        print("De vaste snapshot bestaat al. Gebruik --vernieuw alleen als je bewust nieuwe data wilt.")
        return
    bestanden = {naam: ophalen(URLS[naam]).content for naam in ["owid-co2-data.csv", "owid-co2-codebook.csv"]}
    metadata, bbp = alle_paginas(URLS["bbp_api"])
    _, landen = alle_paginas(URLS["landen_api"])
    bestanden["worldbank_gdp_raw.json"] = json.dumps({"metadata": metadata, "data": bbp}, ensure_ascii=False).encode("utf-8")
    bestanden["worldbank_countries_raw.json"] = json.dumps(landen, ensure_ascii=False).encode("utf-8")
    bestanden["worldbank_gdp_constant_2015_usd.csv"] = maak_bbp(bbp).to_csv(index=False).encode("utf-8")
    bestanden["worldbank_country_metadata.csv"] = maak_landen(landen).to_csv(index=False).encode("utf-8")
    bestanden["landen.geojson"] = json.dumps(maak_kaart(ophalen(URLS["kaart"]).json()), ensure_ascii=False).encode("utf-8")
    bewaar(bestanden, {"opgehaald_utc": datetime.now(timezone.utc).isoformat(),
                       "worldbank_metadata": metadata, "bronnen": URLS})
    co2 = pd.read_csv(BytesIO(bestanden["owid-co2-data.csv"]))
    print(f"Snapshot opgeslagen: {len(co2)} CO2-rijen en {len(bbp)} bbp-rijen.")


if __name__ == "__main__":
    main()
