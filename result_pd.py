import pandas as pd
from io import StringIO


def read_results(results_file):
    results = pd.read_csv(results_file)
    names = results.filter(["Nachname", "Vorname"])
    answers = (
        results.filter(regex="Antwort .*")
        .apply(lambda row: row.str.split(r"Teil \d+:[ ]?([^;]*)", expand=True), axis=1)
        .apply(lambda col: col.stack(dropna=True))
    )

    return (names, answers)


def test_read_results():
    results_file = StringIO(
        """
﻿Nachname,Vorname,Matrikelnummer,Institution,Abteilung,E-Mail-Adresse,Status,"Begonnen am",Beendet,"Verbrauchte Zeit",Bewertung/80.00,"Antwort 1","Antwort 2","Antwort 3","Antwort 4","Antwort 5","Antwort 6","Antwort 7","Antwort 8","Antwort 9","Antwort 10","Antwort 11","Antwort 12","Antwort 13","Antwort 14","Antwort 15","Antwort 16","Antwort 17","Antwort 18","Antwort 19","Antwort 20","Antwort 21","Antwort 22","Antwort 23","Antwort 24","Antwort 25","Antwort 26","Antwort 27","Antwort 28","Antwort 29","Antwort 30","Antwort 31","Antwort 32","Antwort 33","Antwort 34","Antwort 35","Antwort 36","Antwort 37","Antwort 38","Antwort 39","Antwort 40","Antwort 41","Antwort 42"
"Max",Mustermann,14933709,,,max@student.ethz.ch,Beendet,"29. Januar 2018  09:18","29. Januar 2018  11:35","2 Stunden 17 Minuten",23.37,"Teil 1: butan-2,4-enon; Teil 2: Z; Teil 3: Piperidin","Teil 1: Benzolring; Teil 2: Nitril; Teil 3: Acetylen","Teil 1: CC(=O)C1=CC(=CO1)CN; Teil 2: CN(C)C1CCC[C@H](O)C1","Teil 1: Ketone; Teil 2: Imine","{Dropzone 2 -> +}, {Dropzone 3 -> –}, {Dropzone 4 -> +}","Teil 1: [O-]C1=CC2=CC[NH+]=CC2C1; Teil 2: C[N-](C)=CC1=C[CH+]C=C1","Teil 1: a1; Teil 2: b4; Teil 3: b4; Teil 4: a1","Teil 1: identisch (nicht isomer); Teil 2: enantiomer; Teil 3: identisch (nicht isomer)","Teil 1: diastereotop; Teil 2: homotop; Teil 3: konstitutop","Teil 1: chiral; Teil 2: nicht chiral; Teil 3: chiral; Teil 4: nicht chiral","Teil 1: Konstitutionsisomere; Teil 2: keine Isomere","Teil 1: D; Teil 2: R; Teil 3: S; Teil 4: 4; Teil 5: 4","Teil 1: OC[C@@H](O)[C@@H](O)[C@H](O)C=O","Dropzone 1 -> {2. H} Dropzone 2 -> {1. OH} Dropzone 3 -> {1. OH} Dropzone 4 -> {2. H} Dropzone 5 -> {2. H} Dropzone 6 -> {1. OH}","Teil 1: 44; Teil 2: 12; Teil 3: 7; Teil 4: 5; Teil 5: 3","Teil 1: A1; Teil 2: C7; Teil 3: E4","-0,47 kcal/mol","p_K_Taut = p_K_aKeton × p_K_aEnol","Teil 1: Ethyl; Teil 2: 1,7; Teil 3: 55","Dropzone 1 -> {3. iPr} Dropzone 2 -> {2. CH3} Dropzone 3 -> {1. H}","Teil 1: ekliptisch; Teil 2: antiperiplanar; Teil 3: negativ; Teil 4: dem absoluten Energieminimum","Teil 1: 2","Dropzone 1 -> {5. F} Dropzone 2 -> {3. OH} Dropzone 3 -> {4. H} Dropzone 4 -> {2. Ph} Dropzone 5 -> {4. H} Dropzone 6 -> {4. H} Dropzone 7 -> {1. Et} Dropzone 8 -> {4. H} Dropzone 9 -> {10. energiereicherer Sessel} Dropzone 10 -> {9. energieärmerer Sessel}","{Dropzone 1 -> H/D}",-,"Teil 1: 5; Teil 2: 6","Teil 1: A; Teil 2: B","Teil 1: CC1=CCC(=O)C=C1","Teil 1: CCC(C)=O; Teil 2: CC(O)C(C(CC(=O)CO)CC(=O)CO)C(=O)CO","Teil 1: SOCl₂; Teil 2: ClC(=O)CCC1CN(C(=O)c2cccc(Cl)c2)c3cccc(Cl)c13","Teil 1: O=C1CCC(=O)[C@H]2O[C@@H]12; Teil 2: racemisches Gemisch","Teil 1: O=C1CCC(=O)[C@H]2O[C@@H]12; Teil 2: reines Enantiomer","Teil 1: OCC(=O)C1=CC=C(O1)C(=O)CO; Teil 2: SOCl₂; Teil 3: C1C[C@H]2O[C@@H]1c3ccccc23","Teil 1: CC(C)C1CCC(C)C12CCC2O","Teil 1: CC(C)C1CCC(C)C12CC3(CCC(=O)C3=O)C2=O","Teil 1: Cc1cc(COCN2CCCCC2)ccc1O","Teil 1: Cc1cccnc1","Teil 1: B; Teil 2: C; Teil 3: b+d; Teil 4: e; Teil 5: f","Teil 1: dipolar protisch; Teil 2: dipolar protisch; Teil 3: unpolar; Teil 4: dipolar aprotisch","{Dropzone 1 -> Nu}, {Dropzone 2 -> Nu}","Teil 1: 1-Chlorheptan; Teil 2: Ethanol; Teil 3: 2-Brombutan","Nukleophile tragen eine negative elektrische Ladung.; Gute Nukleophile sind schlechte Abgangsgruppen."
    """.strip()
    )

    names, answers = read_results(results_file)
    assert names.equals(pd.DataFrame([["Max", "Mustermann"]], columns=["Nachname", "Vorname"]))
    assert answers["Antwort 2"].values.tolist() == ["Nitril"]
