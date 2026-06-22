"""
build.py — regenerates fall2026tourneymap.html from the tourneydatabase MySQL instance.
Run this whenever tournament or organizer data changes.
"""

import json
import subprocess
import sys
from collections import defaultdict
from datetime import date

import mysql.connector

DB = dict(
    host='34.45.11.139', port=3306,
    user='LBDtbd', password='APIG!9bPG',
    database='tourneydatabase', ssl_disabled=False
)

ORG_CODES = {
    'Perfect Game':         'pg',
    'USSSA':                'usssa',
    'Triple Crown Sports':  'tc',
    'Gametime Tournaments': 'gt',
    'Genesis Sports Complex':'gsc',
    'KC Sports':            'kcs',
    'Sports America':       'sa',
}

ORG_META = {
    'pg':    {'label': 'Perfect Game',         'color': '#1F3A5F'},
    'usssa': {'label': 'USSSA',                'color': '#BC5B39'},
    'tc':    {'label': 'Triple Crown Sports',  'color': '#2F6F4E'},
    'gt':    {'label': 'Gametime Tournaments', 'color': '#EAB308'},
    'gsc':   {'label': 'Genesis Sports Complex','color': '#EA580C'},
    'kcs':   {'label': 'KC Sports',            'color': '#7C3AED'},
    'sa':    {'label': 'Sports America',       'color': '#0891B2'},
}

MONTHS = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTH_ABBR = {8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}


def fetch_events(cur):
    cur.execute("""
        SELECT t.name, o.name, t.city, t.state,
               t.start_date, t.end_date, t.link, t.lat, t.lng
        FROM tournaments t
        JOIN organizers o ON t.organizer_id = o.id
        WHERE t.start_age <= 14 AND t.end_age >= 14
          AND MONTH(t.start_date) BETWEEN 8 AND 12
        ORDER BY t.start_date
    """)
    events = []
    for name, org_name, city, state, start, end, link, lat, lng in cur.fetchall():
        org = ORG_CODES[org_name]
        month = MONTH_ABBR[start.month]
        fmt = '%b %#d' if sys.platform == 'win32' else '%b %-d'
        if start == end:
            dates = f"{start.strftime(fmt)}, {start.year}"
        else:
            if start.month == end.month:
                dates = f"{start.strftime(fmt)}–{end.day}, {end.year}"
            else:
                dates = f"{start.strftime(fmt)}–{end.strftime(fmt)}, {end.year}"
        events.append({
            'org': org, 'month': month, 'name': name,
            'city': city, 'state': state, 'dates': dates,
            'link': link, 'lat': float(lat), 'lng': float(lng),
        })
    return events


def build_html(events):
    org_counts = defaultdict(int)
    month_counts = defaultdict(int)
    for e in events:
        org_counts[e['org']] += 1
        month_counts[e['month']] += 1

    total = len(events)
    start_years = {e['dates'].split(', ')[-1] for e in events}
    year = sorted(start_years)[0]

    events_js = json.dumps(events, indent=2)

    org_chips = '\n      '.join(
        f'<div class="chip" data-org="{code}"><span class="dot"></span>'
        f'{ORG_META[code]["label"]} <span class="count">({org_counts[code]})</span></div>'
        for code in ['pg', 'usssa', 'tc', 'gt', 'gsc', 'kcs', 'sa'] if org_counts[code]
    )

    month_chips = '\n        '.join(
        f'<div class="chip" data-month="{m}">{m} <span class="count">({month_counts[m]})</span></div>'
        for m in MONTHS if month_counts[m]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>14U Fall {year} — Aug–Dec {year}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css" />
<style>
  :root{{
    --cream:#F6F1E6;
    --paper:#FFFDF8;
    --ink:#162338;
    --ink-soft:#4A5568;
    --navy:#1F3A5F;
    --clay:#BC5B39;
    --grass:#2F6F4E;
    --gold:#D7A23B;
    --yellow:#EAB308;
    --orange:#EA580C;
    --line:#E3DBC8;
  }}
  *{{box-sizing:border-box;}}
  html,body{{
    margin:0; padding:0; height:100%;
    background:var(--cream);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    color:var(--ink);
  }}
  .app{{ display:flex; flex-direction:column; height:100vh; }}
  header{{
    background:var(--paper);
    border-bottom:2px solid var(--ink);
    padding:14px 22px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:18px;
    flex-wrap:wrap;
    z-index:1000;
  }}
  .brand{{ display:flex; align-items:center; gap:12px; }}
  .brand svg{{ flex:0 0 auto; }}
  .brand h1{{
    font-family:Georgia,"Times New Roman",serif;
    font-size:22px;
    font-weight:700;
    letter-spacing:0.2px;
    margin:0;
    line-height:1.1;
  }}
  .brand p{{
    margin:2px 0 0;
    font-size:12.5px;
    color:var(--ink-soft);
    letter-spacing:0.3px;
  }}
  .filters{{ display:flex; flex-direction:column; gap:6px; align-items:flex-end; }}
  .legend{{ display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }}
  .chip{{
    display:flex; align-items:center; gap:7px;
    background:var(--paper);
    border:1.5px solid var(--ink);
    border-radius:999px;
    padding:6px 12px 6px 9px;
    font-size:12.5px;
    font-weight:600;
    cursor:pointer;
    user-select:none;
    transition:all .15s ease;
  }}
  .chip:hover{{ transform:translateY(-1px); box-shadow:0 2px 6px rgba(22,35,56,0.15); }}
  .chip.off{{ opacity:0.4; }}
  .chip .dot{{ width:11px; height:11px; border-radius:50%; border:1.5px solid rgba(0,0,0,0.25); }}
  .chip[data-org="pg"] .dot{{ background:var(--navy); }}
  .chip[data-org="usssa"] .dot{{ background:var(--clay); }}
  .chip[data-org="tc"] .dot{{ background:var(--grass); }}
  .chip[data-org="gt"] .dot{{ background:var(--yellow); }}
  .chip[data-org="gsc"] .dot{{ background:var(--orange); }}
  .chip[data-org="kcs"] .dot{{ background:#7C3AED; }}
  .chip[data-org="sa"] .dot{{ background:#0891B2; }}
  .chip .count{{ color:var(--ink-soft); font-weight:400; }}
  .chip[data-month]{{ padding:5px 11px; font-size:12px; }}
  #map{{ flex:1 1 auto; width:100%; background:#E8E2D2; }}
  .leaflet-tooltip.tourney-tip{{
    background:var(--paper);
    border:none;
    border-radius:10px;
    box-shadow:0 6px 18px rgba(22,35,56,0.25);
    padding:0;
    opacity:1 !important;
  }}
  .leaflet-tooltip.tourney-tip::before{{ display:none; }}
  .tip-card{{
    border-left:5px solid var(--ink);
    border-radius:10px;
    padding:10px 14px 10px 11px;
    min-width:200px;
    max-width:240px;
  }}
  .tip-card .org{{ font-size:10px; text-transform:uppercase; letter-spacing:0.8px; font-weight:700; color:var(--ink-soft); margin-bottom:3px; }}
  .tip-card .name{{ font-family:Georgia,serif; font-size:14.5px; font-weight:700; line-height:1.25; margin-bottom:5px; }}
  .tip-card .loc{{ font-size:12px; color:var(--ink); margin-bottom:2px; }}
  .tip-card .date{{ font-size:11.5px; font-family:"SFMono-Regular",Menlo,Consolas,monospace; color:var(--ink-soft); margin-bottom:6px; }}
  .tip-card .cta{{ font-size:10.5px; font-weight:600; color:var(--gold); letter-spacing:0.2px; }}
  .marker-pin{{
    width:16px; height:16px;
    border-radius:50%;
    border:2px solid var(--paper);
    box-shadow:0 1px 4px rgba(0,0,0,0.4);
    cursor:pointer;
    transition:transform .12s ease;
  }}
  .marker-pin:hover{{ transform:scale(1.35); }}
  .cluster-icon{{
    display:flex; align-items:center; justify-content:center;
    border-radius:50%;
    color:#fff;
    font-weight:700;
    font-size:12.5px;
    border:2px solid var(--paper);
    box-shadow:0 1px 5px rgba(0,0,0,0.4);
  }}
  @media (max-width: 640px){{
    header{{ padding:10px 14px; }}
    .brand h1{{ font-size:18px; }}
    .brand p{{ display:none; }}
    .chip{{ font-size:11px; padding:5px 10px 5px 8px; }}
    .chip[data-month]{{ font-size:11px; padding:4px 9px; }}
  }}
</style>
</head>
<body>
<div class="app">
  <header>
    <div class="brand">
      <svg width="34" height="34" viewBox="0 0 34 34" fill="none">
        <circle cx="17" cy="17" r="15" fill="#FFFDF8" stroke="#162338" stroke-width="2"/>
        <path d="M6 11 C12 15, 12 19, 6 23" stroke="#BC5B39" stroke-width="1.4" fill="none" stroke-dasharray="2.2 2"/>
        <path d="M28 11 C22 15, 22 19, 28 23" stroke="#BC5B39" stroke-width="1.4" fill="none" stroke-dasharray="2.2 2"/>
      </svg>
      <div>
        <h1>14U Fall {year}</h1>
        <p>Aug – Dec {year} &nbsp;&middot;&nbsp; <span id="visibleCount">{total}</span> tournaments</p>
      </div>
    </div>
    <div class="filters">
      <div class="legend" id="legend">
      {org_chips}
      </div>
      <div class="legend" id="monthLegend">
        {month_chips}
      </div>
    </div>
  </header>
  <div id="map"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js"></script>
<script>
const ORG_META = {json.dumps(ORG_META, indent=2)};

const events = {events_js};

const map = L.map('map', {{ scrollWheelZoom: true, zoomControl: true }}).setView([37.8, -96], 4);

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  maxZoom: 19,
  subdomains: 'abcd'
}}).addTo(map);

function makeClusterIcon(color){{
  return function(cluster){{
    const count = cluster.getChildCount();
    const size = count < 6 ? 32 : count < 14 ? 38 : 46;
    return L.divIcon({{
      html: `<div class="cluster-icon" style="width:${{size}}px;height:${{size}}px;background:${{color}};">${{count}}</div>`,
      className: '',
      iconSize: [size, size]
    }});
  }};
}}

const clusterGroups = {{}};
Object.keys(ORG_META).forEach(org => {{
  clusterGroups[org] = L.markerClusterGroup({{
    iconCreateFunction: makeClusterIcon(ORG_META[org].color),
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    maxClusterRadius: 40
  }});
  map.addLayer(clusterGroups[org]);
}});

const allMarkers = events.map(ev => {{
  const color = ORG_META[ev.org].color;
  const icon = L.divIcon({{
    className: '',
    html: `<div class="marker-pin" style="background:${{color}};"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  }});
  const marker = L.marker([ev.lat, ev.lng], {{ icon }});
  const tipHtml = `
    <div class="tip-card" style="border-left-color:${{color}};">
      <div class="org">${{ORG_META[ev.org].label}}</div>
      <div class="name">${{ev.name}}</div>
      <div class="loc">${{ev.city}}, ${{ev.state}}</div>
      <div class="date">${{ev.dates}}</div>
      <div class="cta">Click pin to open event page ↗</div>
    </div>`;
  marker.bindTooltip(tipHtml, {{ direction: 'top', offset: [0, -10], className: 'tourney-tip', sticky: true }});
  marker.on('click', () => window.open(ev.link, '_blank', 'noopener,noreferrer'));
  return marker;
}});

const bounds = L.featureGroup(allMarkers).getBounds();
map.fitBounds(bounds, {{ padding: [50, 50] }});

const activeOrgs   = new Set(Object.keys(ORG_META));
const activeMonths = new Set({json.dumps(MONTHS)});

function rebuildMarkers(){{
  Object.values(clusterGroups).forEach(g => g.clearLayers());
  let count = 0;
  events.forEach((ev, i) => {{
    if (activeOrgs.has(ev.org) && activeMonths.has(ev.month)) {{
      clusterGroups[ev.org].addLayer(allMarkers[i]);
      count++;
    }}
  }});
  document.getElementById('visibleCount').textContent = count;
}}

rebuildMarkers();

document.querySelectorAll('.chip[data-org]').forEach(chip => {{
  chip.addEventListener('click', () => {{
    const org = chip.dataset.org;
    if (activeOrgs.has(org)) {{ activeOrgs.delete(org); chip.classList.add('off'); }}
    else                      {{ activeOrgs.add(org);    chip.classList.remove('off'); }}
    rebuildMarkers();
  }});
}});

document.querySelectorAll('.chip[data-month]').forEach(chip => {{
  chip.addEventListener('click', () => {{
    const month = chip.dataset.month;
    if (activeMonths.has(month)) {{ activeMonths.delete(month); chip.classList.add('off'); }}
    else                         {{ activeMonths.add(month);    chip.classList.remove('off'); }}
    rebuildMarkers();
  }});
}});
</script>
</body>
</html>"""


def main():
    conn = mysql.connector.connect(**DB)
    cur = conn.cursor()
    events = fetch_events(cur)
    cur.close()
    conn.close()

    html = build_html(events)

    out = 'fall2026tourneymap.html'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written {out} ({len(events)} tournaments)')

    result = subprocess.run(
        ['git', 'diff', '--stat', out],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(result.stdout)
        answer = input('Commit and push? [y/N] ').strip().lower()
        if answer == 'y':
            subprocess.run(['git', 'add', out], check=True)
            subprocess.run(['git', 'commit', '-m', 'Rebuild map from database'], check=True)
            subprocess.run(['git', 'push'], check=True)
            print('Pushed.')
    else:
        print('No changes to HTML.')


if __name__ == '__main__':
    main()
