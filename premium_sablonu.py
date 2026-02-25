from datetime import datetime

def premium_html_olustur(current_gw, kaptan_card, al_cards, sat_cards, uyari_rows, tahmin_rows, hafta_basliklari, fikstür_satirlar):
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FPL Analiz Premium — Hafta {current_gw}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; }}
  header {{ background: #38003c; padding: 24px 32px; display: flex; justify-content: space-between; align-items: center; }}
  header h1 {{ font-size: 22px; color: #fff; letter-spacing: 1px; }}
  .badge-premium {{ background: #f0c040; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; }}
  .badge-hafta {{ background: #00ff87; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; }}
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
  table {{ width: 100%; border-collapse: separate; border-spacing: 4px; }}
  .tablo-kapsayici {{ background: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; overflow-x: auto; }}
  footer {{ text-align: center; padding: 40px; color: #8b949e; font-size: 13px; margin-top: 40px; border-top: 1px solid #30363d; }}
</style>
</head>
<body>
<header>
  <h1>⚽ FPL ANALİZ</h1>
  <div style="display:flex;gap:8px">
    <span class="badge-premium">★ PREMIUM</span>
    <span class="badge-hafta">HAFTA {current_gw}</span>
  </div>
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

  <p class="section-title">📊 Gelecek Hafta Puan Tahminleri</p>
  <div class="tablo-kapsayici">
    <table>
      <thead>
        <tr>
          <th style="padding:10px;text-align:left;color:#8b949e">Oyuncu</th>
          <th style="padding:10px;color:#8b949e">Takım</th>
          <th style="padding:10px;color:#8b949e">Mevki</th>
          <th style="padding:10px;color:#8b949e">5H Ort</th>
          <th style="padding:10px;color:#8b949e">Zorluk</th>
          <th style="padding:10px;color:#8b949e">Tahmin</th>
        </tr>
      </thead>
      <tbody>{tahmin_rows}</tbody>
    </table>
  </div>

  <p class="section-title">📅 5 Haftalık Fikstür Takvimi</p>
  <div class="tablo-kapsayici">
    <table>
      <thead>
        <tr>
          <th style="padding:8px;text-align:left;color:#8b949e">Takım</th>
          {hafta_basliklari}
        </tr>
      </thead>
      <tbody>{fikstür_satirlar}</tbody>
    </table>
  </div>

</div>
<footer>FPL Analiz Premium — Hafta {current_gw} · {datetime.now().strftime("%d.%m.%Y")}</footer>
</body>
</html>"""