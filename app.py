import streamlit as st
import pandas as pd
import sqlite3

# 1. Dashboard-Header im EWE-Design
st.title("📊 EWE-Praktikumsprojekt: SQL Data Analytics")
st.markdown("""
Dieses Dashboard demonstriert die Kombination aus **Python, Streamlit und SQL** nativ unter Linux.
Im Hintergrund läuft eine SQLite-Datenbank, die typische CRM- und Vertragsdaten eines Energieversorgers simuliert.
""")

# 2. SQL-Datenbank im Hintergrund aufbauen & befüllen
@st.cache_resource # Sorgt dafür, dass die DB nicht bei jedem Klick neu erstellt wird
def erstelle_datenbank():
    # Verbindung zur (In-Memory) Datenbank herstellen
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    
    # Tabelle für EWE-Kunden erstellen
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ewe_kunden (
        kunden_id INTEGER PRIMARY KEY,
        stadt TEXT,
        vertragstyp TEXT,
        monats_verbrauch_kwh INTEGER,
        status TEXT
    )
    """)
    
    # Testdaten einfügen (Typische EWE-Regionen & Tarife)
    kunden_daten = [
        (101, 'Oldenburg', 'EWE Strom Classic', 250, 'Aktiv'),
        (102, 'Bremen', 'EWE Strom Green', 180, 'Aktiv'),
        (103, 'Wilhelmshaven', 'EWE Strom Classic', 410, 'Gekündigt'),
        (104, 'Oldenburg', 'EWE Strom Green', 310, 'Aktiv'),
        (105, 'Emden', 'EWE Strom Fix', 150, 'Aktiv'),
        (106, 'Bremen', 'EWE Strom Classic', 520, 'Gekündigt'),
        (107, 'Wilhelmshaven', 'EWE Strom Fix', 290, 'Aktiv'),
        (108, 'Oldenburg', 'EWE Strom Green', 220, 'Aktiv')
    ]
    
    cursor.executemany("INSERT INTO ewe_kunden VALUES (?, ?, ?, ?, ?)", kunden_daten)
    conn.commit()
    return conn

# Datenbank-Verbindung initialisieren
db_verbindung = erstelle_datenbank()

# 3. Interaktive SQL-Filterung in der Sidebar
st.sidebar.header("🔍 SQL-Filtersteuerung")

# Auswahlbox für die Stadt (SQL WHERE-Bedingung)
staedte = ['Alle', 'Oldenburg', 'Bremen', 'Wilhelmshaven', 'Emden']
ausgewaehlte_stadt = st.sidebar.selectbox("Region filtern:", staedte)

# 4. Die SQL-Abfrage (Query) dynamisch aufbauen
if ausgewaehlte_stadt == 'Alle':
    sql_query = "SELECT * FROM ewe_kunden"
else:
    # Sicherer SQL-String mit Platzhalter
    sql_query = f"SELECT * FROM ewe_kunden WHERE stadt = '{ausgewaehlte_stadt}'"

# 5. SQL-Befehl ausführen und in Pandas DataFrame laden
df_ergebnis = pd.read_sql_query(sql_query, db_verbindung)

# 6. Anzeige im Dashboard
st.subheader("1. Angewendeter SQL-Befehl")
st.code(sql_query, language="sql")

st.subheader("2. Abfrage-Ergebnis aus der Datenbank")
st.dataframe(df_ergebnis, use_container_width=True)

# 7. Kleine SQL-Aggregation für die Insights
st.subheader("3. Strategische Kennzahlen (SQL Aggregation)")

# Berechne den durchschnittlichen Verbrauch via SQL
cursor = db_verbindung.cursor()
if ausgewaehlte_stadt == 'Alle':
    cursor.execute("SELECT AVG(monats_verbrauch_kwh), COUNT(*) FROM ewe_kunden WHERE status='Gekündigt'")
else:
    cursor.execute(f"SELECT AVG(monats_verbrauch_kwh), COUNT(*) FROM ewe_kunden WHERE status='Gekündigt' AND stadt='{ausgewaehlte_stadt}'")

avg_verbrauch_kuendigung, anzahl_kuendigungen = cursor.fetchone()

col1, col2 = st.columns(2)
col1.metric(
    label="Kündigungen in Auswahl", 
    value=int(anzahl_kuendigungen) if anzahl_kuendigungen else 0
)
col2.metric(
    label="Ø Verbrauch Gekündigter", 
    value=f"{round(avg_verbrauch_kuendigung, 1) if avg_verbrauch_kuendigung else 0} kWh"
)

