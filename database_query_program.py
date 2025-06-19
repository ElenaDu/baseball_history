import sqlite3

db_path = './db/baseball_stats.db'

def get_conn():
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Error connecting to DB: {e}")
        return None

def top_batting_teams():
    conn = get_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.name, COUNT(*) as leader_count
            FROM batting_stats b
            JOIN teams t ON b.team_id = t.id
            GROUP BY t.name
            ORDER BY leader_count DESC
            LIMIT 10
        ''')
        results = cursor.fetchall()
        print("\nTop 10 teams with the most batting leaders:")
        print(f"{'Team':<30}Leaders")
        print("-" * 40)
        for team, count in results:
            print(f"{team:<30}{count}")
    except sqlite3.Error as e:
        print(f"DB query error in top_batting_teams: {e}")
    finally:
        conn.close()

def top_pitching_teams():
    conn = get_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.name, COUNT(*) as leader_count
            FROM pitching_stats p
            JOIN teams t ON p.team_id = t.id
            GROUP BY t.name
            ORDER BY leader_count DESC
            LIMIT 10
        ''')
        results = cursor.fetchall()
        print("\nTop 10 teams with the most pitching leaders:")
        print(f"{'Team':<30}Leaders")
        print("-" * 40)
        for team, count in results:
            print(f"{team:<30}{count}")
    except sqlite3.Error as e:
        print(f"DB query error in top_pitching_teams: {e}")
    finally:
        conn.close()

def leaders_by_year():
    while True:
        year_input = input("Enter a year (1901-2024) to see batting and pitching leaders, or type 'exit' to quit: ").strip()
        
        if year_input.lower() == 'exit':
            print("Exiting the query.")
            return
        
        if year_input.isdigit() and 1901 <= int(year_input) <= 2024:
            year = int(year_input)
            break
        
        print("Invalid input. Please enter a valid year between 1901 and 2024 or type 'exit' to quit.")

    conn = get_conn()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 'Batting' AS role, b.stat, b.name, t.name AS team, b.value
            FROM batting_stats b
            JOIN teams t ON b.team_id = t.id
            WHERE b.year = ?
            UNION ALL
            SELECT 'Pitching' AS role, p.stat, p.name, t.name AS team, p.value
            FROM pitching_stats p
            JOIN teams t ON p.team_id = t.id
            WHERE p.year = ?
            ORDER BY role, stat
        ''', (year, year))
        results = cursor.fetchall()

        if not results:
            print(f"\nNo batting or pitching leaders found for {year}.")
            return

        print(f"\nBatting & Pitching leaders for {year}:")
        print(f"{'Role':<10}{'Stat':<20}{'Player':<25}{'Team':<20}{'Value'}")
        print("-" * 95)
        for role, stat, player, team, value in results:
            print(f"{role:<10}{stat:<20}{player:<25}{team:<20}{value}")

    except sqlite3.Error as e:
        print(f"DB query error in leaders_by_year: {e}")
    finally:
        conn.close()

def top_players_by_stat():
    stat_options = {
        "1": ("batting", "Home Runs"),
        "2": ("batting", "Base on Balls"),
        "3": ("pitching", "Wins"),
        "4": ("pitching", "ERA")
    }

    print("\nSelect a stat to see top 5 players:")
    print("1. Home Runs (Batting)")
    print("2. Base on Balls (Batting)")
    print("3. Wins (Pitching)")
    print("4. ERA (Pitching)")

    while True:
        choice = input("Enter your choice (1-4), or 'exit' to cancel: ").strip()
        if choice.lower() == 'exit':
            print("Cancelled.")
            return
        if choice in stat_options:
            role, stat = stat_options[choice]
            break
        print("Invalid choice. Please enter a number from 1 to 4.")

    table = "batting_stats" if role == "batting" else "pitching_stats"

    conn = get_conn()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT name, value
            FROM {table}
            WHERE stat = ?
            ORDER BY value DESC
            LIMIT 5
        ''', (stat,))
        results = cursor.fetchall()

        print(f"\nTop 5 players by '{stat}' ({role.title()}):")
        print(f"{'Player':<30}{'Value'}")
        print("-" * 40)
        for player, value in results:
            print(f"{player:<30}{value}")

    except sqlite3.Error as e:
        print(f"DB query error in top_players_by_stat: {e}")
    finally:
        conn.close()



def menu():
    while True:
        print("\n==== Baseball Leaders Stats Query Menu ====")
        print("1. Display top 10 teams with most batting leaders")
        print("2. Display top 10 teams with most pitching leaders")
        print("3. Select year to see batting and pitching leaders")
        print("4. Display top 5 players by performance metric ")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            top_batting_teams()    
        elif choice == '2':
            top_pitching_teams()
        elif choice == '3':
            leaders_by_year()
        elif choice == '4':
            top_players_by_stat()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

if __name__ == '__main__':
    menu()