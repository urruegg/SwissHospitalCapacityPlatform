# -*- coding: utf-8 -*-
"""
Curavias Skills Ontology — OneLake master-data generator.
Deterministic (seeded) synthetic data covering the three Curavias showcase tenants.
Employee NAMES are synthetic/anonymized; organisation structure & everything else is realistic.
Outputs UTF-8 CSVs into this script's own directory.
"""
import csv, os, random
from datetime import date, timedelta

random.seed(42)
REF = date(2026, 7, 19)
OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

def write_csv(name, header, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")

def gln_check(twelve):
    tot = 0
    for i, ch in enumerate(reversed(twelve)):
        tot += int(ch) * (3 if i % 2 == 0 else 1)
    return str((10 - (tot % 10)) % 10)

def person_gln(tcode, n):
    base = f"7601{tcode}9{n:06d}"      # 7601 + tenant(1) + '9' marker + 6-digit counter = 12
    return base + gln_check(base)

def d(dt):
    return dt.isoformat() if dt else ""

ASSUR_RANK = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}

# ---------------------------------------------------------------------------
# 1. dim_tenant
# ---------------------------------------------------------------------------
tenants = [
    # tenant_id, subdomain, name, archetype, canton, beds, fte, legal_form, grounded_on
    ("CN", "curanova.curavias.ch", "Uniklinik CuraNova", "Universitäres Zentrumsspital", "HN", "~900", "8600",
     "Öffentlich-rechtliche Anstalt (kantonal)", "USZ (Universitätsspital Zürich)"),
    ("CP", "curalp.curavias.ch", "Kantonsspital Curalp", "Kantonale Multi-Site-Spitalgruppe", "CA", "~840", "8600",
     "Holding-AG (100% kantonseigen)", "LUKS Gruppe (Luzerner Kantonsspital)"),
    ("VT", "vialta.curavias.ch", "Spital Vialta", "Regionales Grundversorgungsspital (privat)", "HN", "174", "1200",
     "Stiftung mit angeschlossenen Betrieben", "Spital Zollikerberg (Diakoniewerk Neumünster)"),
]
write_csv("dim_tenant.csv",
          ["tenant_id","tenant_subdomain","tenant_name","archetype","primary_canton","beds_approx","fte_approx","legal_form","grounded_on"],
          tenants)
TCODE = {"CN": "1", "CP": "2", "VT": "3"}

# ---------------------------------------------------------------------------
# 2. dim_org_unit  (the 48 entities from Demo-Hospitals-Master-Data, typed + level)
#    (entity_id, subdomain, entity_type, name, parent_id, role, beds, fte, location, canton, gln, grounded_on)
# ---------------------------------------------------------------------------
ORG = [
 ("CN","curanova.curavias.ch","Hospital-Org","Uniklinik CuraNova","","Öffentlich-rechtliche Anstalt, eigene Rechtspersönlichkeit","~900","8600","Stadt Helvetia-Nord","HN","7601001000010","USZ (Gesamthaus)"),
 ("CN-LE1","curanova.curavias.ch","Legal-Entity","Uniklinik CuraNova (Anstalt öR)","CN","Kantonale Anstalt, Träger des Leistungsauftrags","","","Stadt Helvetia-Nord","HN","7601001000027","USZ Rechtsträger"),
 ("CN-LE2","curanova.curavias.ch","Legal-Entity","CuraNova Forschung & Lehre AG","CN","Tochter-AG (Aus-, Weiter- & Fortbildung, Studien)","","240","Campus Helvetia-Nord","HN","7601001000034","USZ Uni/ETH-Kopplung"),
 ("CN-GOV1","curanova.curavias.ch","Governance-Body","Spitalrat CuraNova","CN","Oberstes strategisches Organ (9 externe Mitglieder)","","","Stadt Helvetia-Nord","HN","7601001000041","USZ Spitalrat"),
 ("CN-GOV2","curanova.curavias.ch","Governance-Body","Spitaldirektion CuraNova","CN","Operatives Führungsgremium","","","Stadt Helvetia-Nord","HN","7601001000058","USZ Spitaldirektion"),
 ("CN-S1","curanova.curavias.ch","Site","Campus Zentrum CuraNova","CN","Hauptstandort (Akut, Notfall, 6 Intensivstationen)","780","","Stadt Helvetia-Nord","HN","7601001000065","USZ Hauptareal"),
 ("CN-S2","curanova.curavias.ch","Site","CuraNova Aussenstandort Flughafen","CN","Ambulantes Zentrum / Aussenstandort","120","","Helvetia-Nord Flughafen","HN","7601001000072","USZ Standorte"),
 ("CN-D1","curanova.curavias.ch","Department","Herz- & Gefässzentrum","CN-S1","Medizinbereich (Herzchirurgie, Kardiologie, Angiologie)","120","620","Campus Zentrum","HN","7601001000089","USZ Herz-Gefäss"),
 ("CN-D2","curanova.curavias.ch","Department","Neuro- & Kopfzentrum","CN-S1","Medizinbereich (Neurochirurgie, Neurologie, HNO)","110","560","Campus Zentrum","HN","7601001000096","USZ Neuro-Kopf"),
 ("CN-D3","curanova.curavias.ch","Department","Innere Medizin & Onkologie","CN-S1","Medizinbereich (Innere, Onkologie, Infektiologie)","180","940","Campus Zentrum","HN","7601001000102","USZ Innere/Onko"),
 ("CN-D4","curanova.curavias.ch","Department","Trauma & Bewegungsapparat","CN-S1","Medizinbereich (Traumatologie, Orthopädie, Rheuma)","130","610","Campus Zentrum","HN","7601001000119","USZ Trauma"),
 ("CN-D5","curanova.curavias.ch","Department","Frauen- & Kinderzentrum","CN-S1","Medizinbereich (Geburtshilfe, Gynäkologie, Neonatologie)","95","520","Campus Zentrum","HN","7601001000126","USZ Frauen-Kind"),
 ("CN-D6","curanova.curavias.ch","Department","Diagnostik, Radiologie & Labor","CN-S1","Medizinbereich (Radiologie, Nuklearmedizin, Pathologie)","20","480","Campus Zentrum","HN","7601001000133","USZ Diagnostik"),
 ("CN-D7","curanova.curavias.ch","Department","Intensiv- & Notfallmedizin","CN-S1","Medizinbereich (6 IPS, Notfallzentrum, Brandverletzte)","90","720","Campus Zentrum","HN","7601001000140","USZ Intensiv/Notfall"),
 ("CN-D8","curanova.curavias.ch","Department","Zentrum für Klinische Forschung","CN-LE2","Forschungsbereich (Clinical Trials Center)","","260","Campus Helvetia-Nord","HN","7601001000157","USZ ZKF"),
 ("CP","curalp.curavias.ch","Hospital-Group","Curalp Gruppe AG","","Holding-AG, 100% kantonseigen","~840","8600","Curalp-Stadt","CA","7601002000013","LUKS Gruppe AG"),
 ("CP-LE1","curalp.curavias.ch","Legal-Entity","Kantonsspital Curalp AG","CP","Rechtsträgerin (100% Kanton Curalp)","","","Curalp-Stadt","CA","7601002000020","Luzerner Kantonsspital AG"),
 ("CP-LE2","curalp.curavias.ch","Legal-Entity","Spital Talkirchen AG","CP","Tochter-AG (Kanton Talkirchen 40%)","","","Talkirchen","TK","7601002000037","Spital Nidwalden AG"),
 ("CP-LE3","curalp.curavias.ch","Legal-Entity","Augenzentrum Curalp AG","CP","Tochter-AG (spezialärztlicher Betrieb)","","90","Curalp-Stadt","CA","7601002000044","LUKS Augenärzte Zentralschweiz AG"),
 ("CP-GOV1","curalp.curavias.ch","Governance-Body","Verwaltungsrat Curalp Gruppe","CP","Strategisches Organ (VR)","","","Curalp-Stadt","CA","7601002000051","LUKS Verwaltungsrat"),
 ("CP-S1","curalp.curavias.ch","Site","Curalp Stadt (Zentrumsspital)","CP-LE1","Zentrums-/Tertiärversorgung, Lehre & Forschung","560","","Curalp-Stadt","CA","7601002000068","LUKS Luzern"),
 ("CP-S2","curalp.curavias.ch","Site","Curalp Seetal","CP-LE1","Grundversorgungsspital","130","","Seetal","CA","7601002000075","LUKS Sursee"),
 ("CP-S3","curalp.curavias.ch","Site","Curalp Bergland","CP-LE1","Grundversorgungsspital","90","","Bergland","CA","7601002000082","LUKS Wolhusen"),
 ("CP-S4","curalp.curavias.ch","Site","Spital Talkirchen","CP-LE2","Grundversorgung (Tochtergesellschaft)","60","","Talkirchen","TK","7601002000099","Spital Nidwalden / Stans"),
 ("CP-S5","curalp.curavias.ch","Site","Höhenklinik Curalp-Bergsee","CP-LE1","Rehabilitation / Höhenklinik","60","","Bergsee","VS","7601002000105","Höhenklinik Montana"),
 ("CP-D1","curalp.curavias.ch","Department","Herzzentrum Curalp","CP-S1","Klinik (Kardiologie, Herzchirurgie)","90","480","Curalp Stadt","CA","7601002000112","LUKS Herzzentrum"),
 ("CP-D2","curalp.curavias.ch","Department","Neurozentrum Curalp","CP-S1","Klinik (Neurologie, Neurochirurgie)","70","360","Curalp Stadt","CA","7601002000129","LUKS Neurozentrum"),
 ("CP-D3","curalp.curavias.ch","Department","Tumorzentrum Curalp","CP-S1","Zentrum (Onkologie, Radio-Onkologie)","80","420","Curalp Stadt","CA","7601002000136","LUKS Tumorzentrum"),
 ("CP-D4","curalp.curavias.ch","Department","Frauenklinik & Geburtshilfe","CP-S1","Klinik (Gynäkologie, Geburtshilfe, Perinatalzentrum)","85","440","Curalp Stadt","CA","7601002000143","LUKS Frauenklinik"),
 ("CP-D5","curalp.curavias.ch","Department","Kinderspital Curalp","CP-S1","Klinik (Pädiatrie, Neonatologie)","75","400","Curalp Stadt","CA","7601002000150","LUKS Kinderspital"),
 ("CP-D6","curalp.curavias.ch","Department","Notfallzentrum & Rettungsdienst 144","CP-S1","Interdisziplinäres Notfallzentrum, Rettung","40","520","Curalp Stadt","CA","7601002000167","LUKS Notfall/144"),
 ("CP-D7","curalp.curavias.ch","Department","Orthopädie & Unfallchirurgie","CP-S2","Klinik (Ortho, Traumatologie, Wirbelsäule)","80","360","Seetal","CA","7601002000174","LUKS Ortho/Unfall"),
 ("CP-D8","curalp.curavias.ch","Department","Radiologie & Nuklearmedizin","CP-S1","Institut (Bildgebung, PET-CT, SPECT-CT)","","300","Curalp Stadt","CA","7601002000181","LUKS Radiologie"),
 ("VT","vialta.curavias.ch","Hospital-Org","Spital Vialta","","Privates Akutspital mit öffentlichem Leistungsauftrag","174","1200","Vialtaberg","HN","7601003000016","Spital Zollikerberg"),
 ("VT-LE1","vialta.curavias.ch","Legal-Entity","Stiftung Diakoniewerk Vialtaberg","VT","Stiftung (Trägerschaft, gemeinnützig)","","","Vialtaberg","HN","7601003000023","Stiftung Diakoniewerk Neumünster"),
 ("VT-LE2","vialta.curavias.ch","Legal-Entity","Residenz Vialta Park","VT-LE1","Betrieb (Alterswohnen / Langzeitpflege)","","180","Vialtaberg","HN","7601003000030","Residenz Neumünster Park"),
 ("VT-LE3","vialta.curavias.ch","Legal-Entity","Alterszentrum Seehalden","VT-LE1","Betrieb (Langzeitpflege)","","110","Seehalden","HN","7601003000047","Alterszentrum Hottingen"),
 ("VT-LE4","vialta.curavias.ch","Legal-Entity","Vialta Fachzentren- & Praxen AG","VT-LE1","Betrieb (Belegarzt-Praxen, Fachzentren)","","140","Vialtaberg","HN","7601003000054","Fachzentren- und Praxen AG"),
 ("VT-LE5","vialta.curavias.ch","Legal-Entity","Institut Vialta","VT-LE1","Betrieb (Aus- & Weiterbildung Pflege)","","40","Vialtaberg","HN","7601003000061","Institut Neumünster"),
 ("VT-S1","vialta.curavias.ch","Site","Spital Vialta (Hauptareal)","VT","Akutspital-Areal (Zentrum-, West-, Ost-, Nordbau)","174","","Vialtaberg","HN","7601003000078","Zollikerberg Areal"),
 ("VT-D1","vialta.curavias.ch","Department","Innere Medizin","VT-S1","Klinik (inkl. Palliativstation)","60","260","Vialtaberg","HN","7601003000085","Zollikerberg Innere"),
 ("VT-D2","vialta.curavias.ch","Department","Gynäkologie & Geburtshilfe mit Neonatologie","VT-S1","Klinik (>2'000 Geburten/Jahr, Geburtshaus)","34","220","Vialtaberg","HN","7601003000092","Zollikerberg Gyn/Geburt"),
 ("VT-D3","vialta.curavias.ch","Department","Allgemeine Chirurgie","VT-S1","Klinik (Viszeral-, plastische Chirurgie)","30","180","Vialtaberg","HN","7601003000108","Zollikerberg Chirurgie"),
 ("VT-D4","vialta.curavias.ch","Department","Orthopädie & Wirbelsäulenchirurgie","VT-S1","Klinik (spezialisierte Wirbelsäulenchirurgie)","26","150","Vialtaberg","HN","7601003000115","Zollikerberg Ortho/Spine"),
 ("VT-D5","vialta.curavias.ch","Department","Interdisziplinäres Notfallzentrum","VT-S1","Notfall 24/7, 365 Tage, Kinder-Permanence","12","160","Vialtaberg","HN","7601003000122","Zollikerberg Notfall"),
 ("VT-D6","vialta.curavias.ch","Department","Intensivstation","VT-S1","IPS","12","110","Vialtaberg","HN","7601003000139","Zollikerberg IPS"),
 ("VT-D7","vialta.curavias.ch","Department","Nephrologie & Dialysezentrum","VT-S1","Klinik + Dialyse (23 Plätze, grösstes im Kanton)","","90","Vialtaberg","HN","7601003000146","Zollikerberg Dialyse"),
 ("VT-D8","vialta.curavias.ch","Department","Radiologie & BrustCentrum","VT-S1","Institut (Radiologie) + zertifiziertes BrustCentrum","","80","Vialtaberg","HN","7601003000153","Zollikerberg Radiologie/Brust"),
]
sub2tenant = {"curanova.curavias.ch":"CN","curalp.curavias.ch":"CP","vialta.curavias.ch":"VT"}
org_by_id = {r[0]: r for r in ORG}
def org_level(eid):
    lvl, cur = 0, eid
    while org_by_id[cur][4]:
        cur = org_by_id[cur][4]; lvl += 1
    return lvl
org_rows = []
for r in ORG:
    eid, sub, etype, name, parent, role, beds, fte, loc, canton, gln, grounded = r
    org_rows.append([eid, sub2tenant[sub], etype, name, parent, org_level(eid), role, beds, fte, loc, canton, gln, grounded, "TRUE"])
write_csv("dim_org_unit.csv",
          ["org_unit_id","tenant_id","entity_type","org_unit_name","parent_org_unit_id","org_level","legal_form_or_role","beds","fte_approx","location","canton","gln","grounded_on","is_active"],
          org_rows)

DEPARTMENTS = [r for r in ORG if r[2] == "Department"]

# ---------------------------------------------------------------------------
# 3. dim_department  (Department rows as first-class org concept)
# ---------------------------------------------------------------------------
def medical_area(name, role):
    n = (name + " " + role).lower()
    if "intensiv" in n or "ips" in n: return "Intensiv- & Notfallmedizin"
    if "notfall" in n or "rettung" in n: return "Notfallmedizin"
    if "herz" in n: return "Kardiologie & Herzchirurgie"
    if "neuro" in n: return "Neurologie & Neurochirurgie"
    if "onko" in n or "tumor" in n: return "Onkologie"
    if "innere" in n: return "Innere Medizin"
    if "trauma" in n or "orthop" in n or "unfall" in n or "chirurgie" in n: return "Chirurgie & Bewegungsapparat"
    if "frauen" in n or "gyn" in n or "geburt" in n or "kinder" in n: return "Frauen- & Kindermedizin"
    if "radiolog" in n or "diagnost" in n or "nuklear" in n or "brust" in n: return "Radiologie & Diagnostik"
    if "nephro" in n or "dialyse" in n: return "Nephrologie"
    if "forschung" in n: return "Klinische Forschung"
    return "Allgemein"
dep_rows = []
for r in DEPARTMENTS:
    eid, sub, etype, name, parent, role, beds, fte, loc, canton, gln, grounded = r
    dep_rows.append([eid, sub2tenant[sub], parent, name, medical_area(name, role),
                     beds or "", fte or "", "CC-"+eid, canton, gln, grounded])
write_csv("dim_department.csv",
          ["department_id","tenant_id","site_id","department_name","medical_area","beds","planned_fte","cost_centre","canton","gln","grounded_on"],
          dep_rows)

# ---------------------------------------------------------------------------
# 4. dim_specialisation
# ---------------------------------------------------------------------------
SPEC = [
 ("SPEC-ANAES","Anästhesiologie","Anaesthesiology","medical_specialty","SIWF","siwf:facharzt/anaesthesiologie","SK-FMH-ANAES"),
 ("SPEC-INTENS","Intensivmedizin","Intensive care medicine","medical_specialty","SIWF","siwf:schwerpunkt/intensivmedizin","SK-FMH-INTENS"),
 ("SPEC-NOTF-MED","Klinische Notfallmedizin","Clinical emergency medicine","medical_specialty","SGNOR/SIWF","siwf:schwerpunkt/notfallmedizin","SK-FMH-NOTF"),
 ("SPEC-CARD","Kardiologie","Cardiology","medical_specialty","SIWF","siwf:facharzt/kardiologie","SK-FMH-CARD"),
 ("SPEC-CARDSURG","Herz- & Gefässchirurgie","Cardiac & vascular surgery","medical_specialty","SIWF","siwf:facharzt/herzchirurgie","SK-FMH-CARDSURG"),
 ("SPEC-NEURO","Neurologie","Neurology","medical_specialty","SIWF","siwf:facharzt/neurologie","SK-FMH-NEURO"),
 ("SPEC-NEUROSURG","Neurochirurgie","Neurosurgery","medical_specialty","SIWF","siwf:facharzt/neurochirurgie","SK-FMH-NEUROSURG"),
 ("SPEC-ONCO","Medizinische Onkologie","Medical oncology","medical_specialty","SIWF","siwf:facharzt/onkologie","SK-FMH-ONCO"),
 ("SPEC-RADONC","Radio-Onkologie","Radiation oncology","medical_specialty","SIWF","siwf:facharzt/radioonkologie","SK-FMH-RADONC"),
 ("SPEC-SURG","Chirurgie (Viszeral)","Visceral surgery","medical_specialty","SIWF","siwf:facharzt/chirurgie","SK-FMH-SURG"),
 ("SPEC-ORTHO","Orthopädie & Traumatologie","Orthopaedics & traumatology","medical_specialty","SIWF","siwf:facharzt/orthopaedie","SK-FMH-ORTHO"),
 ("SPEC-GYN","Gynäkologie & Geburtshilfe","Gynaecology & obstetrics","medical_specialty","SIWF","siwf:facharzt/gynaekologie","SK-FMH-GYN"),
 ("SPEC-PAED","Kinder- & Jugendmedizin","Paediatrics","medical_specialty","SIWF","siwf:facharzt/paediatrie","SK-FMH-PAED"),
 ("SPEC-NEONAT","Neonatologie","Neonatology","medical_specialty","SIWF","siwf:schwerpunkt/neonatologie","SK-FMH-NEONAT"),
 ("SPEC-INTMED","Allgemeine Innere Medizin","General internal medicine","medical_specialty","SIWF","siwf:facharzt/innere-medizin","SK-FMH-INTMED"),
 ("SPEC-RADIOL","Radiologie","Radiology","medical_specialty","SIWF","siwf:facharzt/radiologie","SK-FMH-RADIOL"),
 ("SPEC-NUCMED","Nuklearmedizin","Nuclear medicine","medical_specialty","SIWF","siwf:facharzt/nuklearmedizin","SK-FMH-NUCMED"),
 ("SPEC-NEPHRO","Nephrologie","Nephrology","medical_specialty","SIWF","siwf:facharzt/nephrologie","SK-FMH-NEPHRO"),
 ("SPEC-PALL","Palliativmedizin","Palliative medicine","medical_specialty","SIWF","siwf:schwerpunkt/palliativmedizin","SK-FMH-PALL"),
 ("SPEC-OPHT","Ophthalmologie","Ophthalmology","medical_specialty","SIWF","siwf:facharzt/ophthalmologie","SK-FMH-OPHT"),
 ("SPEC-IPS-NURSE","NDS HF Intensivpflege","ICU nursing (NDS HF)","nursing_specialisation","OdASanté/SBFI","odasante:nds-hf/intensivpflege","SK-NDS-IPS"),
 ("SPEC-ANAES-NURSE","NDS HF Anästhesiepflege","Anaesthesia nursing (NDS HF)","nursing_specialisation","OdASanté/SBFI","odasante:nds-hf/anaesthesiepflege","SK-NDS-ANAES"),
 ("SPEC-NOTF-NURSE","NDS HF Notfallpflege","Emergency nursing (NDS HF)","nursing_specialisation","OdASanté/SBFI","odasante:nds-hf/notfallpflege","SK-NDS-NOTF"),
 ("SPEC-OTA","Operationstechnik HF","Operating-theatre technology (HF)","technical","NAREG","nareg:hf/operationstechnik","SK-LIC-OTA"),
 ("SPEC-MTRA","Radiologie HF (MTRA)","Radiography (HF)","technical","NAREG","nareg:hf/radiologie","SK-LIC-MTRA"),
 ("SPEC-PARA","Rettungssanität HF","Paramedic (HF)","technical","NAREG","nareg:hf/rettungssanitaet","SK-LIC-PARA"),
 ("SPEC-MIDWIFE","Hebamme BSc","Midwifery (BSc)","nursing_specialisation","GesReg","gesreg:bsc/hebamme","SK-LIC-MIDWIFE"),
 ("SPEC-DIAL","Dialyse / Nierenersatzverfahren","Dialysis / renal replacement","nursing_specialisation","In-house/HöFa","inhouse:spec/dialyse","SK-DIAL"),
]
write_csv("dim_specialisation.csv",
          ["specialisation_id","specialisation_name_de","specialisation_name_en","spec_type","anchor_source","esco_or_siwf_ref","related_skill_id"],
          SPEC)

# ---------------------------------------------------------------------------
# 5. dim_issuing_authority
# ---------------------------------------------------------------------------
AUTH = [
 ("AUTH-MEDREG","MedReg — Medizinalberuferegister","federal_register","L4","yes","CH","bag.admin.ch/medreg"),
 ("AUTH-GESREG","GesReg — Gesundheitsberuferegister","federal_register","L4","yes","CH","gesreg.ch"),
 ("AUTH-NAREG","NAREG — Nat. Register der Gesundheitsberufe","federal_register","L4","yes","CH","nareg.ch"),
 ("AUTH-PSYREG","PsyReg — Psychologieberuferegister","federal_register","L4","yes","CH","bag.admin.ch/psyreg"),
 ("AUTH-SIWF","SIWF / ISFM (FMH)","specialist_body","L3","no","CH","siwf.ch"),
 ("AUTH-SGAR","SGAR — Anästhesie-Fachgesellschaft","specialist_body","L3","no","CH","sgar-ssar.ch"),
 ("AUTH-SGI","SGI — Intensivmedizin-Fachgesellschaft","specialist_body","L3","no","CH","sgi-ssmi.ch"),
 ("AUTH-SGNOR","SGNOR — Notfall- & Rettungsmedizin","specialist_body","L3","no","CH","sgnor.ch"),
 ("AUTH-ODASANTE","OdASanté — Nat. OdA Gesundheit","education","L3","no","CH","odasante.ch"),
 ("AUTH-SBFI","SBFI/SEFRI — Staatssekretariat BFI","education","L3","no","CH","sbfi.admin.ch"),
 ("AUTH-EDK","EDK/CDIP — Diplomanerkennung","education","L3","no","CH","edk.ch"),
 ("AUTH-SBK-ELOG","SBK/ASI eLog — Pflege-CPD","specialist_body","L1","no","CH","sbk-asi.ch"),
 ("AUTH-SRC","SRC — Swiss Resuscitation Council","cert_body","L2","no","CH","resuscitation.ch"),
 ("AUTH-IVR","IVR-IAS — Interverband für Rettungswesen","cert_body","L2","no","CH","ivr-ias.ch"),
 ("AUTH-BAG-SSK","BAG Strahlenschutz-Sachkunde","cert_body","L2","no","CH","bag.admin.ch/strahlenschutz"),
 ("AUTH-SWISSNOSO","Swissnoso — Infektionsprävention","cert_body","L2","no","CH","swissnoso.ch"),
 ("AUTH-SRK","SRK — Schweizerisches Rotes Kreuz (Anerkennung)","foreign_recognition","L3","no","CH","redcross.ch"),
 ("AUTH-MEBEKO","MEBEKO — Medizinalberufekommission","foreign_recognition","L4","no","CH","bag.admin.ch/mebeko"),
 ("AUTH-FIDE","fide — Schweizer Sprachkompetenzsystem","language","L2","no","CH","fide-info.ch"),
 ("AUTH-ORCID","ORCID","research","L2","no","INT","orcid.org"),
 ("AUTH-PUBMED","PubMed / MEDLINE (NCBI)","research","L2","no","INT","pubmed.ncbi.nlm.nih.gov"),
 ("AUTH-SNSF","SNSF P3","research","L3","no","CH","p3.snf.ch"),
 ("AUTH-ESCO","ESCO (EU)","taxonomy","L0","no","EU","esco.ec.europa.eu"),
 ("AUTH-FHIR","HL7 FHIR R5","taxonomy","L0","no","INT","hl7.org/fhir"),
 ("AUTH-SNOMED","SNOMED CT","taxonomy","L0","no","INT","snomed.org"),
 ("AUTH-LMS","In-house LMS / Skills-Passport","cert_body","L1","no","facility","internal"),
 ("AUTH-WORKID","Work-ID (Work-ID AG)","labour_market","L0","no","CH","work-id.ch"),
 ("AUTH-SKILLSMGR","Skills-Manager (Work-ID AG)","labour_market","L1","no","CH","skills-manager.ch"),
]
write_csv("dim_issuing_authority.csv",
          ["authority_id","authority_name","authority_kind","base_assurance_level","gln_keyed","jurisdiction","verify_reference"],
          AUTH)

# ---------------------------------------------------------------------------
# 6. dim_assurance_level  &  dim_proficiency_level
# ---------------------------------------------------------------------------
write_csv("dim_assurance_level.csv",
          ["assurance_level","name","evidence_source","verifiable","fit_for"],
          [("L4","Federally registered / licensed","MedReg, GesReg, NAREG, PsyReg (GLN-keyed)","yes","Any safety-critical rostering; legal gate"),
           ("L3","Accredited diploma / specialist title","SIWF/FMH, OdASanté/SBFI, SRK recognition","yes","Scope-of-practice, sub-specialty allocation"),
           ("L2","Issued dated certificate","SRC, BAG radiation, fide, in-house course","partly","Task competency within validity window"),
           ("L1","Manager sign-off / supervised log","Ward-lead confirmation, in-house LMS","internal","Refines currency; not a standalone gate"),
           ("L0","Self-declared / inferred","Self-report, Work-ID, document mining","no","Discovery & suggestions only")])
write_csv("dim_proficiency_level.csv",
          ["proficiency_level","name","description"],
          [(1,"Novice","Requires supervision for all tasks"),
           (2,"Advanced beginner","Handles routine tasks with occasional support"),
           (3,"Competent","Works independently within scope"),
           (4,"Proficient","Handles complex cases; can supervise juniors"),
           (5,"Expert","Reference competency; leads, teaches, sets standard")])

# ---------------------------------------------------------------------------
# 7. dim_occupation_role
# ---------------------------------------------------------------------------
OCC = [
 ("OCC-RN","Pflegefachfrau/-mann (Station)","Registered nurse (ward)","2221","esco:occupation/nursing-professional","GesReg","L4"),
 ("OCC-ICU-RN","Intensivpflegefachperson","Intensive care nurse","2221","esco:occupation/specialist-nurse-icu","GesReg","L4"),
 ("OCC-ANAES-RN","Anästhesiepflegefachperson","Anaesthesia nurse","2221","esco:occupation/specialist-nurse-anaesthesia","GesReg","L4"),
 ("OCC-ER-RN","Notfallpflegefachperson","Emergency nurse","2221","esco:occupation/specialist-nurse-emergency","GesReg","L4"),
 ("OCC-SCRUB","Fachperson Operationstechnik HF","Scrub / OR technician","3211","esco:occupation/operating-theatre-technician","NAREG","L4"),
 ("OCC-MTRA","Fachperson Radiologie HF (MTRA)","Radiographer","3211","esco:occupation/radiographer","NAREG","L4"),
 ("OCC-PARA","Rettungssanitäter/in HF","Paramedic","3258","esco:occupation/ambulance-paramedic","NAREG","L4"),
 ("OCC-MIDWIFE","Hebamme","Midwife","2222","esco:occupation/midwife","GesReg","L4"),
 ("OCC-PHYS-ANAES","Facharzt/-ärztin Anästhesiologie","Anaesthetist physician","2212","esco:occupation/specialist-anaesthetist","MedReg","L4"),
 ("OCC-PHYS-INTENS","Ärztin/Arzt Intensivmedizin","Intensive-care physician","2212","esco:occupation/specialist-intensivist","MedReg","L4"),
 ("OCC-PHYS-EMERG","Ärztin/Arzt Notfallmedizin","Emergency physician","2212","esco:occupation/specialist-emergency","MedReg","L4"),
 ("OCC-PHYS-SURG","Fachärztin/-arzt Chirurgie","Surgeon","2212","esco:occupation/specialist-surgeon","MedReg","L4"),
 ("OCC-PHYS-INTMED","Fachärztin/-arzt Innere Medizin","Internal-medicine physician","2212","esco:occupation/specialist-internal","MedReg","L4"),
 ("OCC-PHYS-CARD","Fachärztin/-arzt Kardiologie","Cardiologist","2212","esco:occupation/specialist-cardiologist","MedReg","L4"),
 ("OCC-PHYS-NEURO","Fachärztin/-arzt Neurologie","Neurologist","2212","esco:occupation/specialist-neurologist","MedReg","L4"),
 ("OCC-PHYS-ONCO","Fachärztin/-arzt Onkologie","Oncologist","2212","esco:occupation/specialist-oncologist","MedReg","L4"),
 ("OCC-PHYS-GYN","Fachärztin/-arzt Gynäkologie","Gynaecologist","2212","esco:occupation/specialist-gynaecologist","MedReg","L4"),
 ("OCC-PHYS-PAED","Fachärztin/-arzt Pädiatrie","Paediatrician","2212","esco:occupation/specialist-paediatrician","MedReg","L4"),
 ("OCC-PHYS-RADIOL","Fachärztin/-arzt Radiologie","Radiologist","2212","esco:occupation/specialist-radiologist","MedReg","L4"),
 ("OCC-PHYS-NEPHRO","Fachärztin/-arzt Nephrologie","Nephrologist","2212","esco:occupation/specialist-nephrologist","MedReg","L4"),
 ("OCC-PHYSIO","Physiotherapeut/in","Physiotherapist","2264","esco:occupation/physiotherapist","GesReg","L4"),
 ("OCC-BEDMGR","Bettenmanager/in (BMCA)","Bed / flow manager","1342","esco:occupation/health-services-manager","none","L1"),
 ("OCC-ORCOORD","OP-Koordinator/in (ORSA)","OR coordinator","1342","esco:occupation/health-services-manager","none","L1"),
 ("OCC-DISCHARGE","Austritts-/Care-Transition-Koordination (DCA)","Discharge coordinator","2221","esco:occupation/case-manager-nurse","GesReg","L4"),
 ("OCC-CRISIS","Dienst-/Krisenmanager/in (CSA)","Duty / crisis manager","1342","esco:occupation/emergency-response-coordinator","none","L1"),
 ("OCC-DQ","Datenqualität- & Ontologie-Steward (DQ)","Data / ontology steward","2521","esco:occupation/data-steward","none","L1"),
 ("OCC-WARDLEAD","Stationsleitung","Ward lead","1342","esco:occupation/nurse-manager","GesReg","L4"),
]
write_csv("dim_occupation_role.csv",
          ["occupation_id","label_de","label_en","isco_08_code","esco_occupation_uri","professional_register","licence_assurance"],
          OCC)

# ---------------------------------------------------------------------------
# 8. dim_skill  (Step-2 catalogue)
#    fields: label_de, label_en, category, skill_type, authority, default_assurance,
#            is_safety_critical, has_expiry, validity_months
# ---------------------------------------------------------------------------
SKILLS = [
 # cross-cutting
 ("SK-BLS","Basale Reanimation BLS-AED","Basic life support BLS-AED","clinical","skill","AUTH-SRC","L2",1,1,24),
 ("SK-ACLS","Erweiterte Reanimation ACLS/ALS","Advanced life support ACLS","clinical","skill","AUTH-SRC","L2",1,1,24),
 ("SK-PALS","Pädiatrische Reanimation PALS","Paediatric advanced life support","clinical","skill","AUTH-SRC","L2",1,1,24),
 ("SK-IPC","Infektionsprävention & Hygiene","Infection prevention & control","clinical","skill","AUTH-SWISSNOSO","L2",1,1,12),
 ("SK-MEDADMIN","Sichere Medikamentenverabreichung","Safe medication administration","clinical","skill","AUTH-LMS","L1",1,0,0),
 ("SK-DOC","Klinische Dokumentation (KIS)","Clinical documentation (HIS)","digital","skill","AUTH-LMS","L1",0,0,0),
 ("SK-DEESC","Deeskalation / Patientensicherheit","De-escalation / patient safety","clinical","transversal","AUTH-LMS","L1",0,1,24),
 ("SK-DE-B2","Deutsch Stationssprache B2+","German ward language B2+","language","language","AUTH-FIDE","L2",1,0,0),
 ("SK-FR-B2","Französisch B2+","French B2+","language","language","AUTH-FIDE","L2",0,0,0),
 ("SK-IT-B2","Italienisch B2+","Italian B2+","language","language","AUTH-FIDE","L2",0,0,0),
 ("SK-DATA","Datenschutz DSG / Informationssicherheit","Data protection / infosec","regulatory","knowledge","AUTH-LMS","L1",0,1,12),
 # licences
 ("SK-LIC-NURSE","Berufsausübung Pflege HF/BSc","Nursing practice licence","regulatory","skill","AUTH-GESREG","L4",1,0,0),
 ("SK-LIC-MIDWIFE","Berufsausübung Hebamme BSc","Midwifery practice licence","regulatory","skill","AUTH-GESREG","L4",1,0,0),
 ("SK-LIC-OTA","Berufsausübung Operationstechnik HF","OR-tech practice licence","regulatory","skill","AUTH-NAREG","L4",1,0,0),
 ("SK-LIC-MTRA","Berufsausübung Radiologie HF","Radiography practice licence","regulatory","skill","AUTH-NAREG","L4",1,0,0),
 ("SK-LIC-PARA","Berufsausübung Rettungssanität HF","Paramedic practice licence","regulatory","skill","AUTH-NAREG","L4",1,0,0),
 ("SK-LIC-PHYS","Ärztliche Berufsausübungsbewilligung","Physician practice licence","regulatory","skill","AUTH-MEDREG","L4",1,0,0),
 ("SK-LIC-PHYSIO","Berufsausübung Physiotherapie","Physiotherapy practice licence","regulatory","skill","AUTH-GESREG","L4",1,0,0),
 ("SK-LIC-PSY","Weiterbildungstitel Psychotherapie","Psychotherapy title","regulatory","skill","AUTH-PSYREG","L4",1,0,0),
 # nursing specialisations
 ("SK-NDS-IPS","NDS HF Intensivpflege","ICU nursing (NDS HF)","clinical","skill","AUTH-ODASANTE","L3",1,0,0),
 ("SK-NDS-ANAES","NDS HF Anästhesiepflege","Anaesthesia nursing (NDS HF)","clinical","skill","AUTH-ODASANTE","L3",1,0,0),
 ("SK-NDS-NOTF","NDS HF Notfallpflege","Emergency nursing (NDS HF)","clinical","skill","AUTH-ODASANTE","L3",1,0,0),
 ("SK-VENT","Beatmung / Ventilator-Management","Ventilator management","clinical","skill","AUTH-LMS","L2",1,1,24),
 ("SK-HAEMO","Hämodynamisches Monitoring","Haemodynamic monitoring","clinical","skill","AUTH-LMS","L1",1,0,0),
 ("SK-ECMO","ECMO-Betreuung","ECMO management","clinical","skill","AUTH-LMS","L2",1,1,24),
 ("SK-DIAL","Dialyse / Nierenersatzverfahren","Dialysis / renal replacement","technical","skill","AUTH-LMS","L2",1,1,24),
 ("SK-SCRUB","Perioperative Instrumentierung (Scrub)","Perioperative scrub","clinical","skill","AUTH-LMS","L1",1,0,0),
 ("SK-TRIAGE","Notfall-Triage","Emergency triage","clinical","skill","AUTH-LMS","L1",1,1,24),
 ("SK-OBST","Geburtshilfliche Betreuung","Obstetric care","clinical","skill","AUTH-GESREG","L4",1,0,0),
 ("SK-NEO","Neonatologische Pflege","Neonatal nursing","clinical","skill","AUTH-LMS","L1",1,1,24),
 ("SK-WOUND","Komplexes Wundmanagement","Complex wound management","clinical","skill","AUTH-LMS","L1",0,1,36),
 ("SK-ONCO-NURSE","Onkologiepflege / Chemo-Handling","Oncology nursing / chemo","clinical","skill","AUTH-LMS","L2",1,1,24),
 # physician specialties
 ("SK-FMH-ANAES","FMH Anästhesiologie","FMH anaesthesiology","clinical","skill","AUTH-SIWF","L3",1,0,0),
 ("SK-FMH-INTENS","Schwerpunkt Intensivmedizin","Intensive-care medicine","clinical","skill","AUTH-SIWF","L3",1,0,0),
 ("SK-FMH-NOTF","Schwerpunkt Klinische Notfallmedizin","Clinical emergency medicine","clinical","skill","AUTH-SGNOR","L3",1,0,0),
 ("SK-FMH-CARD","FMH Kardiologie","FMH cardiology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-CARDSURG","FMH Herz-/Gefässchirurgie","FMH cardiac surgery","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-NEURO","FMH Neurologie","FMH neurology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-NEUROSURG","FMH Neurochirurgie","FMH neurosurgery","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-ONCO","FMH Medizinische Onkologie","FMH medical oncology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-RADONC","FMH Radio-Onkologie","FMH radiation oncology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-SURG","FMH Chirurgie","FMH surgery","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-ORTHO","FMH Orthopädie & Traumatologie","FMH orthopaedics","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-GYN","FMH Gynäkologie & Geburtshilfe","FMH gynaecology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-PAED","FMH Kinder- & Jugendmedizin","FMH paediatrics","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-NEONAT","Schwerpunkt Neonatologie","Neonatology","clinical","skill","AUTH-SIWF","L3",1,0,0),
 ("SK-FMH-INTMED","FMH Allgemeine Innere Medizin","FMH internal medicine","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-RADIOL","FMH Radiologie","FMH radiology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-NUCMED","FMH Nuklearmedizin","FMH nuclear medicine","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-NEPHRO","FMH Nephrologie","FMH nephrology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-PALL","Schwerpunkt Palliativmedizin","Palliative medicine","clinical","skill","AUTH-SIWF","L3",0,0,0),
 ("SK-FMH-OPHT","FMH Ophthalmologie","FMH ophthalmology","clinical","skill","AUTH-SIWF","L3",0,0,0),
 # technical / diagnostic
 ("SK-RADPROT","Strahlenschutz-Sachkunde","Radiation-protection competence","regulatory","skill","AUTH-BAG-SSK","L2",1,1,60),
 ("SK-CT","CT-Bildgebung","CT imaging","technical","skill","AUTH-LMS","L1",1,0,0),
 ("SK-MRI","MRT-Bildgebung","MRI imaging","technical","skill","AUTH-LMS","L1",1,0,0),
 ("SK-PETCT","PET-CT / SPECT-CT","PET-CT / SPECT-CT","technical","skill","AUTH-LMS","L1",1,0,0),
 ("SK-MAMMO","Mammographie / BrustCentrum","Mammography","technical","skill","AUTH-LMS","L2",1,1,36),
 ("SK-LAB","Biomedizinische Analytik","Biomedical analysis","technical","skill","AUTH-NAREG","L4",0,0,0),
 ("SK-PATH","Pathologie-Aufarbeitung","Pathology processing","technical","skill","AUTH-LMS","L1",0,0,0),
 # leadership / ops
 ("SK-BEDFLOW","Bettenmanagement / Patientenfluss","Bed / flow management","leadership","skill","AUTH-LMS","L1",0,1,24),
 ("SK-ORCOORD","OP-Koordination / Slate-Management","OR coordination","leadership","skill","AUTH-LMS","L1",0,1,24),
 ("SK-DISCHARGE","Austrittsplanung / Care-Transition","Discharge / care transition","leadership","skill","AUTH-LMS","L1",0,1,24),
 ("SK-CRISIS","Krisen-/Lagemanagement","Crisis / incident command","leadership","skill","AUTH-LMS","L1",0,1,24),
 ("SK-ROSTER","Dienstplanung / Personaleinsatz","Rostering / staffing","leadership","skill","AUTH-LMS","L1",0,0,0),
 ("SK-DQSTEWARD","Datenqualität / Ontologie-Stewardship","Data / ontology stewardship","digital","skill","AUTH-LMS","L2",0,0,0),
 ("SK-WARDLEAD","Stationsleitung (Leadership)","Ward leadership","leadership","skill","AUTH-LMS","L1",0,0,0),
]
skill_meta = {s[0]: s for s in SKILLS}
write_csv("dim_skill.csv",
          ["skill_id","label_de","label_en","skill_category","skill_type","anchor_authority_id","default_min_assurance","is_safety_critical","has_expiry","typical_validity_months"],
          [[s[0],s[1],s[2],s[3],s[4],s[5],s[6],("TRUE" if s[7] else "FALSE"),("TRUE" if s[8] else "FALSE"),s[9]] for s in SKILLS])

# ---------------------------------------------------------------------------
# 9. dim_capacity_unit  (per department, by archetype)
# ---------------------------------------------------------------------------
def dept_archetype(name, role):
    n = (name + " " + role).lower()
    if "intensivstation" in n or ("intensiv" in n and "notfall" in n) or n.strip()=="ips" or "ips" in n.split():
        return "critical_care"
    if "intensiv" in n: return "critical_care"
    if "rettungsdienst" in n or ("notfall" in n): return "emergency"
    if "herz" in n: return "cardiology"
    if "neuro" in n: return "neuro"
    if "tumor" in n or "onko" in n: return "onco"
    if "innere" in n: return "internal"
    if "trauma" in n or "orthop" in n or "unfall" in n or "chirurgie" in n: return "surgery"
    if "frauen" in n or "gyn" in n or "geburt" in n: return "obstetrics"
    if "kinder" in n: return "paediatrics"
    if "radiolog" in n or "diagnost" in n or "nuklear" in n or "brust" in n: return "radiology"
    if "nephro" in n or "dialyse" in n: return "nephrology"
    if "forschung" in n: return "research"
    return "general"

def to_int(x):
    try: return int(x)
    except: return 0

cap_rows = []
cap_by_dept = {}
ucount = 0
for r in DEPARTMENTS:
    eid, sub, etype, name, parent, role, beds, fte, loc, canton, gln, grounded = r
    t = sub2tenant[sub]; arch = dept_archetype(name, role); b = to_int(beds)
    units = []
    def add_unit(utype, uname, slots, ratio, crit):
        global ucount
        ucount += 1
        uid = f"{eid}-U{len([x for x in cap_rows if x[1]==eid])+1:02d}"
        cap_rows.append([uid, eid, t, utype, uname, slots, canton, ratio, ("TRUE" if crit else "FALSE")])
        units.append(uid)
    if arch == "critical_care":
        nwards = 6 if eid == "CN-D7" else 2
        per = max(4, b // max(nwards,1)) if b else 8
        for i in range(nwards):
            add_unit("ICU","%s — IPS %d" % (name, i+1), per, "1:1 / 1:2 (Betten:Pflege)", True)
        if eid == "CN-D7":
            add_unit("ED_bay","Notfallzentrum — Schockraum", 6, "Triage-basiert", True)
            add_unit("OR_slot","Anästhesie — OP-Slots", 8, "1 Anästhesie-Team / Slot", True)
    elif arch == "emergency":
        add_unit("ED_bay","%s — Akut-/Schockraum" % name, max(6,b//2) if b else 8, "Triage-basiert", True)
        add_unit("ED_bay","%s — Behandlungsplätze" % name, max(6,b//2) if b else 8, "Triage-basiert", True)
        if "rettung" in role.lower():
            add_unit("transport","%s — Rettungswagen 144" % name, 4, "2 pro Fahrzeug", True)
    elif arch in ("cardiology","neuro","surgery"):
        add_unit("ward","%s — Station" % name, max(8,b) if b else 20, "1:4 (Tag) / 1:8 (Nacht)", False)
        add_unit("OR_slot","%s — OP-Slots" % name, 4, "Scrub + Anästhesie / Slot", True)
    elif arch == "onco":
        add_unit("ward","%s — Onkologie-Station" % name, max(8,b) if b else 20, "1:4 (Chemo-Handling)", True)
    elif arch == "obstetrics":
        add_unit("delivery_room","%s — Gebärsäle" % name, 4, "1 Hebamme / Geburt", True)
        add_unit("ward","%s — Wochenbett/Neo" % name, max(8,b) if b else 20, "1:4", True)
    elif arch == "paediatrics":
        add_unit("ward","%s — Station" % name, max(8,b) if b else 20, "1:4", True)
    elif arch == "radiology":
        add_unit("imaging","%s — CT/MRT" % name, 3, "1 MTRA / Modalität", True)
        if "nuklear" in (name+role).lower(): add_unit("imaging","%s — PET-CT/SPECT" % name, 2, "1 MTRA / Modalität", True)
        if "brust" in (name+role).lower(): add_unit("imaging","%s — Mammographie" % name, 2, "1 MTRA / Modalität", True)
    elif arch == "nephrology":
        add_unit("dialysis_station","%s — Dialyseplätze" % name, 23, "1:3 (Pflege:Plätze)", True)
    elif arch == "internal":
        add_unit("ward","%s — Station" % name, max(8,b) if b else 20, "1:4 / 1:8", False)
        if "palliativ" in role.lower(): add_unit("ward","%s — Palliativstation" % name, 8, "1:3", True)
    else:
        add_unit("ward","%s — Station" % name, max(8,b) if b else 15, "1:4 / 1:8", False)
    cap_by_dept[eid] = units
write_csv("dim_capacity_unit.csv",
          ["unit_id","department_id","tenant_id","unit_type","unit_name","beds_or_slots","canton","staffing_ratio_rule","is_safety_critical"],
          cap_rows)

# ---------------------------------------------------------------------------
# 10. Employees + positions
# ---------------------------------------------------------------------------
DEPT_PLAN = {
 "CN-D1":{"OCC-RN":3,"OCC-ICU-RN":1,"OCC-PHYS-CARD":2,"OCC-SCRUB":1},
 "CN-D2":{"OCC-RN":3,"OCC-PHYS-NEURO":2},
 "CN-D3":{"OCC-RN":4,"OCC-PHYS-INTMED":2,"OCC-PHYS-ONCO":1,"OCC-DISCHARGE":1},
 "CN-D4":{"OCC-RN":3,"OCC-SCRUB":1,"OCC-PHYS-SURG":2,"OCC-ORCOORD":1},
 "CN-D5":{"OCC-MIDWIFE":2,"OCC-RN":2,"OCC-PHYS-GYN":1,"OCC-PHYS-PAED":1},
 "CN-D6":{"OCC-MTRA":3,"OCC-PHYS-RADIOL":2},
 "CN-D7":{"OCC-ICU-RN":5,"OCC-ANAES-RN":2,"OCC-ER-RN":2,"OCC-PHYS-INTENS":2,"OCC-PHYS-ANAES":1,"OCC-BEDMGR":1,"OCC-CRISIS":1},
 "CN-D8":{"OCC-DQ":1,"OCC-PHYS-INTMED":1},
 "CP-D1":{"OCC-RN":3,"OCC-PHYS-CARD":2,"OCC-SCRUB":1},
 "CP-D2":{"OCC-RN":2,"OCC-PHYS-NEURO":1},
 "CP-D3":{"OCC-RN":3,"OCC-PHYS-ONCO":2,"OCC-DISCHARGE":1},
 "CP-D4":{"OCC-MIDWIFE":2,"OCC-RN":1,"OCC-PHYS-GYN":1},
 "CP-D5":{"OCC-RN":2,"OCC-PHYS-PAED":2},
 "CP-D6":{"OCC-ER-RN":3,"OCC-PARA":3,"OCC-PHYS-EMERG":2,"OCC-BEDMGR":1,"OCC-CRISIS":1},
 "CP-D7":{"OCC-RN":2,"OCC-SCRUB":1,"OCC-PHYS-SURG":1,"OCC-ORCOORD":1},
 "CP-D8":{"OCC-MTRA":2,"OCC-PHYS-RADIOL":1,"OCC-DQ":1},
 "VT-D1":{"OCC-RN":3,"OCC-PHYS-INTMED":1,"OCC-DISCHARGE":1},
 "VT-D2":{"OCC-MIDWIFE":2,"OCC-RN":1,"OCC-PHYS-GYN":1},
 "VT-D3":{"OCC-RN":2,"OCC-SCRUB":1,"OCC-PHYS-SURG":1,"OCC-ORCOORD":1},
 "VT-D4":{"OCC-RN":1,"OCC-PHYS-SURG":1},
 "VT-D5":{"OCC-ER-RN":3,"OCC-PHYS-EMERG":1},
 "VT-D6":{"OCC-ICU-RN":4,"OCC-PHYS-INTENS":1,"OCC-BEDMGR":1},
 "VT-D7":{"OCC-RN":2,"OCC-PHYS-NEPHRO":1},
 "VT-D8":{"OCC-MTRA":2,"OCC-PHYS-RADIOL":1,"OCC-DQ":1},
}

FIRST = ["Nora","Luca","Elena","Jonas","Mara","Timo","Sina","Ravi","Alina","Fabio","Lea","Nico","Yara","Silas",
 "Ines","Beat","Chiara","Kai","Anouk","Reto","Sophie","Diego","Livia","Manuel","Noemi","Andrin","Selin","Piero",
 "Jana","Cédric","Aline","Gian","Malin","Enzo","Rahel","Loris","Tabea","Aymo","Vera","Marco","Nadia","Sven",
 "Céline","Deniz","Larissa","Boris","Meret","Flurin","Zoe","Bruno","Nele","Ramon","Fiona","Aaron","Milena","Joel"]
LAST = ["Berger","Frei","Widmer","Steiner","Rossi","Baumann","Keller","Meier","Zbinden","Fontana","Graf","Huber",
 "Marti","Bianchi","Schmid","Roth","Vogel","Kunz","Suter","Moser","Bernasconi","Hofer","Lehmann","Brunner","Egli",
 "Favre","Studer","Ricci","Amacher","Gerber","Perren","Schneider","Furrer","Blanc","Odermatt","Caduff","Wyss",
 "Bühler","Colombo","Sennhauser","Truniger","Aebischer","Zürcher","Béguin","Nussbaumer","Reber","Locher","Villiger"]
used_names = set()
def make_name():
    for _ in range(500):
        g = random.choice(FIRST); fam = random.choice(LAST)
        if (g,fam) not in used_names:
            used_names.add((g,fam)); return g, fam
    return random.choice(FIRST), random.choice(LAST)+str(random.randint(2,9))

# canton per department (from org)
dept_canton = {r[0]: r[9] for r in DEPARTMENTS}
dept_name = {r[0]: r[3] for r in DEPARTMENTS}
dept_role = {r[0]: r[5] for r in DEPARTMENTS}
def arch_of(deptid): return dept_archetype(dept_name[deptid], dept_role[deptid])

emp_rows, pos_rows = [], []
employees = []            # dict per employee
pos_counter = 0
gcount = {"CN":0,"CP":0,"VT":0}
statuses = ["active"]*17 + ["active_parttime","on_leave","active"]
for dept, plan in DEPT_PLAN.items():
    t = dept[:2] if dept[:2] in ("CN","CP","VT") else dept.split("-")[0]
    t = "CN" if dept.startswith("CN") else "CP" if dept.startswith("CP") else "VT"
    canton = dept_canton[dept]
    for occ, cnt in plan.items():
        pos_counter += 1
        pos_id = f"POS-{dept}-{occ.replace('OCC-','')}"
        planned_fte = round(cnt * random.choice([0.8,0.9,1.0,1.0]) + random.choice([0,0.2,0.4]),1)
        pos_rows.append([pos_id, t, dept, occ, planned_fte, cnt+random.choice([0,0,1]), "3-Schicht" if occ in ("OCC-ICU-RN","OCC-ER-RN","OCC-ANAES-RN","OCC-RN","OCC-PARA") else "Tagdienst", "FALSE"])
        for _ in range(cnt):
            gcount[t] += 1
            n = gcount[t]
            gln = person_gln(TCODE[t], n)
            g, fam = make_name()
            eid = f"EMP-{t}-{n:04d}"
            contract = random.choice([1.0,1.0,0.9,0.8,0.8,0.6,1.0])
            hire = REF - timedelta(days=random.randint(120, 5200))
            addlangs = []
            if canton == "VS" or random.random() < 0.18: addlangs.append("FR-B1")
            if random.random() < 0.10: addlangs.append("IT-B1")
            if random.random() < 0.12: addlangs.append("EN-B2")
            status = random.choice(statuses)
            work_id_ref = ""  # set later if opted in
            emp = dict(employee_id=eid, gln=gln, tenant=t, dept=dept, pos=pos_id, occ=occ,
                       given=g, family=fam, status=status, fte=contract, hire=hire,
                       canton=canton, primlang="DE-C1" if random.random()<0.7 else "DE-B2",
                       addlangs=";".join(addlangs))
            employees.append(emp)
write_csv("dim_workforce_position.csv",
          ["position_id","tenant_id","department_id","occupation_id","planned_fte","headcount_budget","shift_pattern","is_vacant"],
          pos_rows)

# ---------------------------------------------------------------------------
# 11. fact_skill_assertion  (+ collect for supply/eligibility)
# ---------------------------------------------------------------------------
OCC_RECIPE = {
 "OCC-RN":["SK-LIC-NURSE","SK-MEDADMIN","SK-BLS","SK-IPC","SK-DE-B2","SK-DOC"],
 "OCC-ICU-RN":["SK-LIC-NURSE","SK-NDS-IPS","SK-VENT","SK-HAEMO","SK-ACLS","SK-BLS","SK-IPC","SK-DE-B2"],
 "OCC-ANAES-RN":["SK-LIC-NURSE","SK-NDS-ANAES","SK-ACLS","SK-BLS","SK-IPC","SK-DE-B2"],
 "OCC-ER-RN":["SK-LIC-NURSE","SK-NDS-NOTF","SK-TRIAGE","SK-ACLS","SK-PALS","SK-BLS","SK-DE-B2"],
 "OCC-SCRUB":["SK-LIC-OTA","SK-SCRUB","SK-IPC","SK-DE-B2"],
 "OCC-MTRA":["SK-LIC-MTRA","SK-RADPROT","SK-CT","SK-DE-B2"],
 "OCC-PARA":["SK-LIC-PARA","SK-ACLS","SK-TRIAGE","SK-BLS","SK-DE-B2"],
 "OCC-MIDWIFE":["SK-LIC-MIDWIFE","SK-OBST","SK-BLS","SK-DE-B2"],
 "OCC-PHYS-ANAES":["SK-LIC-PHYS","SK-FMH-ANAES","SK-ACLS","SK-DE-B2"],
 "OCC-PHYS-INTENS":["SK-LIC-PHYS","SK-FMH-INTENS","SK-ACLS","SK-DE-B2"],
 "OCC-PHYS-EMERG":["SK-LIC-PHYS","SK-FMH-NOTF","SK-ACLS","SK-PALS","SK-DE-B2"],
 "OCC-PHYS-SURG":["SK-LIC-PHYS","SK-FMH-SURG","SK-DE-B2"],
 "OCC-PHYS-INTMED":["SK-LIC-PHYS","SK-FMH-INTMED","SK-DE-B2"],
 "OCC-PHYS-CARD":["SK-LIC-PHYS","SK-FMH-CARD","SK-DE-B2"],
 "OCC-PHYS-NEURO":["SK-LIC-PHYS","SK-FMH-NEURO","SK-DE-B2"],
 "OCC-PHYS-ONCO":["SK-LIC-PHYS","SK-FMH-ONCO","SK-DE-B2"],
 "OCC-PHYS-GYN":["SK-LIC-PHYS","SK-FMH-GYN","SK-DE-B2"],
 "OCC-PHYS-PAED":["SK-LIC-PHYS","SK-FMH-PAED","SK-PALS","SK-DE-B2"],
 "OCC-PHYS-RADIOL":["SK-LIC-PHYS","SK-FMH-RADIOL","SK-RADPROT","SK-DE-B2"],
 "OCC-PHYS-NEPHRO":["SK-LIC-PHYS","SK-FMH-NEPHRO","SK-DE-B2"],
 "OCC-PHYSIO":["SK-LIC-PHYSIO","SK-DE-B2"],
 "OCC-BEDMGR":["SK-BEDFLOW","SK-DE-B2","SK-DOC"],
 "OCC-ORCOORD":["SK-ORCOORD","SK-DE-B2","SK-DOC"],
 "OCC-DISCHARGE":["SK-LIC-NURSE","SK-DISCHARGE","SK-WOUND","SK-DE-B2"],
 "OCC-CRISIS":["SK-CRISIS","SK-DE-B2"],
 "OCC-DQ":["SK-DQSTEWARD","SK-DATA","SK-DE-B2"],
 "OCC-WARDLEAD":["SK-LIC-NURSE","SK-WARDLEAD","SK-DE-B2"],
}
EVID_TYPE = {"L4":"registration","L3":"diploma","L2":"certificate","L1":"signoff","L0":"self_declared"}
def prof_pick(minv=2):
    r = random.random()
    v = 2 if r<0.15 else 3 if r<0.5 else 4 if r<0.85 else 5
    return max(v, minv)
def evref(auth, skill):
    if auth=="AUTH-MEDREG": return "MEDREG-%06d" % random.randint(100000,999999)
    if auth=="AUTH-GESREG": return "GESREG-%06d" % random.randint(100000,999999)
    if auth=="AUTH-NAREG": return "NAREG-%06d" % random.randint(100000,999999)
    if auth=="AUTH-PSYREG": return "PSYREG-%06d" % random.randint(100000,999999)
    if auth=="AUTH-SIWF": return "SIWF-%s-%d" % (skill.replace("SK-FMH-",""), random.randint(2005,2024))
    if auth=="AUTH-SGNOR": return "SGNOR-%05d" % random.randint(1000,99999)
    if auth=="AUTH-ODASANTE": return "NDS-HF-%05d" % random.randint(10000,99999)
    if auth=="AUTH-SRC": return "SRC-%s-%06d" % (skill.replace("SK-",""), random.randint(100000,999999))
    if auth=="AUTH-BAG-SSK": return "BAG-SSK-%05d" % random.randint(10000,99999)
    if auth=="AUTH-FIDE": return "FIDE-%s-%05d" % (skill.split("-")[1], random.randint(10000,99999))
    if auth=="AUTH-SWISSNOSO": return "IPC-%05d" % random.randint(10000,99999)
    if auth=="AUTH-WORKID": return "WID-%08X" % random.randint(0,0xFFFFFFFF)
    return "LMS-%s-%05d" % (skill.replace("SK-",""), random.randint(10000,99999))

assertion_rows = []
# supply index: (dept, skill) -> list of (proficiency, assurance_rank, valid_until_or_None, employee_id)
supply = {}
# per-employee assertions map: emp_id -> {skill: (prof, assur, valid_until)}
emp_assert = {}
acount = 0
for emp in employees:
    recipe = list(OCC_RECIPE.get(emp["occ"], ["SK-DE-B2"]))
    # a share of general nurses in specialist wards carry the department add-on competency
    _addon = {"onco":"SK-ONCO-NURSE","nephrology":"SK-DIAL","paediatrics":"SK-PALS"}.get(arch_of(emp["dept"]))
    if emp["occ"] == "OCC-RN" and _addon and random.random() < 0.6:
        recipe.append(_addon)
    emp_assert[emp["employee_id"]] = {}
    for skill in recipe:
        meta = skill_meta[skill]
        default_assur = meta[6]; has_exp = meta[8]; vmonths = meta[9]; auth = meta[5]
        assur = default_assur
        etype = EVID_TYPE[assur]
        if assur == "L4": etype = "registration" if skill.startswith("SK-LIC") else ("licence" if False else "registration")
        if assur == "L3": etype = "diploma"
        if assur == "L2": etype = "certificate"
        if assur == "L1": etype = random.choice(["signoff","experience"])
        # validity
        if has_exp and vmonths:
            vm_days = int(vmonths*30.4)
            r = random.random()
            if r < 0.16:      # expired
                vu = REF - timedelta(days=random.randint(1,150)); vf = vu - timedelta(days=vm_days)
            elif r < 0.29:    # near expiry (<=30d)
                vu = REF + timedelta(days=random.randint(1,30)); vf = vu - timedelta(days=vm_days)
            else:
                vu = REF + timedelta(days=random.randint(45, vm_days)); vf = vu - timedelta(days=vm_days)
        else:
            vu = None; vf = REF - timedelta(days=random.randint(200, 3200))
            if vf < emp["hire"] - timedelta(days=400): vf = emp["hire"] - timedelta(days=random.randint(0,400))
        # verification status
        if assur == "L4":
            vstat = "register-verified"; vsrc = auth
            va = REF - timedelta(days=random.randint(1, 40))
            if random.random() < 0.10: va = REF - timedelta(days=random.randint(35, 90))  # a few stale -> DQ
        elif assur in ("L3","L2"):
            vstat = "issuer-confirmed"; vsrc = auth; va = REF - timedelta(days=random.randint(5,300))
        else:
            vstat = random.choice(["self","issuer-confirmed"]); vsrc = auth; va = REF - timedelta(days=random.randint(5,400))
        minp = 3 if skill.startswith("SK-LIC") else 2
        prof = prof_pick(minp)
        # make some ICU nurses novice on ACLS/VENT for demo realism
        if emp["occ"]=="OCC-ICU-RN" and skill in ("SK-VENT","SK-ACLS") and random.random()<0.25:
            prof = 2
        jur = emp["canton"] if assur=="L4" else ("national" if assur in ("L3","L2") else "facility")
        restr = ""
        if assur=="L4" and random.random()<0.05: restr = "Auflage: Tätigkeit unter Supervision (Demo)"
        acount += 1
        aid = "ASR-%06d" % acount
        assertion_rows.append([aid, emp["gln"], emp["employee_id"], skill, prof, etype, auth, evref(auth,skill),
                               assur, d(vf), d(vu), vstat, d(va), vsrc, jur, restr,
                               "HRIS" if assur=="L4" else "LMS", "PII-personal", "employment_contract"])
        supply.setdefault((emp["dept"], skill), []).append((prof, ASSUR_RANK[assur], vu, emp["employee_id"]))
        emp_assert[emp["employee_id"]][skill] = (prof, ASSUR_RANK[assur], vu)
    # ~35% get an extra Work-ID self-declared discovery skill (L0)
    if random.random() < 0.35:
        disc = random.choice(["SK-DEESC","SK-FR-B2","SK-IT-B2","SK-WOUND","SK-DOC"])
        acount += 1
        aid = "ASR-%06d" % acount
        emp["work_id"] = True
        assertion_rows.append([aid, emp["gln"], emp["employee_id"], disc, prof_pick(2), "self_declared",
                               "AUTH-WORKID", evref("AUTH-WORKID",disc), "L0", d(REF-timedelta(days=random.randint(10,300))),
                               "", "self", d(REF-timedelta(days=random.randint(10,300))), "AUTH-WORKID",
                               "facility", "", "work_id", "PII-personal", "worker_consent"])
write_csv("fact_skill_assertion.csv",
          ["assertion_id","worker_gln","employee_id","skill_id","proficiency_level","evidence_type","issuing_authority_id",
           "evidence_ref","assurance_level","valid_from","valid_until","verification_status","verified_at","verification_source",
           "jurisdiction_scope","restrictions","source_system","sensitivity_class","consent_basis"],
          assertion_rows)

# dim_employee (now that we know who has Work-ID)
for emp in employees:
    wid = ("WID-%08X" % random.randint(0,0xFFFFFFFF)) if emp.get("work_id") else ""
    emp["work_id_ref"] = wid
    emp_rows.append([emp["employee_id"], emp["gln"], emp["tenant"], emp["dept"], emp["pos"], emp["occ"],
                     emp["given"], emp["family"], emp["status"], emp["fte"], d(emp["hire"]),
                     emp["primlang"], emp["addlangs"], emp["canton"], wid])
write_csv("dim_employee.csv",
          ["employee_id","worker_gln","tenant_id","home_department_id","position_id","primary_occupation_id",
           "given_name","family_name","employment_status","contract_fte","hire_date","primary_language","additional_languages","canton","work_id_ref"],
          emp_rows)

# ---------------------------------------------------------------------------
# 12. bridge_role_skill_demand_template  (occupation/specialisation -> required skills)
# ---------------------------------------------------------------------------
# derive from OCC_RECIPE: mandatory if skill is safety-critical or a licence; else preferred
tmpl_rows = []; tcount = 0
for occ, skills in OCC_RECIPE.items():
    for sk in skills:
        meta = skill_meta[sk]
        mand = meta[7]==1 or sk.startswith("SK-LIC")
        minp = 3 if sk.startswith("SK-LIC") or sk in ("SK-NDS-IPS","SK-NDS-ANAES","SK-NDS-NOTF") else 2
        mina = meta[6] if (meta[6] in ("L2","L3","L4")) else "L1"
        tcount += 1
        tmpl_rows.append([f"TMPL-{tcount:03d}","occupation",occ,sk,minp,mina,("TRUE" if mand else "FALSE"),
                          "Sicherheitskritisch" if meta[7]==1 else "Kernkompetenz Rolle"])
write_csv("bridge_role_skill_demand_template.csv",
          ["template_id","applies_to_type","applies_to_id","skill_id","min_proficiency","min_assurance","is_mandatory","rationale"],
          tmpl_rows)

# ---------------------------------------------------------------------------
# 13. fact_skill_demand  (safety-critical units) + 14. fact_skill_gap + 15. eligibility
# ---------------------------------------------------------------------------
# archetype -> demand skills [(skill, minprof, minassur, applicable unit_types)]
# Headcounts are realistic PER-SHIFT numbers (comparable to the sampled workforce) so gaps are illustrative, not artefacts.
ARCH_DEMAND = {
 "critical_care":[("SK-NDS-IPS",3,"L3",("ICU",)),("SK-VENT",3,"L2",("ICU",)),
                  ("SK-ACLS",3,"L2",("ICU","ED_bay","OR_slot")),("SK-DE-B2",3,"L2",("ICU","ED_bay"))],
 "emergency":[("SK-ACLS",3,"L2",("ED_bay","transport")),("SK-TRIAGE",3,"L1",("ED_bay",)),("SK-DE-B2",3,"L2",("ED_bay",))],
 "obstetrics":[("SK-OBST",3,"L4",("delivery_room",)),("SK-DE-B2",3,"L2",("delivery_room",))],
 "nephrology":[("SK-DIAL",3,"L2",("dialysis_station",)),("SK-DE-B2",3,"L2",("dialysis_station",))],
 "radiology":[("SK-RADPROT",3,"L2",("imaging",)),("SK-DE-B2",3,"L2",("imaging",))],
 "surgery":[("SK-SCRUB",3,"L1",("OR_slot",)),("SK-DE-B2",3,"L2",("OR_slot",))],
 "cardiology":[("SK-ACLS",3,"L2",("OR_slot",)),("SK-DE-B2",3,"L2",("OR_slot",))],
 "onco":[("SK-ONCO-NURSE",3,"L2",("ward",)),("SK-DE-B2",3,"L2",("ward",))],
 "paediatrics":[("SK-PALS",3,"L2",("ward",)),("SK-DE-B2",3,"L2",("ward",))],
}
def head_for(utype):
    return {"ICU":3,"ED_bay":2,"OR_slot":1,"delivery_room":2,"dialysis_station":2,
            "imaging":1,"ward":2,"transport":2}.get(utype,2)
def valid_supply_count(dept, skill, minp, minassur):
    rank = ASSUR_RANK[minassur]
    cnt = 0; upcoming = []
    for (prof, arank, vu, empid) in supply.get((dept, skill), []):
        if arank >= rank and prof >= minp and (vu is None or vu >= REF):
            cnt += 1
            if vu is not None: upcoming.append(vu)
    ne = min(upcoming).isoformat() if upcoming else ""
    return cnt, ne
def redeploy_count(tenant, home_dept, skill, minp, minassur, canton):
    rank = ASSUR_RANK[minassur]; c = 0
    for (dp, sk), lst in supply.items():
        if sk != skill or dp == home_dept: continue
        # same tenant only
        if not dp.startswith(tenant): continue
        for (prof, arank, vu, empid) in lst:
            if arank >= rank and prof >= minp and (vu is None or vu >= REF):
                c += 1
    return c

demand_rows = []; gap_rows = []; dcount = 0; gcnt = 0
shift_windows = ["Nacht","Tag"]
for r in DEPARTMENTS:
    eid = r[0]; sub=r[1]; name=r[3]; role=r[5]; canton=r[9]
    t = "CN" if eid.startswith("CN") else "CP" if eid.startswith("CP") else "VT"
    arch = dept_archetype(name, role)
    if arch not in ARCH_DEMAND: continue
    units = [u for u in cap_rows if u[1]==eid and u[8]=="TRUE"]
    for u in units:
        uid = u[0]; utype = u[3]
        for (skill, minp, mina, utypes) in ARCH_DEMAND[arch]:
            if utype not in utypes:
                continue
            for sw in (shift_windows if arch in ("critical_care","emergency") else ["Tag"]):
                head = head_for(utype)
                dcount += 1
                demand_rows.append([f"DEM-{dcount:04d}", t, eid, uid, skill, minp, mina, head, sw, d(REF)])
                sup, ne = valid_supply_count(eid, skill, minp, mina)
                gap = max(0, head - sup)
                rc = redeploy_count(t, eid, skill, minp, mina, canton)
                gcnt += 1
                gap_rows.append([f"GAP-{gcnt:04d}", t, eid, uid, skill, sw, head, sup, gap, ne, rc, d(REF)])
write_csv("fact_skill_demand.csv",
          ["demand_id","tenant_id","department_id","unit_id","skill_id","min_proficiency","min_assurance","headcount_required","shift_window","effective_date"],
          demand_rows)
write_csv("fact_skill_gap.csv",
          ["gap_id","tenant_id","department_id","unit_id","skill_id","shift_window","headcount_required","valid_supply","gap","nearest_expiry_date","redeploy_candidates_count","computed_at"],
          gap_rows)

# 15. bridge_worker_unit_eligibility — evaluate each worker only against the unit types their role staffs
OCC_UNIT_FIT = {
 "OCC-ICU-RN":{"ICU"}, "OCC-ANAES-RN":{"ICU","OR_slot"}, "OCC-ER-RN":{"ED_bay"},
 "OCC-PARA":{"ED_bay","transport"}, "OCC-MIDWIFE":{"delivery_room"}, "OCC-MTRA":{"imaging"},
 "OCC-RN":{"ward","dialysis_station"}, "OCC-SCRUB":{"OR_slot"},
 "OCC-PHYS-INTENS":{"ICU"}, "OCC-PHYS-EMERG":{"ED_bay"}, "OCC-PHYS-ANAES":{"ICU","OR_slot"},
}
elig_rows = []; ecount = 0
for emp in employees:
    fit = OCC_UNIT_FIT.get(emp["occ"])
    if not fit: continue
    dept = emp["dept"]; arch = arch_of(dept)
    if arch not in ARCH_DEMAND: continue
    units = [u for u in cap_rows if u[1]==dept and u[8]=="TRUE" and u[3] in fit]
    ea = emp_assert.get(emp["employee_id"], {})
    for u in units:
        utype = u[3]
        reqs = [(sk,mp,ma) for (sk,mp,ma,uts) in ARCH_DEMAND[arch] if utype in uts]
        if not reqs: continue
        limiting = ""; eligible = True; nearest = None
        for (skill, minp, mina) in reqs:
            got = ea.get(skill)
            if got is None:
                eligible = False; limiting = limiting or f"fehlt: {skill}"; continue
            prof, arank, vu = got
            if arank < ASSUR_RANK[mina] or prof < minp:
                eligible = False; limiting = limiting or f"unter Schwelle: {skill}"
            if vu is not None and vu < REF:
                eligible = False; limiting = limiting or f"abgelaufen: {skill} ({vu.isoformat()})"
            if vu is not None and (nearest is None or vu < nearest): nearest = vu
        ecount += 1
        elig_rows.append([f"ELIG-{ecount:05d}", emp["employee_id"], emp["gln"], u[0], emp["tenant"],
                          ("TRUE" if eligible else "FALSE"), (limiting if not eligible else ""),
                          (nearest.isoformat() if nearest else ""), d(REF)])
write_csv("bridge_worker_unit_eligibility.csv",
          ["eligibility_id","employee_id","worker_gln","unit_id","tenant_id","is_eligible","limiting_factor","nearest_cert_expiry","computed_at"],
          elig_rows)

# ---------------------------------------------------------------------------
# 16. dim_work_id_profile
# ---------------------------------------------------------------------------
wid_rows = []
for emp in employees:
    if not emp.get("work_id"): continue
    consent = random.choice(["granted","granted","granted","pending","revoked"])
    scope = "skills:all" if consent=="granted" else ("skills:non-clinical" if consent=="pending" else "none")
    wid_rows.append([f"WIDP-{emp['employee_id']}", emp["employee_id"], emp["gln"], emp["work_id_ref"],
                     consent, scope, "worker_consent", d(REF-timedelta(days=random.randint(0,45))),
                     random.choice([60,70,80,90,100]), "work_id"])
write_csv("dim_work_id_profile.csv",
          ["work_id_profile_id","employee_id","worker_gln","work_id_ref","consent_status","visibility_scope","consent_basis","last_sync_at","profile_completeness_pct","external_system"],
          wid_rows)

# ---------------------------------------------------------------------------
# 17. map_skill_crosswalk
# ---------------------------------------------------------------------------
cw_rows = []
for s in SKILLS:
    sk = s[0]
    esco = "esco:skill/" + sk.replace("SK-","").lower()
    smc = "SM-" + sk.replace("SK-","")
    widl = s[1]
    conf = "high" if s[6] in ("L3","L4") else random.choice(["high","medium","medium","low"])
    cw_rows.append([f"CW-{sk}", sk, esco, "", smc, widl, conf])
write_csv("map_skill_crosswalk.csv",
          ["crosswalk_id","internal_skill_id","esco_uri","snomed_code","skills_manager_skill_code","work_id_skill_label","mapping_confidence"],
          cw_rows)

# ---------------------------------------------------------------------------
# 18. fact_skills_manager_sync_log
# ---------------------------------------------------------------------------
sync_rows = []
base = REF - timedelta(days=30)
for i in range(18):
    day = base + timedelta(days=random.randint(0,30))
    direction, src, tgt, rectype = random.choice([
        ("inbound","skills_manager","curavias_bronze","skills_inventory"),
        ("inbound","work_id","curavias_bronze","worker_share"),
        ("outbound","curavias_gold","skills_manager","skill_confirmation"),
    ])
    rin = random.randint(20,400); rup = random.randint(0,rin); rej = random.randint(0,8)
    status = "success" if rej < 6 else "partial"
    sync_rows.append([f"SYNC-{i+1:04d}", day.isoformat()+"T0"+str(random.randint(1,6))+":00:00", direction, src, tgt, rectype, rin, rup, rej, status])
write_csv("fact_skills_manager_sync_log.csv",
          ["sync_id","run_ts","direction","source_system","target_system","record_type","records_in","records_updated","records_rejected","status"],
          sync_rows)

print("TOTAL employees:", len(employees))
print("Done.")
