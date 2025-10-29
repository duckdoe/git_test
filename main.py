import flask
import bcrypt
import db
import uuid
from ss import r

app = flask.Flask(__name__)


@app.post("/signup")
def signup():
    data = flask.request.get_json()
    user_id = str(uuid.uuid4())

    db.insert(
        {
            "username": data["username"],
            "password": data["password"],
            "email": data["email"],
            "role": data["role"] or "user",
            "uuid": user_id,
        }
    )
    return {"status": "created", "message": "user signup successful!"}, 201


@app.post("/login")
def login():
    data = flask.request.get_json()

    usrname = data["username"]
    pw = data["password"]

    usr = db.select_user(usrname)
    if usr:
        is_same = bcrypt.checkpw(pw.encode(), usr["password"].encode())
        if is_same:
            ss_id = str(f"{uuid.uuid4()}|{usr['role']}")
            r.setex(usrname, 3600, ss_id)
            return {
                "status": "success",
                "message": "user logged in successfully",
                "session_id": ss_id,
            }
        return {"status": "denied", "message": "invalid password"}, 400
    return {"status": "failed", "message": "user does not exist"}, 400


@app.put("/update/password")
def update_pw():
    ss_id = flask.request.headers.get("Session-Id")
    req = flask.request.get_json()

    stored_ss_id = r.get(req["username"])
    usr = db.select_user(req["username"])
    if usr:
        if ss_id == stored_ss_id:
            db.update_pw(req["username"], req["password"])
            return {
                "status": "success",
                "message": "user password updated successfully",
            }, 201
        return {"status": "failed", "message": "invalid session id"}, 400
    return {"status": "failed", "message": "user does not exist"}


@app.put("/update/role")
def update_role():
    roles = ["admin", "user"]

    ss_id = flask.request.headers.get("Session-Id")
    req = flask.request.get_json()
    stored_ss_id = r.get(req["username"])
    if ss_id == stored_ss_id:
        _, role = ss_id.split("|")
    else:
        return {"status": "failed", "message": "Invalid session_id"}

    if role == "admin":
        if req["role"] in roles:
            db.update_role(req["username"], req["role"])
            return {
                "status": "success",
                "message": "user role updated successfully",
            }, 201
        return {
            "status": "failed",
            "message": f"user role {req['role']} does not exist",
        }

    return {
        "status": "failed",
        "message": "You do not have enough permissions to do that",
    }, 403


@app.route("/<usr>/dashboard")
def dashboard(usr):
    ss_id = flask.request.headers.get("Session-Id")
    _, role = ss_id.split("|")
    stored_ss_id = r.get(usr)

    user = db.select_user(usr)

    if not user:
        return {"status": "failed", "message": "user does not exist"}, 404

    if ss_id == stored_ss_id:
        if role == "user":
            return {
                "status": "success",
                "message": "welcome user",
                "user": {
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "created_at": user["created_at"],
                },
            }, 200

        if role == "admin":
            return {
                "status": "success",
                "message": "welcome admin",
                "user": {
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "created_at": user["created_at"],
                },
            }, 200

        return {"status": "failed", "message": "invalid role"}

    return {"status": "failed", "message": "invalid session id"}


if __name__ == "__main__":
    app.run(debug=True)
