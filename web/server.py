import os, sqlite3, json
from datetime import datetime, timedelta
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, abort)
import bcrypt
import stripe

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-!@#$%")
app.permanent_session_lifetime = timedelta(days=30)

# ── Stripe 설정 ──────────────────────────────────────────
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Stripe 가격 ID (Stripe 대시보드에서 생성 후 환경변수에 입력)
PRICE_IDS = {
    "starter": os.environ.get("STRIPE_STARTER_PRICE_ID", ""),
    "pro":     os.environ.get("STRIPE_PRO_PRICE_ID",     ""),
}

PLAN_NAMES = {"free": "무료", "starter": "스타터", "pro": "프로"}
PLAN_LIMITS = {
    "free":    {"posts": 10,  "platforms": 1, "ai_calls": 20},
    "starter": {"posts": 200, "platforms": 5, "ai_calls": 500},
    "pro":     {"posts": -1,  "platforms": -1, "ai_calls": -1},
}

DATABASE = os.path.join(os.path.dirname(__file__), "users.db")


# ── DB 초기화 ────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            name                  TEXT    NOT NULL,
            email                 TEXT    UNIQUE NOT NULL,
            password_hash         TEXT    NOT NULL,
            plan                  TEXT    DEFAULT 'free',
            stripe_customer_id    TEXT,
            stripe_subscription_id TEXT,
            subscription_status   TEXT    DEFAULT 'inactive',
            ai_calls_this_month   INTEGER DEFAULT 0,
            posts_this_month      INTEGER DEFAULT 0,
            usage_reset_at        TEXT    DEFAULT CURRENT_TIMESTAMP,
            created_at            TEXT    DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      INTEGER NOT NULL,
            currency    TEXT    DEFAULT 'krw',
            plan        TEXT,
            status      TEXT,
            stripe_id   TEXT,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()


def get_db():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con


def get_user(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated


def plan_required(min_plan):
    order = {"free": 0, "starter": 1, "pro": 2}
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_plan = session.get("user_plan", "free")
            if order.get(user_plan, 0) < order.get(min_plan, 0):
                return redirect(url_for("pricing"))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── 라우트: 공개 페이지 ──────────────────────────────────
@app.route("/")
def index():
    user = None
    if "user_id" in session:
        user = get_user(session["user_id"])
    return render_template("index.html", user=user)


@app.route("/pricing")
def pricing():
    user = None
    if "user_id" in session:
        user = get_user(session["user_id"])
    return render_template("pricing.html", user=user)


# ── 라우트: 인증 ─────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            error = "모든 필드를 입력해주세요."
        elif len(password) < 8:
            error = "비밀번호는 8자 이상이어야 합니다."
        else:
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, pw_hash)
                )
                db.commit()
                user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
                db.close()
                session.permanent = True
                session["user_id"]   = user["id"]
                session["user_name"] = user["name"]
                session["user_plan"] = user["plan"]
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                error = "이미 사용 중인 이메일입니다."
            except Exception as e:
                error = str(e)

    return render_template("auth.html", mode="register", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            session.permanent = True
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            session["user_plan"] = user["plan"]
            next_url = request.args.get("next")
            return redirect(next_url if next_url else url_for("dashboard"))

        error = "이메일 또는 비밀번호가 올바르지 않습니다."

    return render_template("auth.html", mode="login", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ── 라우트: 대시보드 ─────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user(session["user_id"])
    session["user_plan"] = user["plan"]
    limits = PLAN_LIMITS.get(user["plan"], PLAN_LIMITS["free"])

    db = get_db()
    payments = db.execute(
        "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user["id"],)
    ).fetchall()
    db.close()

    return render_template("dashboard.html",
                           user=user, limits=limits, payments=payments,
                           plan_name=PLAN_NAMES.get(user["plan"], "무료"))


# ── 라우트: 결제 (Stripe) ────────────────────────────────
@app.route("/checkout/<plan>", methods=["POST"])
@login_required
def create_checkout(plan):
    if plan not in PRICE_IDS:
        abort(400)

    if not stripe.api_key or not PRICE_IDS.get(plan):
        # Stripe 미설정 시 안내 페이지
        return render_template("stripe_setup.html", plan=plan)

    try:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

        if user["stripe_customer_id"]:
            customer_id = user["stripe_customer_id"]
        else:
            customer = stripe.Customer.create(email=user["email"], name=user["name"])
            customer_id = customer.id
            db.execute("UPDATE users SET stripe_customer_id = ? WHERE id = ?",
                       (customer_id, session["user_id"]))
            db.commit()
        db.close()

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": PRICE_IDS[plan], "quantity": 1}],
            mode="subscription",
            success_url=request.host_url + "subscription/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.host_url + "pricing",
            locale="ko",
            allow_promotion_codes=True,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return render_template("error.html", message=str(e)), 500


@app.route("/subscription/success")
@login_required
def subscription_success():
    session_id = request.args.get("session_id")
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    session["user_plan"] = user["plan"]
    db.close()
    return render_template("success.html", user=user)


@app.route("/subscription/cancel", methods=["POST"])
@login_required
def cancel_subscription():
    user = get_user(session["user_id"])
    if user["stripe_subscription_id"] and stripe.api_key:
        try:
            stripe.Subscription.modify(
                user["stripe_subscription_id"],
                cancel_at_period_end=True
            )
            db = get_db()
            db.execute("UPDATE users SET subscription_status = 'cancelling' WHERE id = ?",
                       (session["user_id"],))
            db.commit()
            db.close()
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return redirect(url_for("dashboard"))


# ── Stripe 웹훅 ──────────────────────────────────────────
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload    = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception:
        return "", 400

    data = event["data"]["object"]

    if event["type"] == "checkout.session.completed":
        customer_id     = data.get("customer")
        subscription_id = data.get("subscription")
        if subscription_id:
            sub      = stripe.Subscription.retrieve(subscription_id)
            price_id = sub["items"]["data"][0]["price"]["id"]
            plan     = next((k for k, v in PRICE_IDS.items() if v == price_id), "starter")
            amount   = sub["items"]["data"][0]["price"]["unit_amount"] or 0

            db = get_db()
            user = db.execute("SELECT * FROM users WHERE stripe_customer_id = ?",
                              (customer_id,)).fetchone()
            if user:
                db.execute("""UPDATE users SET
                    plan = ?, stripe_subscription_id = ?, subscription_status = 'active'
                    WHERE stripe_customer_id = ?""",
                    (plan, subscription_id, customer_id))
                db.execute("""INSERT INTO payments (user_id, amount, plan, status, stripe_id)
                    VALUES (?, ?, ?, 'paid', ?)""",
                    (user["id"], amount, plan, subscription_id))
            db.commit()
            db.close()

    elif event["type"] == "customer.subscription.deleted":
        customer_id = data.get("customer")
        db = get_db()
        db.execute("""UPDATE users SET
            plan = 'free', subscription_status = 'inactive', stripe_subscription_id = NULL
            WHERE stripe_customer_id = ?""", (customer_id,))
        db.commit()
        db.close()

    elif event["type"] == "invoice.payment_failed":
        customer_id = data.get("customer")
        db = get_db()
        db.execute("UPDATE users SET subscription_status = 'past_due' WHERE stripe_customer_id = ?",
                   (customer_id,))
        db.commit()
        db.close()

    return "", 200


# ── API: 사용량 확인 ─────────────────────────────────────
@app.route("/api/usage")
@login_required
def api_usage():
    user   = get_user(session["user_id"])
    limits = PLAN_LIMITS.get(user["plan"], PLAN_LIMITS["free"])
    return jsonify({
        "plan":             user["plan"],
        "ai_calls":         user["ai_calls_this_month"],
        "ai_calls_limit":   limits["ai_calls"],
        "posts":            user["posts_this_month"],
        "posts_limit":      limits["posts"],
    })


if __name__ == "__main__":
    init_db()
    print("✅ 서버 시작: http://localhost:8000")
    app.run(debug=True, port=8000, host="0.0.0.0")
