import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd

# ===== Nastavení databáze =====
DB_PATH = Path("pujcovna.db")

# Vytvoření a naplnění databáze při prvním spuštění
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabulka strojů
    c.execute("""
    CREATE TABLE IF NOT EXISTS stroje (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT,
        popis TEXT,
        cena_za_den REAL,
        dostupnost INTEGER
    )
    """)

    # Tabulka klientů
    c.execute("""
    CREATE TABLE IF NOT EXISTS klienti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazev TEXT,
        adresa TEXT,
        ico TEXT,
        sleva REAL,
        kontakt TEXT
    )
    """)

    # Naplnit ukázkovými daty (jen pokud prázdné)
    c.execute("SELECT COUNT(*) FROM stroje")
    if c.fetchone()[0] == 0:
        data_stroje = [
            ("Bagr CAT 320", "Hloubení základů, výkonný bagr", 2500, 1),
            ("Vibrační deska Wacker", "Hutnění půdy a štěrku", 900, 0),
            ("Přívěs 3t", "Převoz sypkého materiálu", 800, 1),
            ("Míchačka ALTRAD 190L", "Míchání betonu a malty", 500, 1),
            ("Vibrační válec HAMM", "Zhutňování asfaltu", 2700, 0),
            ("Minibagr Kubota U17", "Malé výkopové práce", 1800, 1),
            ("Generátor Honda 5kW", "Záložní napájení na stavbě", 600, 1),
            ("Lešení Layher", "Montážní práce do výšky", 400, 1),
            ("Kompresor Atlas Copco", "Pneumatické nástroje", 950, 0),
            ("Vysokozdvižný vozík Toyota 2t", "Manipulace s materiálem", 1500, 1)
        ]
        c.executemany(
            "INSERT INTO stroje (nazev, popis, cena_za_den, dostupnost) VALUES (?, ?, ?, ?)",
            data_stroje
        )

    # Pokud ještě nejsou klienti, doplň základní testovací sadu (můžeš upravit podle sebe)
    c.execute("SELECT COUNT(*) FROM klienti")
    if c.fetchone()[0] == 0:
        data_klienti = [
            ("Stavmont s.r.o.", "Brno, Kovářská 10", "12345678", 10, "Jan Novák"),
            ("BETONtech a.s.", "Praha, Betonová 5", "87654321", 5, "Eva Křížová"),
            ("DŘEVOMAT s.r.o.", "Zlín, Lesní 22", "55667788", 0, "Petr Havel"),
            ("STAVOMAT spol. s r.o.", "Ostrava, Dolní 4", "99887766", 8, "Jiří Hrubý"),
            ("PůjčovnaPlus s.r.o.", "Plzeň, Letná 7", "88776655", 15, "Lucie Holá")
        ]
        c.executemany(
            "INSERT INTO klienti (nazev, adresa, ico, sleva, kontakt) VALUES (?, ?, ?, ?, ?)",
            data_klienti
        )

    conn.commit()
    conn.close()

# Spustí inicializaci databáze
init_db()

# ===== Streamlit aplikace =====
st.set_page_config(page_title="Půjčovna strojů", layout="wide", page_icon="🚜")

st.title("🚜 Půjčovna stavebních strojů")

# Načíst data
conn = sqlite3.connect(DB_PATH)
stroje = pd.read_sql("SELECT * FROM stroje", conn)
klienti = pd.read_sql("SELECT * FROM klienti", conn)
conn.close()

# Boční menu
menu = st.sidebar.radio("Menu", ["Formulář", "Seznam strojů", "Seznam klientů"])

if menu == "Formulář":
    st.header("Výpočet půjčovného")

    klient = st.selectbox("Vyberte klienta", klienti["nazev"])
    stroj = st.selectbox("Vyberte stroj", stroje["nazev"])
    dny = st.number_input("Počet dní", min_value=1, value=1)

    sleva = klienti.loc[klienti["nazev"] == klient, "sleva"].values[0]
    cena_den = stroje.loc[stroje["nazev"] == stroj, "cena_za_den"].values[0]
    dostupnost = stroje.loc[stroje["nazev"] == stroj, "dostupnost"].values[0]

    if dostupnost == 1:
        st.success("Stroj je dostupný ✅")
        celkem = dny * cena_den * (1 - sleva / 100)
        st.metric("Celková cena (po slevě)", f"{celkem:,.0f} Kč")
    else:
        st.error("Tento stroj momentálně není dostupný ❌")

elif menu == "Seznam strojů":
    st.header("Seznam strojů")
    st.dataframe(stroje)

elif menu == "Seznam klientů":
    st.header("Seznam klientů")
    st.dataframe(klienti)
