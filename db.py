import psycopg2
import bcrypt
from typing import Any

salt = bcrypt.gensalt()


def connection():
    return psycopg2.connect(
        database="rbac",
        host="localhost",
        port=5432,
        user="duck",
        password="duckdb123",
    )


def create_table():
    with connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE rbac(
                user_id UUID PRIMARY KEY,
                username varchar(50) not null,
                email varchar(200) not null,
                password text not null,
                role varchar(8) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT now()
            )"""
        )
        conn.commit()


# create_table()


def select_user(username=None, email=None):
    with connection() as conn:
        cur = conn.cursor()
        if username:
            cur.execute("""SELECT * FROM rbac WHERE username=%s""", (username,))
        if email:
            cur.execute("""SELECT * FROM rbac WHERE email=%s""", (email,))

        user = cur.fetchone()

        if user:
            id, usrname, mail, pw, role, created_at = user
            return {
                "user_id": id,
                "username": usrname,
                "email": mail,
                "password": pw,
                "role": role,
                "created_at": created_at,
            }
        return None


def update_pw(username, pw):
    with connection() as conn:
        cur = conn.cursor()
        cur.execute("""UPDATE rbac SET password=%s WHERE username=%s""", (pw, username))
        conn.commit()


def insert(usr: dict[str, Any]):
    uuid = usr["uuid"]
    usrname = usr["username"]
    pw = bcrypt.hashpw(usr["password"].encode(), salt).decode()
    mail = usr["email"]
    role = usr["role"]

    with connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO rbac (user_id, username, password, email, role) VALUES (%s, %s, %s, %s, %s)""",
            (uuid, usrname, pw, mail, role),
        )
        conn.commit()


def update_role(username, role):
    with connection() as conn:
        cur = conn.cursor()
        cur.execute("""UPDATE rbac SET role=%s WHERE username=%s""", (role, username))
        conn.commit()
