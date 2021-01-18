auth = Blueprint('auth', __name__)

randomKey = ""
beforeRandomKey = ""
scope = "user:email,read:user"

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(choice(letters) for i in range(length))
    return result_str

@auth.route("/github/403")
def gh403():
    return "403 <br> Forbidden <br> Unauthorized app tried to login! If you logged in with this app, please try again!", 403

@auth.route("/github/oauth")
def githubOAUTH():
    GH_ID = os.environ["ID_KEY_GITHUB"]
    GH_SECRET = os.environ["SECRET_KEY_GITHUB"]
    print(randomKey)
    if (randomKey != request.args.get('state') or beforeRandomKey != request.args.get("state")):
        print("403! \nForbidden")
        return redirect(url_for("auth.gh403"))
    else:
        print("[github] Authorizing 1/2...")
        code = request.args.get('code')
        state = request.args.get('state')
        r = requests.get("https://github.com/login/oauth/access_token",
            data = {
                "client_id": GH_ID,
                "client_secret": GH_SECRET,
                "code": code,
                "state": state,
                "Accept": "application/json",
                },
            headers = {
                'Accept': 'application/vnd.github.v3.text-match+json',
                }
            )

        print("[github] Authorizing 2/2")
        json = r.json()
        token = json["access_token"]
        r = requests.get("https://api.github.com/user",
            headers = {
                'Accept': 'application/vnd.github.v3.text-match+json',
                "Authorization": "Token "+token
                },
            )

        json = r.json()

        print("[github] Authorized!")

        login = User.query.filter_by(username=json["login"]).first()
        if not login:
            print("[login-system] Not registred!")
            if json["name"] == None or json["name"] == "None":
                jsonName = json["login"]
            else:
                jsonName = json["name"]
            jsonUser = json["login"]
            if json["email"] == None or json["email"] == "None":
                email = None
            terms_accepted = int(time())
            avatar = json["avatar_url"]

            new_user = User(email=email, first_name=jsonName, terms_accepted= terms_accepted, avatar = avatar, username = jsonUser, last_name="")
            db.session.add(new_user)
            db.session.commit()

        user = User.query.filter_by(username=json["login"]).first()
        if user is not None:

            login_user(user, remember=True)

            return redirect(url_for("main.index"))



authVal = 0
@auth.route("/github/login")
def githubLOGIN(authVal=authVal, scope=scope):
    if (authVal==0):
        global randomKey
        global beforeRandomKey
        beforeRandomKey = randomKey
        randomKey = get_random_string(10)
        authVal = authVal + 1
    elif (authVal==4):
        authVal = 0
    else:
        authVal = authVal + 1
    GH_ID = os.environ["ID_KEY_GITHUB"]
    return redirect("https://github.com/login/oauth/authorize?client_id="+GH_ID+"&state="+randomKey+"&scope="+scope)
