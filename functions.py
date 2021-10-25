import sqlite3
import datetime

connection = None
cursor = None

def connect(dbName):
    global connection, cursor
    connection = sqlite3.connect(dbName)
    cursor = connection.cursor()
    _createViews()


def _createViews():
    global connection, cursor
    cursor.executescript("""
    CREATE VIEW IF NOT EXISTS ActiveProducts AS 
    SELECT sid, lister, products.pid, strftime('%Y-%m-%d', edate), products.descr as pdescr, cond, rprice, sales.descr as sdescr, rid, reviewer, rating, rtext, rdate FROM sales, products LEFT OUTER JOIN previews ON previews.pid = products.pid WHERE sales.pid = products.pid AND julianday(edate) > julianday('now');
    CREATE VIEW IF NOT EXISTS SalesFormat AS
    SELECT sales.sid, sales.pid, lister, descr, ifnull(MAX(amount), rprice) AS price, strftime('%Y-%m-%d %H:%M', edate) AS TimeRemaining from sales LEFT OUTER JOIN bids ON sales.sid = bids.sid WHERE julianday(edate) > julianday('now') GROUP BY sales.sid, sales.pid, lister, descr, rprice;
    """)
    connection.commit()


def _getDateTimeDifference(date):
    if date in ["", None]:
        return ""
    currentTime = datetime.datetime.now()
    compareTime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
    timediff = compareTime - currentTime
    hours = int(timediff.seconds / (60 * 60))
    minutes = int((timediff.seconds - (hours * 60 * 60)) / 60)
    time = str(timediff.days) + " days " + str(hours) + " hours " + str(minutes) + " mins"
    return time

def list_products():
    global connection, cursor
    cursor.execute("""
    select pid, pdescr, COUNT(distinct rid) as numreviews, AVG(rating) as avgrating, COUNT(distinct sid) as activesales
    from ActiveProducts
    GROUP BY pid ORDER BY activesales DESC;
    """)
    return [[i[0] for i in cursor.description], cursor.fetchall()]


def _get_next_preview_id():
    global connection, cursor
    cursor.execute("SELECT MAX(rid) from previews");
    return str(int(cursor.fetchone()[0]) + 1)


def product_review(pid, user, rating, rtext):
    global connection, cursor
    cursor.execute("""
    INSERT INTO previews VALUES (?,?, ?, ?, ?, julianday('now'));
    """, (_get_next_preview_id(), pid, user, rating, rtext))
    connection.commit()


def list_reviews(pid):
    global connection, cursor
    cursor.execute("""
    SELECT rtext from ActiveProducts WHERE pid = ? AND rid NOT NULL;
    """, (pid,))
    return [[i[0] for i in cursor.description], cursor.fetchall()]


def _get_next_sale_id():
    global connection, cursor
    cursor.execute("SELECT MAX(sid) from sales");
    return "S" + str((int(cursor.fetchone()[0][1:]) + 1))


def post_sale(user, pid, endtime, descr, cond, rprice):
    global connection, cursor
    cursor.execute("""
     INSERT INTO sales Values (?, ?, ?, julianday(strftime("%Y-%m-%d %H:%M", ?)), ?, ?, ?);
     """,(_get_next_sale_id(), user, pid, endtime, descr, cond, rprice))
    connection.commit()


def search_sales(keywords):
    global connection, cursor
    args = ['%' + i + '%' for i in keywords.split(' ')]
    doubleargs = []
    for i in args:
        doubleargs.append(i)
        doubleargs.append(i)
    templateStatement = "SELECT * from SalesFormat LEFT OUTER JOIN products on SalesFormat.pid = products.pid WHERE SalesFormat.descr LIKE ? or products.descr LIKE ?"
    innerStatements = templateStatement
    for i in range(len(args) - 1):
        innerStatements = innerStatements + " UNION ALL " + templateStatement
    finalStatement = "SELECT sid, descr, price, TimeRemaining from (" + innerStatements + ") GROUP BY sid, descr, price, TimeRemaining ORDER BY COUNT(sid) DESC;"
    cursor.execute(finalStatement, tuple(doubleargs))
    data = cursor.fetchall()
    for i in range(len(data)):
        temp = list(data[i])
        temp[-1] = _getDateTimeDifference(temp[-1])
        data[i] = tuple(temp)
    return [[i[0] for i in cursor.description], data]


def login(email, password):
    global connection, cursor
    cursor.execute("""
     SELECT email FROM users WHERE email = ? AND pwd = ?;
     """,(email, password))
    return (cursor.fetchone() != None)


def sign_up(email,pwd,name,gender,city):
    global connection, cursor
    try:
        cursor.execute("""
         INSERT INTO users Values (?, ?, ?, ?, ?);
         """,(email,name,pwd,city,gender))    
        connection.commit()
        return True
    except:
        return False
    # TODO:check if email is duplicate


def search_users(keyword):
    global connection, cursor
    cursor.execute("""
    SELECT email, name, city FROM users WHERE name LIKE ? or email LIKE ?
    """, ("%" + keyword + "%", "%" + keyword + "%"))
    return [[i[0] for i in cursor.description], cursor.fetchall()]


def user_review(reviewer, reviewee, rtext, rating):
    global connection, cursor
    cursor.execute("""
    INSERT INTO reviews VALUES (?, ?, ?, ?, julianday('now'));
    """, (reviewer, reviewee, rating, rtext))
    connection.commit()


def list_product_sales(pid):
    global connection, cursor
    cursor.execute("""
    SELECT sid, descr, price, TimeRemaining FROM SalesFormat WHERE pid LIKE ?;
    """, (pid,))
    return [[i[0] for i in cursor.description], cursor.fetchall()]


def list_user_sales(user):
    global connection, cursor
    cursor.execute("""
    SELECT sid, descr, price, TimeRemaining FROM SalesFormat WHERE lister = ?;
    """, (user,))
    return [[i[0] for i in cursor.description], cursor.fetchall()]


def list_user_reviews(user):
    global connection, cursor
    cursor.execute("""
    SELECT reviewer, rating, rtext FROM reviews WHERE reviewee = ?;
    """, (user,))
    return [[i[0] for i in cursor.description], cursor.fetchall()]


def sale_info(sid):
    global connection, cursor
    cursor.execute("""
    select sales.sid, lister, COUNT(distinct reviews.reviewer) AS UserReviews, AVG(reviews.rating) AS UserRating, sales.descr AS SaleDescription, strftime('%Y-%m-%d', edate) AS EndDate, cond AS Condition, ifnull(MAX(amount), rprice) as Price, products.pid AS pid, products.descr AS ProductsDescription, COUNT(distinct rid) AS ProductReviews, AVG(previews.rating) AS ProductRating from sales LEFT OUTER JOIN reviews ON sales.lister = reviews.reviewee LEFT OUTER JOIN bids ON bids.sid = sales.sid LEFT OUTER JOIN products ON products.pid = sales.pid LEFT OUTER JOIN previews ON previews.pid = products.pid WHERE sales.sid = ? GROUP BY sales.sid, lister, SaleDescription, EndDate, Condition, rprice, ProductsDescription;
    """, (sid,))
    data = [[i[0] for i in cursor.description], cursor.fetchall()]
    if data[1][0][data[0].index("pid")] in ['', None]:
        data[1][0] = data[1][0][0:data[0].index("pid")]
        data[0] = data[0][0:data[0].index("pid")]
    elif data[1][0][data[0].index("ProductReviews")] == 0:
        data[1][0] = data[1][0][0:data[0].index("ProductReviews")]
        data[0] = data[0][0:data[0].index("ProductReviews")]
        data[0].append("ProductReview")
        data[1][0] = tuple(list(data[1][0]) + ["Product not reviewed"])
    return data


def _get_max_bid_amount(sid):
    global connection, cursor
    cursor.execute("SELECT MAX(amount) from bids WHERE sid = ?", (sid,));
    return cursor.fetchone()[0]


def _get_next_bid():
    global connection, cursor
    cursor.execute("SELECT MAX(bid) from bids");
    return "B" + str((int(cursor.fetchone()[0][1:]) + 1))


def place_bid(user, sid, amount):
    global connection, cursor
    if int(_get_max_bid_amount(sid)) >= amount:
        return False
    else:
        cursor.execute("""
        INSERT INTO bids VALUES (?, ?, ?, date('now'), ?);
        """, (_get_next_bid(), user, sid, amount))
        connection.commit()
        return True
