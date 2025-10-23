import os
import csv
import time
import random
import hashlib
import sqlite3
import urllib.parse
import pandas as pd
from datetime import datetime, date, time as dtime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# ===== Selenium =====
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= Config =================
load_dotenv()

# Fonte de dados
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL", "").strip()
CSV_PATH      = os.getenv("CSV_PATH", "").strip()

# Execução/driver
DELAY_BETWEEN   = float(os.getenv("DELAY_BETWEEN", "10"))
TIMEOUT_OPEN    = float(os.getenv("TIMEOUT_OPEN", "40"))
HEADLESS        = os.getenv("HEADLESS", "false").lower() == "true"
PROFILE_DIR     = os.path.abspath(os.getenv("PROFILE_DIR", "./chrome_profile"))
WINDOW_MIN      = int(os.getenv("WINDOW_MINUTES", "15"))
TIMEZONE        = os.getenv("TIMEZONE", "America/Sao_Paulo")

# Regra de envio (slots por atraso)
def _parse_slots(var, default_list):
    raw = os.getenv(var, "")
    if not raw:
        return default_list
    out = []
    for token in raw.split(","):
        token = token.strip()
        if not token: 
            continue
        hh, mm = token.split(":")
        out.append(dtime(int(hh), int(mm)))
    return out

SLOTS_1_10  = _parse_slots("SLOTS_1_10",  [dtime(9,0)])
SLOTS_11_20 = _parse_slots("SLOTS_11_20", [dtime(9,0), dtime(13,0), dtime(18,0)])
SLOTS_21_30 = _parse_slots("SLOTS_21_30", [dtime(9,0), dtime(12,0), dtime(15,0), dtime(18,0)])
SLOTS_GT_30 = _parse_slots("SLOTS_GT_30", [dtime(8,0), dtime(11,0), dtime(14,0), dtime(17,0), dtime(20,0)])

# Filtros
SEND_ONLY_OD  = os.getenv("SEND_ONLY_IF_OVERDUE", "true").lower() == "true"

# Logs
LOG_PATH      = os.path.abspath(os.getenv("LOG_PATH", "registro_de_envios.csv"))
DB_PATH       = os.path.abspath(os.getenv("DB_PATH", "send_log.db"))

# Util
TZ = ZoneInfo(TIMEZONE)

# ================= Utils =================
def now_tz():
    return datetime.now(TZ)

def normalize_phone_br(raw: str) -> str:
    if raw is None: return ""
    v = "".join(ch for ch in str(raw) if ch.isdigit())
    v = v.lstrip("0")
    if not v.startswith("55"):
        v = "55" + v
    return v if 12 <= len(v) <= 13 else ""

def load_data() -> pd.DataFrame:
    if SHEET_CSV_URL:
        print("[info] Lendo CSV online (Sheets)…")
        return pd.read_csv(SHEET_CSV_URL)
    if CSV_PATH:
        print(f"[info] Lendo CSV local: {CSV_PATH}")
        return pd.read_csv(CSV_PATH)
    raise RuntimeError("Defina SHEET_CSV_URL (export do Sheets) ou CSV_PATH no .env")

def append_csv_log(nome, telefone, dias, status, detalhe):
    header_exists = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if not header_exists:
            w.writerow(["timestamp","nome","telefone","dias_em_atraso","status","detalhe"])
        w.writerow([now_tz().strftime("%Y-%m-%d %H:%M:%S"), nome, telefone, dias, status, detalhe])

def msg_hash(telefone: str, mensagem: str) -> str:
    return hashlib.sha256(f"{telefone}::{mensagem or ''}".encode("utf-8")).hexdigest()

def format_ddmmyyyy(dt: date) -> str:
    return dt.strftime("%d/%m/%Y")

def compute_dias_atraso(venc_field) -> int|None:
    if pd.isna(venc_field) or str(venc_field).strip() == "":
        return None
    s = str(venc_field).strip()
    try:
        if "/" in s:
            d = datetime.strptime(s, "%d/%m/%Y").date()
        else:
            d = datetime.fromisoformat(s).date()
    except Exception:
        try:
            d = pd.to_datetime(venc_field).date()
        except Exception:
            return None
    diff = (now_tz().date() - d).days
    return max(0, diff)

def msg_template(nome: str, venc: date|None, dias: int) -> str:
    trat = f"Sr(a) {nome}, " if nome else ""
    p1 = f"Olá {trat}identificamos que sua fatura"
    p2 = f" com vencimento em {format_ddmmyyyy(venc)}" if venc else ""
    p3 = f" já se encontra com {dias} {'dia' if dias==1 else 'dias'} em atraso." if dias is not None else ""
    return (p1 + p2 + p3).strip()

def wa_url(phone: str, msg: str) -> str:
    return f"https://wa.me/{phone}?text={urllib.parse.quote(msg or '')}"

# ============== Régua de envio ==============
def slots_for_days(dias: int) -> list[dtime]:
    if dias is None or dias <= 0:
        return []
    if 1 <= dias <= 10:
        return SLOTS_1_10
    if 11 <= dias <= 20:
        return SLOTS_11_20
    if 21 <= dias <= 30:
        return SLOTS_21_30
    return SLOTS_GT_30

def in_window(target: dtime) -> bool:
    n = now_tz()
    start = datetime.combine(n.date(), target, tzinfo=TZ) - timedelta(minutes=WINDOW_MIN)
    end   = datetime.combine(n.date(), target, tzinfo=TZ) + timedelta(minutes=WINDOW_MIN)
    return start <= n <= end

# ============== SQLite (controle diário) ==============
def db_init():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            d DATE NOT NULL,
            phone TEXT NOT NULL,
            slot TEXT NOT NULL,
            msg_hash TEXT NOT NULL,
            created_at DATETIME NOT NULL
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS ix_sent_d_phone_slot ON sent(d, phone, slot)")
    con.commit()
    con.close()

def already_sent_today(phone: str, slot_str: str, hash_: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM sent WHERE d=? AND phone=? AND slot=? AND msg_hash=? LIMIT 1",
                (now_tz().date().isoformat(), phone, slot_str, hash_))
    row = cur.fetchone()
    con.close()
    return row is not None

def mark_sent(phone: str, slot_str: str, hash_: str):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO sent(d, phone, slot, msg_hash, created_at) VALUES(?,?,?,?,?)",
                (now_tz().date().isoformat(), phone, slot_str, hash_, now_tz().isoformat()))
    con.commit()
    con.close()

# ============== Selenium (sessão única) ==============
def start_driver() -> webdriver.Chrome:
    chrome_opts = Options()
    if HEADLESS:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--start-maximized")
    chrome_opts.add_argument("--disable-notifications")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_opts)
    return driver

TEXTBOX_SELECTORS = [
    (By.XPATH, "//div[@contenteditable='true' and @data-tab='10']"),
    (By.XPATH, "//div[@contenteditable='true' and @data-tab='6']"),
    (By.XPATH, "//div[@contenteditable='true' and @role='textbox']"),
    (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']"),
    (By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']"),
]
SENDBTN_SELECTORS = [
    (By.XPATH, "//*[@data-icon='send']"),
    (By.XPATH, "//button[@aria-label='Send' or @aria-label='Enviar' or @aria-label='Enviar mensagem']"),
    (By.CSS_SELECTOR, "button[aria-label='Send'], button[aria-label='Enviar'], span[data-icon='send']"),
]

def open_and_send(driver: webdriver.Chrome, url: str, timeout: float) -> bool:
    driver.get(url)
    end = time.time() + timeout
    while time.time() < end:
        # enter
        for by, sel in TEXTBOX_SELECTORS:
            try:
                box = WebDriverWait(driver, 2).until(EC.presence_of_element_located((by, sel)))
                box.send_keys(Keys.ENTER)
                return True
            except Exception:
                pass
        # botão
        for by, sel in SENDBTN_SELECTORS:
            try:
                btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((by, sel)))
                btn.click()
                return True
            except Exception:
                pass
        time.sleep(0.5)
    return False

# ==================== Main ====================
def main():
    db_init()
    df = load_data()

    # Mapear colunas
    cols = {c.lower().strip(): c for c in df.columns}
    nome_col   = cols.get("nome")
    phone_col  = cols.get("telefone") or cols.get("numero")
    msg_col    = cols.get("mensagem")         # opcional (montamos se vazio)
    venc_col   = cols.get("vencimento")
    atraso_col = cols.get("dias em atraso") or cols.get("dias_em_atraso")

    if not phone_col:
        raise RuntimeError(f"Coluna de telefone não encontrada. Recebi: {list(df.columns)}")

    # Telefone e atraso
    df = df.copy()
    df["__telefone__"] = df[phone_col].astype(str).apply(normalize_phone_br)

    if atraso_col in df.columns:
        df["__dias__"] = pd.to_numeric(df[atraso_col], errors="coerce").fillna(0).astype(int)
    else:
        if not venc_col:
            raise RuntimeError("Sem 'dias em atraso' e sem 'vencimento' para calcular.")
        df["__dias__"] = df[venc_col].apply(compute_dias_atraso).fillna(0).astype(int)

    # Filtrar
    if SEND_ONLY_OD:
        df = df[df["__dias__"] >= 1]
    df = df[df["__telefone__"] != ""]

    if df.empty:
        print("[info] Nada para enviar agora.")
        return

    # Inicia o WhatsApp Web uma vez
    driver = start_driver()
    driver.get("https://web.whatsapp.com/")
    print("[info] Se for a primeira vez, escaneie o QR Code no WhatsApp Web.")
    time.sleep(10)  # tempo para login (primeira execução)

    total_try, total_ok, total_skip = 0, 0, 0
    print(f"[info] Agora: {now_tz().strftime('%Y-%m-%d %H:%M:%S %Z')} | janela ±{WINDOW_MIN} min")

    for i, row in df.iterrows():
        nome = str(row.get(nome_col, "")).strip() if nome_col else ""
        tel  = row["__telefone__"]
        dias = int(row["__dias__"])

        # slots de hoje pela régua
        slots = slots_for_days(dias)
        if not slots:
            total_skip += 1
            append_csv_log(nome, tel, dias, "skip", "sem slots p/ este atraso")
            continue

        # precisa estar dentro de um slot
        slot_to_fire = None
        for s in slots:
            if in_window(s):
                slot_to_fire = s
                break
        if not slot_to_fire:
            total_skip += 1
            append_csv_log(nome, tel, dias, "skip", "fora da janela de envio")
            continue

        # mensagem
        if msg_col and pd.notna(row.get(msg_col)):
            msg = str(row[msg_col])
        else:
            # tenta extrair vencimento para template
            venc = None
            if venc_col and pd.notna(row.get(venc_col)):
                try:
                    v = str(row.get(venc_col)).strip()
                    venc = datetime.strptime(v, "%d/%m/%Y").date() if "/" in v else pd.to_datetime(v).date()
                except Exception:
                    venc = None
            msg = msg_template(nome, venc, dias)

        url = wa_url(tel, msg)

        # deduplicação dia/slot/mensagem
        slot_str = slot_to_fire.strftime("%H:%M")
        h = msg_hash(tel, msg)
        if already_sent_today(tel, slot_str, h):
            total_skip += 1
            append_csv_log(nome, tel, dias, "dupe", f"já enviado hoje no slot {slot_str}")
            continue

        # enviar
        total_try += 1
        ok = open_and_send(driver, url, TIMEOUT_OPEN)
        if ok:
            mark_sent(tel, slot_str, h)
            total_ok += 1
            append_csv_log(nome, tel, dias, "ok", f"slot {slot_str}")
            print(f"[ok ] {tel} | {dias} dias | slot {slot_str}")
        else:
            append_csv_log(nome, tel, dias, "erro", f"timeout | slot {slot_str}")
            print(f"[err] {tel} | {dias} dias | slot {slot_str}")

        # intervalo com jitter
        jitter = random.uniform(-0.3, 0.3) * DELAY_BETWEEN
        time.sleep(max(2.0, DELAY_BETWEEN + jitter))

    print(f"[done] tentativas={total_try} ok={total_ok} skip={total_skip}")
    # driver.quit()  # opcional

if __name__ == "__main__":
    main()
