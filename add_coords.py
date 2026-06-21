import mysql.connector

conn = mysql.connector.connect(
    host='34.45.11.139', port=3306,
    user='LBDtbd', password='APIG!9bPG',
    database='tourneydatabase', ssl_disabled=False
)
cur = conn.cursor()

cur.execute('ALTER TABLE tournaments ADD COLUMN lat DECIMAL(9,6), ADD COLUMN lng DECIMAL(9,6)')

coords = [
    ('2026 14U PG WWBA World Championship (Major)', 26.7153, -80.0534),
    ('2026 PG 14U BCS World Championship', 28.8028, -81.2731),
    ('2026 14U PG Northeast Champions Cup', 40.5795, -74.1502),
    ("2026 14U (Open) PG Florida Champion's Cup", 28.8028, -81.2731),
    ('2026 14U (Major) National All-State Select Championship', 30.0972, -95.6161),
    ('KENTUCKY USSSA FALL STATE TOURNAMENT', 37.6975, -85.8591),
    ('Tennessee Fall State Championship', 36.5484, -82.5618),
    ('Fun On The Field (Fall State)', 34.3665, -89.5192),
    ('Nashville Belt Championship (USSSA Belts & Rings)', 36.3048, -86.6200),
    ('CIS Pink Out State', 41.5868, -93.6250),
    ('USSSA Fall State Championship', 33.3528, -111.7890),
    ('THE YARDS STATE CHAMPIONSHIP (BELTS & RINGS)', 31.2519, -89.8323),
    ('Clearwater Fall Championship (Bling Chains)', 27.9659, -82.8001),
    ('Panhandle State Championship', 30.4213, -87.2169),
    ('ULTIMATE TEXAS CHAMPIONSHIP (STATE RINGS)', 29.7858, -95.8244),
    ('METRO FALL STATE CHAMPIONSHIP (STATE RINGS)', 32.6518, -96.9083),
    ('West Coast State Championship', 27.4989, -82.5748),
    ('East Coast Florida State Championship', 28.2639, -80.7370),
    ('Houston Fall Championship (State Rings)', 29.7604, -95.3698),
    ('Winter Nationals: Toys for Tots - PAP', 30.2241, -92.0198),
    ('13th Annual Winter Blast', 36.1699, -115.1398),
    ('San Diego Summer Sizzle', 32.7157, -117.1611),
    ('Temecula Summer Special', 33.4936, -117.1484),
    ('San Diego Labor Day', 32.7157, -117.1611),
    ('Desert Midnight Madness', 33.7222, -116.3744),
    ('San Diego Classic', 32.7157, -117.1611),
    ('Temecula Fall Classic', 33.4936, -117.1484),
    ('Desert Fall Season Opener', 33.7222, -116.3744),
    ('San Diego September to Remember', 32.7157, -117.1611),
    ('Central Cal Oktoberfest', 36.8252, -119.7029),
    ('Fall Classic', 32.7157, -117.1611),
    ('San Clemente Showdown', 33.4270, -117.6120),
    ('Veterans Day', 32.7157, -117.1611),
    ('Central Cal Super Cup', 36.8252, -119.7029),
    ('Pre Thanksgiving', 33.4936, -117.1484),
    ('Central Cal Pre Thanksgiving', 36.8252, -119.7029),
    ('Desert Thanksgiving Qualifier', 33.7222, -116.3744),
    ('San Diego Thanksgiving', 32.7157, -117.1611),
    ('Central Cal Toy Drive', 36.8252, -119.7029),
    ('Ontario Sports Empire NIT', 34.0633, -117.6509),
]

for name, lat, lng in coords:
    cur.execute('UPDATE tournaments SET lat=%s, lng=%s WHERE name=%s', (lat, lng, name))

conn.commit()
cur.execute('SELECT COUNT(*) FROM tournaments WHERE lat IS NOT NULL')
print(f'Rows with coords: {cur.fetchone()[0]}')
cur.close()
conn.close()
