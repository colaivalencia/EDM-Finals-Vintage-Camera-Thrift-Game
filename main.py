import sqlite3
import random
import os
import datetime


def cls():
    os.system('clear' if os.name != 'nt' else 'cls')


def init_db(conn):
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            balance REAL DEFAULT 5000,
            day INTEGER DEFAULT 1,
            leica_bought INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price_min REAL,
            price_max REAL,
            is_film INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            name TEXT,
            price_paid REAL,
            cond TEXT,
            repair_cost REAL,
            sell_asis REAL,
            sell_fixed REAL,
            is_fixed INTEGER DEFAULT 0,
            is_sold INTEGER DEFAULT 0,
            day_bought INTEGER,
            is_film INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            day INTEGER,
            name TEXT,
            price REAL,
            bought INTEGER DEFAULT 0,
            is_film INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            type TEXT,
            amount REAL,
            balance_before REAL,
            balance_after REAL,
            note TEXT,
            created TEXT
        )
    ''')
     
    c.execute('SELECT count(*) FROM catalog')
    if c.fetchone()[0] == 0:
        items = [
            # FILM - cheap quick flips
            ('Colored Film Roll', 80, 200, 1),
            ('Black and White Film Roll', 150, 350, 1),
            # BUDGET
            ('Agfa Super Silette', 1000, 3000, 0),
            ('Zorki 4', 800, 2500, 0),
            # COMMON CAMERAS
            ('Canon AE-1', 1500, 3500, 0),
            ('Canon AE-1 Program', 1200, 3000, 0),
            ('Canon F-1N', 4000, 9000, 0),
            ('Canon T90', 3500, 8000, 0),
            ('Canon 7 Rangefinder', 3000, 7000, 0),
            ('Nikon FE', 1000, 2500, 0),
            ('Nikon FM', 1500, 3500, 0),
            ('Nikon FM2', 2500, 6000, 0),
            ('Nikon FE2', 2000, 4500, 0),
            ('Nikon F2 Photomic', 5500, 13000, 0),
            ('Nikon F3', 6000, 14000, 0),
            ('Minolta HiMatic', 800, 2000, 0),
            ('Minolta X-700', 1000, 2500, 0),
            ('Minolta X-570', 1500, 4000, 0),
            ('Olympus OM-1', 1500, 4000, 0),
            ('Olympus OM-2n', 1200, 3000, 0),
            ('Olympus OM-4T', 7000, 16000, 0),
            ('Olympus Trip 35', 1200, 3500, 0),
            ('Olympus XA2', 1000, 2500, 0),
            ('Pentax K1000', 800, 2000, 0),
            ('Pentax MX', 1500, 3500, 0),
            ('Pentax Spotmatic F', 1500, 4000, 0),
            ('Yashica Mat 124G', 4000, 9000, 0),
            ('Yashica Electro 35', 800, 2000, 0),
            ('Yashica T4', 5000, 12000, 0),
            ('Rollei 35', 4000, 9000, 0),
            ('Voigtlander Bessa R3A', 8000, 18000, 0),
            # MID-RANGE
            ('Canon A-1', 2000, 4500, 0),
            ('Contax T2', 25000, 55000, 0),
            ('Contax G2', 20000, 45000, 0),
            ('Ricoh GR1s', 8000, 18000, 0),
            ('Konica Hexar AF', 12000, 28000, 0),
            # RARE / EXPENSIVE
            ('Contax IIa', 18000, 45000, 0),
            ('Nikon S3 Rangefinder', 22000, 45000, 0),
            ('Minolta CLE', 25000, 55000, 0),
            ('Pentax 67', 12000, 28000, 0),
            ('Zeiss Ikon ZM', 18000, 40000, 0),
            ('Rolleiflex 3.5F', 30000, 75000, 0),
            ('Rolleiflex 2.8GX', 55000, 130000, 0),
            ('Mamiya 7II', 35000, 80000, 0),
            ('Mamiya RB67 Pro-S', 14000, 32000, 0),
            ('Mamiya RZ67 Pro II', 14000, 32000, 0),
            ('Bronica SQ-A', 10000, 22000, 0),
            ('Hasselblad 500C/M', 40000, 95000, 0),
            ('Hasselblad XPan', 60000, 140000, 0),
            ('Leica IIIf', 18000, 42000, 0),
            ('Leica M2', 45000, 90000, 0),
            ('Leica M3', 40000, 80000, 0),
            ('Leica M4', 55000, 120000, 0),
            ('Leica M4-P', 55000, 120000, 0),
            ('Leica M5', 20000, 50000, 0),
            ('Leica M6', 80000, 160000, 0),
            ('Leica MP', 120000, 285000, 0),
        ]
        c.executemany('INSERT INTO catalog VALUES (NULL,?,?,?,?)', items)


def log_trans(conn, player_id, trans_type, amount, before, after, note):
    c = conn.cursor()
    c.execute('''
        INSERT INTO log (player_id, type, amount, balance_before, balance_after, note, created)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (player_id, trans_type, amount, before, after, note))
    conn.commit()


def get_cond(price, is_film):
    if is_film == 1:
        r = random.random() * 100
        if r < 40:
            return 'Expired', 0, price * 1.1, 0
        else:
            return 'Fresh', 0, price * 1.4, 0
    
    r = random.random() * 100
    
    if r < 10:
        return 'Mint', 0, price * 3.0, 0
    elif r < 30:
        return 'Good', 0, price * 2.5, 0
    elif r < 55:
        return 'Working', 0, price * 2.0, 0
    elif r < 85:
        return 'Broken', price * 0.5, price * 0.7, price * 2.2
    else:
        return 'Parts Only', 0, price * 0.4, 0


def load_daily(conn, player_id, day):
    c = conn.cursor()
    c.execute('SELECT id, name, price, is_film FROM daily WHERE player_id=? AND day=?', (player_id, day))
    rows = c.fetchall()
    if rows:
        return [{'id': r[0], 'name': r[1], 'price': r[2], 'is_film': r[3]} for r in rows]
    
    random.seed(day)
    c.execute('SELECT name, price_min, price_max, is_film FROM catalog ORDER BY RANDOM() LIMIT 3')
    items = c.fetchall()
    random.seed()
    
    result = []
    for item in items:
        price = round(random.uniform(item[1], item[2]), 2)
        c.execute('INSERT INTO daily VALUES (NULL,?,?,?,?,0,?)', (player_id, day, item[0], price, item[3]))
        result.append({'id': c.lastrowid, 'name': item[0], 'price': price, 'is_film': item[3]})
    
    return result


def main_menu():
    cls()
    print('===========================')
    print('  VINTAGE CAM THRIFT & FLIP')
    print('===========================')
    print('[1] New Game')
    print('[2] Continue')
    print('[3] Quit')
    print('===========================')


def intro():
    cls()
    print('=== VINTAGE CAM THRIFT & FLIP ===')
    print()
    print('Buy vintage cameras cheap, sell high!')
    print()
    print('Conditions: Mint, Good, Working, Broken, Parts Only,')
    print('            Expired, Fresh')
    print()
    print('Repair broken cameras to sell for more!')
    print()
    print('GOAL: Reach P1,000,000 to buy the legendary')
    print('       Leica 0-Series No. 105!')
    print()
    input('Press Enter to start...')


def dashboard(day, balance):
    cls()
    print('===========================')
    print(' Day', day, '       Bal: P{:,.0f}'.format(balance))
    print('===========================')
    print('[1] Go Thrifting')
    print('[2] Inventory')
    print('[3] Save & Quit')
    print('===========================')
    print('Goal: P1,000,000 for Leica 0-Series')


def thrift_screen(day, balance, items):
    cls()
    print('=== DAY {} THRIFT FINDS ==='.format(day))
    print('Balance: P{:,.0f}'.format(balance))
    print()
    
    for i, item in enumerate(items, 1):
        print('[{}] {}'.format(i, item['name']), 'P{:,.0f}'.format(item['price']))
    
    print()
    print('[P] Pass')
    print('[Q] Quit to Menu')


def show_inventory(day, balance, items):
    cls()
    print('=== YOUR INVENTORY ===')
    print('Balance: P{:,.0f}'.format(balance))
    print()
    
    if not items:
        print('Empty')
    else:
        for i, item in enumerate(items, 1):
            repair_text = ''
            if item['is_fixed'] == 1:
                repair_text = ' [FIXED]'
            elif item['repair_cost'] > 0:
                repair_text = ' [Repair: P{:,.0f}]'.format(item['repair_cost'])
            
            print('{}. {} | {} | Paid P{:,.0f}{}'.format(
                i, item['name'], item['cond'], item['price_paid'], repair_text))
    
    print()
    print('[Q] Quit to Menu')


def manage_item_screen(name, cond, balance, repair_cost, sell_asis, sell_fixed, is_fixed, can_fix):
    cls()
    print('{} - {}'.format(name, cond))
    print('Balance: P{:,.0f}'.format(balance))
    print()
    
    if is_fixed:
        print('[S] Sell (repaired) for P{:,.0f}'.format(sell_fixed))
    else:
        print('[S] Sell as-is for P{:,.0f}'.format(sell_asis))
    
    if can_fix and not is_fixed and repair_cost > 0:
        print('[R] Repair for P{:,.0f} -> sell for P{:,.0f}'.format(repair_cost, sell_fixed))
    
    print('[B] Back')
    print()


def purchase_screen(name, cond, paid, sell_price, new_balance):
    cls()
    print('=== PURCHASED ===')
    print('You bought {}!'.format(name))
    print('Condition: {}'.format(cond))
    print('Paid: P{:,.0f}'.format(paid))
    print('Sell: P{:,.0f}'.format(sell_price))
    print('Balance: P{:,.0f}'.format(new_balance))
    print()
    input('Press Enter...')


def sell_screen(name, sell_price, profit, new_balance):
    cls()
    print('=== SOLD ===')
    print('Sold {} for P{:,.0f}'.format(name, sell_price))
    print('Profit: P{:,.0f}'.format(profit))
    print('Balance: P{:,.0f}'.format(new_balance))
    print()
    input('Press Enter...')


def win_screen(day, balance):
    cls()
    print('===========================')
    print('  YOU BOUGHT THE LEGENDARY!')
    print('  Leica 0-Series No. 105')
    print('===========================')
    print('Days: {}'.format(day))
    print('Final Balance: P{:,.0f}'.format(balance))
    print('===========================')
    print()
    input('Press Enter to quit...')


def main():
    conn = sqlite3.connect('thrift.db', timeout=30)
    conn.execute('PRAGMA journal_mode=WAL')
    init_db(conn)
    
    player = None
    
    while True:
        main_menu()
        choice = input('Choose: ').strip()
        
        if choice == '1':
            name = input('Your name: ').strip()
            if name == '':
                continue
            
            intro()
            
            c = conn.cursor()
            c.execute('INSERT INTO players VALUES (NULL,?,10000,1,0)', (name,))
            player_id = c.lastrowid
            conn.commit()
            
            player = {
                'id': player_id,
                'name': name,
                'balance': 10000,
                'day': 1
            }
            
            load_daily(conn, player['id'], player['day'])
        
        elif choice == '2':
            c = conn.cursor()
            c.execute('SELECT id, name, day, balance FROM players')
            players = c.fetchall()
            
            if not players:
                print('No saved games.')
                input('Press Enter...')
                continue
            
            cls()
            print('=== SAVED GAMES ===')
            for i, p in enumerate(players, 1):
                print('[{}] {} - Day {}, P{:,.0f}'.format(i, p[1], p[2], p[3]))
            print('[Q] Back')
            print()
            choice = input('Choose: ').strip()
            
            if choice.upper() == 'Q':
                continue
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(players):
                    p = players[idx]
                    player = {
                        'id': p[0],
                        'name': p[1],
                        'balance': p[3],
                        'day': p[2]
                    }
            except:
                continue
        
        elif choice == '3':
            conn.close()
            break
        else:
            continue
        
        if not player:
            continue
        
        while True:
            if player['balance'] >= 1000000:
                c = conn.cursor()
                c.execute('UPDATE players SET leica_bought=1 WHERE id=?', (player['id'],))
                conn.commit()
                win_screen(player['day'], player['balance'])
                break
            
            dashboard(player['day'], player['balance'])
            choice = input('Choose: ').strip()
            
            if choice == '1':
                items = load_daily(conn, player['id'], player['day'])
                thrift_screen(player['day'], player['balance'], items)
                choice = input('Choose: ').strip().upper()
                
                if choice == 'Q':
                    c = conn.cursor()
                    c.execute('UPDATE players SET balance=?, day=? WHERE id=?',
                              (player['balance'], player['day'], player['id']))
                    conn.commit()
                    break
                
                bought = False
                
                if choice == 'P':
                    cls()
                    print('You found some loose change!')
                    print('+P50')
                    before = player['balance']
                    player['balance'] += 50
                    after = player['balance']
                    log_trans(conn, player['id'], 'LOOSE_CHANGE', 50, before, after, 'Loose change found')
                    input('Press Enter...')
                else:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(items):
                            item = items[idx]
                            
                            if player['balance'] >= item['price']:
                                cond, repair, sell_asis, sell_fixed = get_cond(item['price'], item['is_film'])
                                before = player['balance']
                                new_bal = player['balance'] - item['price']
                                
                                purchase_screen(item['name'], cond, item['price'], sell_asis, new_bal)
                                
                                c = conn.cursor()
                                c.execute('''INSERT INTO inventory VALUES 
                                    (NULL,?,?,?,?,?,?,?,0,0,?,?)''',
                                    (player['id'], item['name'], item['price'], cond,
                                     repair, sell_asis, sell_fixed, player['day'], item['is_film']))
                                
                                player['balance'] = new_bal
                                c.execute('UPDATE players SET balance=? WHERE id=?',
                                          (player['balance'], player['id']))
                                conn.commit()
                                
                                log_trans(conn, player['id'], 'BUY', -item['price'], before, new_bal, item['name'])
                                bought = True
                    except:
                        pass
                
                player['day'] += 1
                c = conn.cursor()
                c.execute('UPDATE players SET balance=?, day=? WHERE id=?',
                          (player['balance'], player['day'], player['id']))
                conn.commit()
            
            elif choice == '2':
                while True:
                    c = conn.cursor()
                    c.execute('''SELECT id, name, price_paid, cond, repair_cost, 
                        sell_asis, sell_fixed, is_fixed, is_film FROM inventory 
                        WHERE player_id=? AND is_sold=0''',
                        (player['id'],))
                    inv = c.fetchall()
                    
                    items = []
                    for row in inv:
                        items.append({
                            'id': row[0], 'name': row[1], 'price_paid': row[2],
                            'cond': row[3], 'repair_cost': row[4],
                            'sell_asis': row[5], 'sell_fixed': row[6],
                            'is_fixed': row[7], 'is_film': row[8]
                        })
                    
                    show_inventory(player['day'], player['balance'], items)
                    choice = input('Choose: ').strip().upper()
                    
                    if choice == 'Q':
                        break
                    
                    if choice == 'B' or items == []:
                        continue
                    
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(items):
                            item = items[idx]
                            can_fix = item['cond'] == 'Broken'
                            
                            while True:
                                manage_item_screen(
                                    item['name'], item['cond'], player['balance'],
                                    item['repair_cost'], item['sell_asis'],
                                    item['sell_fixed'], item['is_fixed'], can_fix
                                )
                                action = input('Choose: ').strip().upper()
                                
                                if action == 'B':
                                    break
                                
                                elif action == 'S':
                                    if item['is_fixed']:
                                        price = item['sell_fixed']
                                    else:
                                        price = item['sell_asis']
                                    
                                    profit = price - item['price_paid']
                                    if item['is_fixed']:
                                        profit -= item['repair_cost']
                                    
                                    before = player['balance']
                                    player['balance'] += price
                                    after = player['balance']
                                    c.execute('UPDATE inventory SET is_sold=1 WHERE id=?',
                                              (item['id'],))
                                    c.execute('UPDATE players SET balance=? WHERE id=?',
                                              (player['balance'], player['id']))
                                    conn.commit()
                                    
                                    log_trans(conn, player['id'], 'SELL', price, before, after, item['name'])
                                    sell_screen(item['name'], price, profit, player['balance'])
                                    break
                                
                                elif action == 'R' and can_fix and not item['is_fixed']:
                                    if player['balance'] < item['repair_cost']:
                                        print('Not enough money!')
                                        input('Press Enter...')
                                        continue
                                    
                                    before = player['balance']
                                    player['balance'] -= item['repair_cost']
                                    after = player['balance']
                                    c.execute('UPDATE inventory SET is_fixed=1 WHERE id=?',
                                              (item['id'],))
                                    c.execute('UPDATE players SET balance=? WHERE id=?',
                                              (player['balance'], player['id']))
                                    conn.commit()
                                    
                                    log_trans(conn, player['id'], 'REPAIR', -item['repair_cost'], before, after, item['name'])
                                    item['is_fixed'] = 1
                                    print('Repaired!')
                                    input('Press Enter...')
                    except:
                        pass
            
            elif choice == '3':
                c = conn.cursor()
                c.execute('UPDATE players SET balance=?, day=? WHERE id=?',
                          (player['balance'], player['day'], player['id']))
                conn.commit()
                break
    
    conn.close()


if __name__ == '__main__':
    main()
