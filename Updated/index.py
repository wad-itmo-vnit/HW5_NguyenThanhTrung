  
from flask import Flask, request, render_template, make_response, redirect, flash
import app_config
from model.user import User                                                             # chi can moi class User nen dung from thay vi import
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = app_config.SECRET_KEY                                        # Can dung den cookie nen phai co SECRET_KEY

# Co user roi, thi can phai luu user vao dictonary, de tien cho demo
# users = {}                                                                              # dictionary: key: username , doi tuong: du lieu va cac ham can thiet
# users['admin'] = User('admin', '1337')                                                  # user mac dinh

# -5 la data la 4 chu, them dau "." nua la 5 , nghia la bo di phan duoi la .data
users = {name[:-5]:User.from_file(name) for name in os.listdir(app_config.USER_DB_DIR)}               # ham os.list... dua ra danh sach tat ca cac file

# DECORATOR:
def login_required(func):
    @wraps(func)
    def login_func(*arg, **kwargs):
        # phai dung try, catch vi chua xu li truong hop chua co cookie
        try:
            if (users[request.cookies.get('username')].authorize(request.cookies.get('token'))):                    # luu 2 thong tin la username va token, vi trong backend xu li nhieu thong tin, vi du nhu hash token truoc khi gui den cho nguoi dung, thi viec dung token do de tim lai trong CSDL rat kho, con username la cai k the giau vi tren ung dung nao cung xuat hien cai do, nen dung username cho nhanh
                return func(*arg, **kwargs)
        except:
            pass
        flash("Login required!!!")
        return redirect('/login')
    return login_func

def no_login(func):
    @wraps(func)
    def no_login_func(*arg, **kwargs):
        try:
            if (users[request.cookies.get('username')].authorize(request.cookies.get('token'))):                    # dang nhap roi thi redirect ve home
                flash("You're already in!")
                return redirect('/')
        except:
            pass
        return func(*arg, **kwargs)
    return no_login_func

@app.route('/')
def home():
    return redirect('/index')

@app.route('/index')
@login_required                                                                     # can login_required
def index():
    return render_template('index.html', text="Welcome!!!")

@app.route('/login', methods=['POST', 'GET'])
@no_login
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # Post request se gui den 2 thong tin la username va password, dau tien phai lay thong tin ra
    # O day chi xu li de thuc hien chuc nang, chu k bao dam an toan cho ung dung
    # Thuc te thi phai kiem tra nhung du lieu do co dung k.
    username, password = request.form.get('username'), request.form.get('password')

    # truoc tien nguoi dung can dang nhap, roi moi xu li den phan authorize, nen co phan o duoi day
    if username in users.keys():                                                    # kiem tra user co hay k
        # current_user = users[username]
        if users[username].authenticate(password):                                  # neu dung nua thi tien hanh set cookie, bao nguoi dung da dang nhap
            token = users[username].init_session()                                  # co the su dung current_user thay vi su dung truc tiep tu trong mang nhu o day, init_session(): tao token, luu token vao trong object user do, va tra ve token cho chung ta
            resp = make_response(redirect('/index'))
            resp.set_cookie('username', username)
            resp.set_cookie('token', token)
            return resp
        else:
            flash("Username or password is not correct!!!")
    else:
        flash("User does not exist")
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required                                                                     # Chi gui yeu cau thoat dang nhap khi da dang nhap
def logout():
    username = request.cookies.get('username')                                      # da co token, username o trong cookie
    users[username].terminate_session()
    resp = make_response(redirect('/login'))
    resp.delete_cookie('username')
    resp.delete_cookie('token')
    flash("You've logged out!!!")
    return resp

@app.route('/register', methods=['POST', 'GET'])
@no_login
def register():
    if request.method == "GET":
        return render_template('register.html')
    
    # POST
    username, password, password_confirm = request.form.get('username'), request.form.get('password'), request.form.get('password_confirm')
    if username not in users.keys():
        if password == password_confirm:
            # users[username] = User(username, password)                              # sai, vi password nay se luu thang chu khong luu duoi dang hash nua
            users[username] = User.new(username,password)
            token = users[username].init_session()                                  # dang ki
            resp = make_response(redirect('/index'))                                # xong
            resp.set_cookie('username', username)                                   # thi
            resp.set_cookie('token', token)                                         # dang nhap
            return resp                                                             # luon
        else:
            flash("Passwords don't match!!!")
    else:
        flash("User already exists!!!")  
    return render_template('register.html')                                         # GET request

if __name__ == '__main__':
    app.run(host='localhost', port=80, debug=True)
    # Thuc te thi co the doi localhost -> mang LAN, port co the = 5000
    # debug = True , tuc la khi sua lai code va luu thi trang web tu sua lai roi, k can phai chay lai "py index.py" nua