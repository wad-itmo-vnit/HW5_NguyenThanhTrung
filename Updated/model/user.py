# MUC DICH: De tao them duoc user, hay luu tru dang nhap voi nhieu user, thi can model user

import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
import app_config

# tao random
def gen_session_token(length = 24):
    token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(length)])                   # random ra 24 ki tu roi noi chung voi nhau
    return token

class User:                                                     # class User de luu tat ca thong tin ve 1 user
    # def __init__(self, username, password): #, token=None):
    #     self.username = username
    #     self.password = password
    #     # self.token = token
    #     self.token = None                                      # de phong truong hop chua tao token ma co yeu cau truy cap den
    #     # self.dump()

    def __init__(self, username, password, token=None):
        self.username = username
        # self.password = generate_password_hash(password)        # doc trong file ra ma da hash san roi, nen k dung cai nay dc nua
        self.password = password
        self.token = token                                      # de phong truong hop chua tao token ma co yeu cau truy cap den
        self.dump()
    
    # Truong hop co du lieu moi
    @classmethod
    def new(cls, username, password):
        password = generate_password_hash(password)
        return cls(username, password)
    
    # LOAD FROM FILE
    @classmethod
    def from_file(cls, filename):
        with open(app_config.USER_DB_DIR + '/' + filename, 'r') as f:
            text = f.readline().strip()                                 # xoa dau cach o 2 dau string
            username, password, token = text.split(';')
            if token == 'None':
                return cls(username, password)
            return cls(username, password, token)
    
    def authenticate(self, password):
        # return password == self.password
        return check_password_hash(self.password, password)
    
# Dung session_based:
    def init_session(self):
        self.token = gen_session_token()
        self.dump()                                                   
        return self.token                                               # cai init_session can phai gan gia tri cookie cho client nua
    
    def authorize(self, token):                                         # kiem tra xem chung ta co dung la nguoi dang nhap hay khong, kiem tra trong token gui den cho client, login_required
        return token == self.token
    
    def terminate_session(self):                                        # xoa bo thong tin khi log out
        self.token = None                                               # chi don gian la xoa token di
        self.dump()
    
    def __str__(self):                                                  # khi ta dung ham str voi doi tuong nay, thi se tra ve cai gi
        return f'{self.username};{self.password};{self.token}'          # ke ca khi reset roi, van co the dang nhap bang cac token duoc cap
    
    def dump(self):                                                                         # ham de lam viec voi file
        with open(app_config.USER_DB_DIR + '/' + self.username + '.data', 'w') as f:        # mo file de ghi
            f.write(str(self))