import openpyxl
import mysql.connector
from datetime import datetime

DB = dict(
    host='34.45.11.139', port=3306,
    user='LBDtbd', password='APIG!9bPG',
    database='tourneydatabase', ssl_disabled=False
)

CITY_COORDS = {
    ('Fenton/St. Peters', 'MO'): (38.5126, -90.4432),
    ('Fenton',            'MO'): (38.5126, -90.4432),
    ('Goddard',           'KS'): (37.6594, -97.5742),
}

TARGET_ORGS = {'Gametime Tournaments', 'Genesis Sports Complex'}

def parse_date(val):
    if isinstance(val, datetime):
        return val.date()
    for fmt in ('%b %d, %Y', '%B %d, %Y'):
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError(f'Cannot parse date: {val!r}')

wb = openpyxl.load_workbook(r'D:\GoogleDrive\TourneyDB\14UTourneysFall2026.xlsx')
ws = wb['Tournaments']

rows = [r for r in ws.iter_rows(values_only=True) if r[1] in TARGET_ORGS]

conn = mysql.connector.connect(**DB)
cur = conn.cursor()

cur.execute('SELECT id, name FROM organizers')
org_map = {name: oid for oid, name in cur.fetchall()}

inserted = 0
for name, org_name, city, state, start, end, start_age, end_age, link in rows:
    org_id = org_map[org_name]
    start_date = parse_date(start)
    end_date   = parse_date(end)
    lat, lng   = CITY_COORDS[(city, state)]
    cur.execute(
        '''INSERT INTO tournaments
           (name, organizer_id, city, state, start_date, end_date, start_age, end_age, link, lat, lng)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        (name, org_id, city, state, start_date, end_date,
         int(start_age), int(end_age), link, lat, lng)
    )
    inserted += 1

conn.commit()
print(f'Inserted {inserted} tournaments')
cur.execute('SELECT COUNT(*) FROM tournaments')
print(f'Total tournaments in DB: {cur.fetchone()[0]}')
cur.close()
conn.close()
