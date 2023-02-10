from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

# login을 위한 모듈
from datetime import datetime, timedelta, timezone 
from flask_jwt_extended import *

#password 암호화
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

#mongo db library
from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://sayhong_db:happy*721@cluster0.cnaox23.mongodb.net/?retryWrites=true&w=majority', 27017, tlsCAFile=ca)
db = client.dbsparta

# JWT 매니저 활성화
app.config.update(DEBUG = True, JWT_SECRET_KEY = "spartateam" )
# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False     #Configure application to store JWTs in cookies
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config['JWT_ACCESS_COOKIE_PATH'] = '/' # access cookie를 보관할 url (Frontend 기준)
app.config['JWT_REFRESH_COOKIE_PATH'] = '/' # refresh cookie를 보관할 url (Frontend 기준)

app.config['JWT_HEADER_TYPE'] = None

jwt = JWTManager(app)

#route 설정
@app.route('/')    #첫화면
def home():     
    return render_template('login.html')
@app.route('/index')    #wishlist page
def index():
    return render_template('index.html')
@app.route('/register')    #회원가입 page
def open_register_page():
    return render_template('register.html')

############################################
#               로그인 API                 #
############################################

#회원 등록
@app.route("/user/register", methods=["POST"])      #register.html의 register()에서 call
def register():
    # 회원정보 생성
    user_id = request.form['user_id_give']
    user_pwd = request.form['user_pwd_give']
    pwd_hash = bcrypt.generate_password_hash(user_pwd)   # 비밀번호 암호화
    doc = {
        'user_id' : user_id,
        'user_pwd' : pwd_hash
    }
    db.users.insert_one(doc)        #db에 회원정보 등록
    return jsonify({'msg':'등록 완료'})

# 동일한 user_id를 가진 회원이 없는지 확인
@app.route("/user/user_id_check", methods=["GET"])      #register.html의 check_user_id()에서 call
def register_check_id():
    user_id = request.args.get('user_id')
    check_id = db.users.find_one({'user_id':user_id})
    if check_id is not None:
        return jsonify({'result' : "fail"})
    return jsonify({'result' : "success"})

#로그인하기
@app.route("/user/login", methods=["POST"])   #login.html의 login() 에서 call
def login():
    # 사용자가 입력한 id, password
    user_id = request.form['user_id_give']
    user_pwd = request.form['user_pwd_give']

    #db에 저장된 password와 비교
    #같은 password를 입력해도 hash값을 다를 수 있으므로 user_pwd는 해쉬화 하지 않는다.
    #check_password_hash 함수를 이용하여 hash된 값과 원래 값이 동일한 지 비교 가능하다. 
    user = db.users.find_one({'user_id': user_id})
    origin_pwd = user['user_pwd']
    check_pwd = bcrypt.check_password_hash(origin_pwd, user_pwd)

    if check_pwd is False:
        return jsonify({'msg': '아이디나 비밀번호가 잘못되었습니다!!', 'login': False})

    # Create the tokens we will be sending back to the user
    access_token = create_access_token(identity=user_id, expires_delta=False)
    refresh_token = create_refresh_token(identity=user_id)

    response = jsonify({'msg':'로그인 성공', 'login': True})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200

# 로그아웃
@app.route('/token/remove', methods=['POST'])           #index.html의 logout()에서 call
def logout():
    response = jsonify({'msg':'로그아웃 성공', 'logout': True})
    unset_jwt_cookies(response)     #delete the cookies in order to logout
    return response, 200



############################################
#               위시리스트 API             #
############################################

#url에서 image 추출하는 함수
def image_from_url(url_receive):
    headers = {        
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    try:
        data = requests.get(url_receive, headers=headers, timeout=1)
    except requests.exceptions.Timeout:         #메타 데이터를 1초 내 로드 실패시 디폴트 이미지 return
        image = "https://t3.ftcdn.net/jpg/04/62/93/66/360_F_462936689_BpEEcxfgMuYPfTaIAOC1tCDurmsno7Sp.jpg"
        return image

    soup = BeautifulSoup(data.text, 'html.parser')
    image = soup.select_one('meta[property="og:image"]')['content']
    return image

#GET API 
#조건에 맞는 list를 return
@app.route("/wishlist", methods=["GET"])
@jwt_required(optional=True)
def wishlist_get():
    current_user_id = get_jwt()['sub']      #로그인 회원의 id
    list_method = request.args.get('list')
    if list_method == 'all':
        wishlist = list(db.wishlist.find({'user_id' : current_user_id},{'_id':False}))
    elif list_method == 'toBuy':
        wishlist = list(db.wishlist.find({'user_id' : current_user_id, 'status': 'toBuy'}, {'_id': False}))
    elif list_method == 'hold':
        wishlist = list(db.wishlist.find({'user_id' : current_user_id, 'status': 'hold'}, {'_id': False}))
    elif list_method == 'order':
        wishlist = list(db.wishlist.find({'user_id' : current_user_id, 'status': 'order'}, {'_id': False}))

    for item in wishlist:  
        url = item['url']
        image = image_from_url(url) 
        item['image'] = image
    return jsonify({'wishlist':wishlist, 'current_user_id':current_user_id})

#해당 번호의 db 정보를 return
@app.route("/wishlist/{listId}", methods=["GET"])
def wishlist_listId_get():                             
    listId_receive = request.args.get('listId_give')
    listId_item = db.wishlist.find_one({'listId': int(listId_receive)}, {'_id': False})
    url = listId_item['url']
    image = image_from_url(url)
    listId_item['image'] = image
    return jsonify({'listId_item':listId_item})


#POST API
#db에 새로운 정보를 추가
@app.route("/wishlist", methods=["POST"])
def wishlist_post():                              #받는 변수 : url, name, price, memo, status
    current_user = request.form['current_user_give']
    url_receive = request.form['url_give']          
    name_receive = request.form['name_give']        
    price_receive = request.form['price_give']
    memo_receive = request.form['memo_give']
    status_receive = request.form['status_give']

    all_wishlist = list(db.wishlist.find({}, {'_id': False}))         #listId 부여
    sort_wishlist = sorted(all_wishlist, key=lambda d: d['listId'])

    if len(sort_wishlist) == 0:
        listId = 1
    else:
        count = 1
        for item in sort_wishlist:
            if item['listId'] == count:
                count += 1
                listId = count
            else:
                listId = count
                break

    doc = {                                 #db 저장 : url, name, price, memo, status, listId
        'url': url_receive,
        'name' : name_receive,
        'price' : price_receive,
        'memo' : memo_receive,
        'status' : status_receive,
        'listId' : listId,
        'user_id' : current_user
    }
    db.wishlist.insert_one(doc)
    return jsonify({'msg':'저장 완료!'})


#PUT API
#db의 특정 정보를 수정
@app.route("/wishlist/{listId}", methods=["PUT"])    #받는 변수 : url, name, price, memo, status, listId
def wishlist_modify():
    url_receive = request.form['url_give']          
    name_receive = request.form['name_give']        
    price_receive = request.form['price_give']
    memo_receive = request.form['memo_give']
    status_receive = request.form['status_give']
    listId_receive = request.form['listId_give']

    doc = {                                 #db 저장 : url, name, price, memo, status, listId
        'url': url_receive,
        'name' : name_receive,
        'price' : price_receive,
        'memo' : memo_receive,
        'status' : status_receive,
        'listId' : int(listId_receive)
    }
    db.wishlist.update_one({'listId':int(listId_receive)},{'$set':doc})
    return jsonify({'msg':'수정 완료!'})

#listId에 해당하는 db의 status만 수정
@app.route("/wishlist/{listId}/status", methods=["PUT"])    #받는 변수 : url, name, price, memo, status, listId
def wishlist_modify_status():
    status_receive = request.form['status_give']
    listId_receive = request.form['listId_give']
    db.wishlist.update_one({'listId':int(listId_receive)},{'$set':{'listId':listId_receive}})
    return jsonify({'msg':'수정 완료!'})

#DELETE API
#해당 번호의 db 정보를 삭제
@app.route("/wishlist/{listId}", methods=["DELETE"])
def wishlist_del():
    listId_receive = request.form['listId_give']
    db.wishlist.delete_one({'listId': int(listId_receive)})
    return jsonify({'msg':'삭제 완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)