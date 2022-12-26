import psycopg2
from secrets import pg_user, pg_password, host, port, dbname

def connect_to_postgres():
    conn = psycopg2.connect(f"host='{host}' port='{port}' dbname='{dbname}' user='{pg_user}' password='{pg_password}'")
    cur = conn.cursor()
    query ="""
    copy spotify_genres
    from '/opt/airflow/dags/spotify_data/spotify_genres.csv'
    delimiter ',' csv;
    """
    cur.execute(query)

if __name__ == "__main__":
    connect_to_postgres()