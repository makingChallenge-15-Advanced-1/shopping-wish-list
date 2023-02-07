from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
import certifi
ca = certifi.where()

# 몽고DB TypeError
# TypeError: Object of type ObjectId is not JSON serializable
from bson.json_util import dumps

client = MongoClient('mongodb+srv://test:sparta@Cluster0.kwrmlin.mongodb.net/?retryWrites=true&w=majority', 27017, tlsCAFile=ca)
db = client.dbsparta

@app.route('/')
def home():
    return render_template('index.html')

#branch에 업로드해보자!!
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
#조건에 맞는 list를 return -> 아직 해결 안됨.(16:50)
@app.route("/wishlist", methods=["GET"])
def wishlist_get():
    list_method = request.args.get('list')
    if list_method == 'all':
        wishlist = list(db.wishlist.find({}, {'_id': False}))
    elif list_method == 'toBuy':
        wishlist = list(db.wishlist.find({'status': 'toBuy'}, {'_id': False}))
    elif list_method == 'hold':
        wishlist = list(db.wishlist.find({'status': 'hold'}, {'_id': False}))
    elif list_method == 'order':
        wishlist = list(db.wishlist.find({'status': 'order'}, {'_id': False}))

    for item in wishlist:
        url = item['url']
        image = image_from_url(url) 
        item['image'] = image
    return jsonify({'wishlist':wishlist})

#해당 번호의 db 정보를 return
@app.route("/wishlist/{listId}", methods=["GET"])
def wishlist_listId_get():                             
    listId_receive = request.args.get('listId_give')
    listId_item = db.wishlist.find_one({'listId': int(listId_receive)})
    url = listId_item['url']
    image = image_from_url(url)
    listId_item['image'] = image
    return jsonify({'listId_item': dumps(listId_item)}) # TypeError 해결용


#POST API
#db에 새로운 정보를 추가
@app.route("/wishlist", methods=["POST"])
def wishlist_post():                              #받는 변수 : url, name, price, memo, status
    url_receive = request.form['url_give']          
    name_receive = request.form['name_give']        
    price_receive = request.form['price_give']
    memo_receive = request.form['memo_give']
    status_receive = request.form['status_give']

    all_wishlist = list(db.wishlist.find({}, {'_id': False}))         #37~50 : listId 부여
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
        'listId' : listId
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