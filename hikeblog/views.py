from hikeblog import app

@app.route("/")
def mainpage():
    return "Main page"