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
            SELECT team, COUNT(*) as leader_count
            FROM batting_stats
            GROUP BY team
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
            SELECT team, COUNT(*) as leader_count
            FROM pitching_stats
            GROUP BY team
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
            SELECT 'Batting' AS role, stat, player, team, value
            FROM batting_stats
            WHERE year = ?
            UNION ALL
            SELECT 'Pitching' AS role, stat, player, team, value
            FROM pitching_stats
            WHERE year = ?
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

def top_5_hitting_players():
    conn = get_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT player, MAX(value) as max_stat_value, stat, year, team
            FROM batting_stats
            GROUP BY player
            ORDER BY max_stat_value DESC
            LIMIT 5
        ''')
        results = cursor.fetchall()
        print("\nTop 5 players of all time based on highest hitting stat:")
        print(f"{'Player':<25}{'Stat':<20}{'Value':<10}{'Year':<6}{'Team'}")
        print("-" * 75)
        for player, value, stat, year, team in results:
            print(f"{player:<25}{stat:<20}{value:<10}{year:<6}{team}")
    except sqlite3.Error as e:
        print(f"DB query error in top_5_hitting_players: {e}")
    finally:
        conn.close()

def menu():
    while True:
        print("\n==== Baseball Leaders Stats Query Menu ====")
        print("1. Display top 10 teams with most batting leaders")
        print("2. Display top 10 teams with most pitching leaders")
        print("3. Select year to see batting and pitching leaders")
        print("4. Display top 5 all-time batting leaders")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            top_batting_teams()    
        elif choice == '2':
            top_pitching_teams()
        elif choice == '3':
            leaders_by_year()
        elif choice == '4':
            top_5_hitting_players()           
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

if __name__ == '__main__':
    menu()