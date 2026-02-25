import sqlite3
from datetime import datetime
import requests
import sqlite3
from datetime import datetime

DB = 'fpl.db'

def db():
    return sqlite3.connect(DB)

def veri_guncelle():
    print("Veri güncelleniyor...")
    conn = db()
    c = conn.cursor()

    # Tablolar
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY, first_name TEXT, second_name TEXT,
        web_name TEXT, team INTEGER, element_type INTEGER,
        now_cost INTEGER, total_points INTEGER, form REAL,
        points_per_game REAL, selected_by_percent REAL, minutes INTEGER,
        goals_scored INTEGER, assists INTEGER, clean_sheets INTEGER,
        yellow_cards INTEGER, red_cards INTEGER, bonus INTEGER,
        expected_goals REAL, expected_assists REAL,
        chance_of_playing_next_round INTEGER, status TEXT, news TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY, name TEXT, short_name TEXT,
        strength INTEGER, strength_attack_home INTEGER,
        strength_attack_away INTEGER, strength_defence_home INTEGER,
        strength_defence_away INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS fixtures (
        id INTEGER PRIMARY KEY, gameweek INTEGER,
        home_team INTEGER, away_team INTEGER,
        home_difficulty INTEGER, away_difficulty INTEGER,
        finished INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS gameweek_history (
        player_id INTEGER, gameweek INTEGER, minutes INTEGER,
        goals_scored INTEGER, assists INTEGER, clean_sheets INTEGER,
        bonus INTEGER, yellow_cards INTEGER, red_cards INTEGER,
        total_points INTEGER, was_home INTEGER, opponent_team INTEGER,
        PRIMARY KEY (player_id, gameweek)
    )''')
    conn.commit()

    # Oyuncular ve takımlar
    data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
    for p in data['elements']:
        c.execute('INSERT OR REPLACE INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
            p['id'], p['first_name'], p['second_name'], p['web_name'],
            p['team'], p['element_type'], p['now_cost'], p['total_points'],
            float(p['form']), float(p['points_per_game']),
            float(p['selected_by_percent']), p['minutes'],
            p['goals_scored'], p['assists'], p['clean_sheets'],
            p['yellow_cards'], p['red_cards'], p['bonus'],
            float(p['expected_goals']), float(p['expected_assists']),
            p['chance_of_playing_next_round'], p['status'], p['news']
        ))
    for t in data['teams']:
        c.execute('INSERT OR REPLACE INTO teams VALUES (?,?,?,?,?,?,?,?)', (
            t['id'], t['name'], t['short_name'], t['strength'],
            t['strength_attack_home'], t['strength_attack_away'],
            t['strength_defence_home'], t['strength_defence_away']
        ))
    print(f"Oyuncular güncellendi: {len(data['elements'])}")

    # Fikstürler
    fixtures = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
    for f in fixtures:
        c.execute('INSERT OR REPLACE INTO fixtures VALUES (?,?,?,?,?,?,?)', (
            f['id'], f['event'], f['team_h'], f['team_a'],
            f['team_h_difficulty'], f['team_a_difficulty'], f['finished']
        ))
    print(f"Fikstürler güncellendi: {len(fixtures)}")

    # Haftalık geçmiş
    c.execute('SELECT id FROM players')
    player_ids = [row[0] for row in c.fetchall()]
    for i, pid in enumerate(player_ids):
        data = requests.get(f"https://fantasy.premierleague.com/api/element-summary/{pid}/").json()
        for gw in data['history']:
            c.execute('INSERT OR REPLACE INTO gameweek_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (
                pid, gw['round'], gw['minutes'],
                gw['goals_scored'], gw['assists'], gw['clean_sheets'],
                gw['bonus'], gw['yellow_cards'], gw['red_cards'],
                gw['total_points'], gw['was_home'], gw['opponent_team']
            ))
        if i % 100 == 0:
            conn.commit()
            print(f"{i}/{len(player_ids)} oyuncu...")

    conn.commit()
    conn.close()
    print("Veri güncelleme tamamlandı.")

# ÇALIŞTIR
veri_guncelle()

conn = sqlite3.connect('fpl.db')
c = conn.cursor()

c.execute('SELECT MAX(gameweek) FROM gameweek_history')
son_gw = c.fetchone()[0]
current_gw = son_gw + 1

# AL LİSTESİ
c.execute(f'''
SELECT p.web_name, t.short_name,
       CASE p.element_type WHEN 1 THEN 'KAL' WHEN 2 THEN 'DEF' WHEN 3 THEN 'ORT' WHEN 4 THEN 'FOR' END as mevki,
       ROUND(AVG(gh.total_points), 2) as son5_ort,
       p.now_cost,
       ROUND(AVG(CASE WHEN f.home_team = t.id THEN f.home_difficulty ELSE f.away_difficulty END), 2) as fikstür
FROM gameweek_history gh
JOIN players p ON p.id = gh.player_id
JOIN teams t ON t.id = p.team
JOIN fixtures f ON (f.home_team = t.id OR f.away_team = t.id)
WHERE gh.gameweek BETWEEN {son_gw-4} AND {son_gw}
AND f.gameweek BETWEEN {current_gw} AND {current_gw+2}
AND f.finished = 0
AND gh.minutes > 45
AND p.status = 'a'
GROUP BY gh.player_id
HAVING COUNT(*) >= 3 AND son5_ort >= 5.0
ORDER BY son5_ort DESC, fikstür ASC
LIMIT 6
''')
al_listesi = c.fetchall()

# SAT LİSTESİ
c.execute(f'''
SELECT p.web_name, t.short_name,
       CASE p.element_type WHEN 1 THEN 'KAL' WHEN 2 THEN 'DEF' WHEN 3 THEN 'ORT' WHEN 4 THEN 'FOR' END as mevki,
       ROUND(AVG(gh.total_points), 2) as son5_ort,
       p.now_cost,
       ROUND(AVG(CASE WHEN f.home_team = t.id THEN f.home_difficulty ELSE f.away_difficulty END), 2) as fikstür
FROM gameweek_history gh
JOIN players p ON p.id = gh.player_id
JOIN teams t ON t.id = p.team
JOIN fixtures f ON (f.home_team = t.id OR f.away_team = t.id)
WHERE gh.gameweek BETWEEN {son_gw-4} AND {son_gw}
AND f.gameweek BETWEEN {current_gw} AND {current_gw+2}
AND f.finished = 0
AND p.total_points > 60
AND gh.minutes > 45
GROUP BY gh.player_id
HAVING COUNT(*) >= 3 AND (son5_ort < 4.0 OR fikstür >= 4.0)
ORDER BY son5_ort ASC, fikstür DESC
LIMIT 4
''')
sat_listesi = c.fetchall()

# KAPTAN ÖNERİSİ
c.execute(f'''
SELECT p.web_name, t.short_name,
       ROUND(AVG(gh.total_points), 2) as son5_ort,
       p.now_cost,
       CASE WHEN f.home_team = t.id THEN 'Ev' ELSE 'Dep' END as konum,
       CASE WHEN f.home_team = t.id THEN f.home_difficulty ELSE f.away_difficulty END as zorluk,
       ROUND(AVG(gh.total_points) * (5.0 - CASE WHEN f.home_team = t.id THEN f.home_difficulty ELSE f.away_difficulty END) *
             CASE WHEN f.home_team = t.id THEN 1.1 ELSE 1.0 END, 2) as skor
FROM gameweek_history gh
JOIN players p ON p.id = gh.player_id
JOIN teams t ON t.id = p.team
JOIN fixtures f ON (f.home_team = t.id OR f.away_team = t.id)
WHERE gh.gameweek BETWEEN {son_gw-4} AND {son_gw}
AND f.gameweek = {current_gw}
AND f.finished = 0
AND gh.minutes > 45
AND p.status = 'a'
AND p.element_type IN (3,4)
GROUP BY gh.player_id
HAVING COUNT(*) >= 3
ORDER BY skor DESC
LIMIT 1
''')
kaptan = c.fetchone()

# SAKATLIK UYARILARI
c.execute('''
SELECT p.web_name, t.short_name, p.status, p.news, p.chance_of_playing_next_round
FROM players p
JOIN teams t ON p.team = t.id
WHERE p.status != 'a' AND p.total_points > 50
ORDER BY p.total_points DESC
LIMIT 5
''')
uyarilar = c.fetchall()

conn.close()

# YARDIMCI FONKSİYONLAR
def fikstür_renk(f):
    if f <= 2.5: return "#00ff87"
    if f <= 3.5: return "#f0c040"
    return "#ff6b6b"

def durum_emoji(s):
    return "🔴" if s in ['i','d'] else "🟡"

# AL KARTLARI
al_cards = ""
for p in al_listesi:
    renk = fikstür_renk(p[5])
    al_cards += f'''
    <div class="card">
        <div class="tag al">▲ AL</div>
        <h3>{p[0]}</h3>
        <div class="takim">{p[1]} — {p[2]} — £{p[4]/10}m</div>
        <div class="stats">
            <div class="stat"><div class="val">{p[3]}</div><div class="lbl">5H Ort</div></div>
            <div class="stat"><div class="val" style="color:{renk}">{p[5]}</div><div class="lbl">Fikstür</div></div>
        </div>
    </div>'''

# SAT KARTLARI
sat_cards = ""
for p in sat_listesi:
    renk = fikstür_renk(p[5])
    sat_cards += f'''
    <div class="card">
        <div class="tag sat">▼ SAT</div>
        <h3>{p[0]}</h3>
        <div class="takim">{p[1]} — {p[2]} — £{p[4]/10}m</div>
        <div class="stats">
            <div class="stat"><div class="val">{p[3]}</div><div class="lbl">5H Ort</div></div>
            <div class="stat"><div class="val" style="color:{renk}">{p[5]}</div><div class="lbl">Fikstür</div></div>
        </div>
    </div>'''

# KAPTAN KARTI
kaptan_card = ""
if kaptan:
    kaptan_card = f'''
    <div class="card kaptan-card">
        <div class="tag kaptan">★ KAPTAN ÖNERİSİ</div>
        <h3>{kaptan[0]}</h3>
        <div class="takim">{kaptan[1]} — £{kaptan[3]/10}m — {kaptan[4]}</div>
        <div class="stats">
            <div class="stat"><div class="val">{kaptan[2]}</div><div class="lbl">5H Ort</div></div>
            <div class="stat"><div class="val">{kaptan[5]}</div><div class="lbl">Zorluk</div></div>
            <div class="stat"><div class="val">{kaptan[6]}</div><div class="lbl">Skor</div></div>
        </div>
    </div>'''

# UYARI SATIRLARI
uyari_rows = ""
for u in uyarilar:
    emoji = durum_emoji(u[2])
    yuzde = f"%{u[4]}" if u[4] is not None else "?"
    haber = u[3][:90] + "..." if u[3] and len(u[3]) > 90 else (u[3] or "Detay yok")
    uyari_rows += f'<div class="uyari kirmizi">{emoji} <strong>{u[0]} ({u[1]})</strong> — {yuzde} forma giyme ihtimali — {haber}</div>'

# HTML
html = f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FPL Analiz — Hafta {current_gw}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; }}
  header {{ background: #38003c; padding: 24px 32px; display: flex; justify-content: space-between; align-items: center; }}
  header h1 {{ font-size: 22px; color: #fff; letter-spacing: 1px; }}
  header span {{ background: #00ff87; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; }}
  .container {{ max-width: 960px; margin: 32px auto; padding: 0 20px; }}
  .section-title {{ font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #8b949e; margin-bottom: 16px; margin-top: 36px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
  .card {{ background: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; }}
  .kaptan-card {{ border-color: #f0c040; }}
  .tag {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
  .tag.al {{ color: #00ff87; }}
  .tag.sat {{ color: #ff6b6b; }}
  .tag.kaptan {{ color: #f0c040; }}
  h3 {{ font-size: 18px; margin-bottom: 4px; }}
  .takim {{ font-size: 13px; color: #8b949e; margin-bottom: 12px; }}
  .stats {{ display: flex; gap: 16px; }}
  .stat {{ text-align: center; }}
  .stat .val {{ font-size: 20px; font-weight: 700; color: #fff; }}
  .stat .lbl {{ font-size: 11px; color: #8b949e; margin-top: 2px; }}
  .uyari-list {{ display: flex; flex-direction: column; gap: 10px; }}
  .uyari {{ background: #161b22; border-radius: 10px; padding: 14px 18px; font-size: 14px; border-left: 3px solid #f0c040; }}
  .uyari.kirmizi {{ border-left-color: #ff6b6b; }}
  footer {{ text-align: center; padding: 40px; color: #8b949e; font-size: 13px; margin-top: 40px; border-top: 1px solid #30363d; }}
</style>
</head>
<body>
<header>
  <h1>⚽ FPL ANALİZ</h1>
  <span>HAFTA {current_gw}</span>
</header>
<div class="container">

  <p class="section-title">★ Kaptan Önerisi</p>
  <div class="cards">{kaptan_card}</div>

  <p class="section-title">▲ Bu Hafta Al</p>
  <div class="cards">{al_cards}</div>

  <p class="section-title">▼ Bu Hafta Sat</p>
  <div class="cards">{sat_cards}</div>

  <p class="section-title">⚠ Sakatlık & Uyarılar</p>
  <div class="uyari-list">{uyari_rows}</div>

</div>
<footer>FPL Analiz — Haftalık otomatik rapor · Hafta {current_gw} · {datetime.now().strftime("%d.%m.%Y")}</footer>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Rapor oluşturuldu: rapor_hafta_{current_gw}.html")