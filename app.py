from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('db 정보', 27017, tlsCAFile=ca)
db = client.dbsparta

@app.route('/')
def home():
    return render_template('index.html')


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
#모든 db 정보 list를 return
@app.route("/wishlist?list=All", methods=["GET"])                                          
def wishlist_get():                               #url에서 image 추출해서 전달하기
    all_wishlist = list(db.wishlist.find({}, {'_id': False}))
    for item in all_wishlist:
        url = item['url']
        image = image_from_url(url) 
        item['image'] = image
    return jsonify({'wishlist':all_wishlist})

#당장구매 db 정보 list를 return
@app.route("/wishlist?list=ready", methods=["GET"])                                          
def wishlist_get_ready():                               #url에서 image 추출해서 전달하기
    ready_wishlist = list(db.wishlist.find({'status':'ready'}, {'_id': False}))
    for item in ready_wishlist:
        url = item['url']
        image = image_from_url(url) 
        item['image'] = image
    return jsonify({'ready_wishlist':ready_wishlist})

#보류한 db 정보 list를 return
@app.route("/wishlist?list=refer", methods=["GET"])                                          
def wishlist_get_refer():                               #url에서 image 추출해서 전달하기
    refer_wishlist = list(db.wishlist.find({'status':'refer'}, {'_id': False}))
    for item in refer_wishlist:
        url = item['url']
        image = image_from_url(url) 
        item['image'] = image
    return jsonify({'refer_wishlist':refer_wishlist})

#구매완료 db 정보 list를 return
@app.route("/wishlist?list=done", methods=["GET"])                                          
def wishlist_get_done():                               #url에서 image 추출해서 전달하기
    done_wishlist = list(db.wishlist.find({'status':'done'}, {'_id': False}))
    for item in done_wishlist:
        url = item['url']
        image = image_from_url(url) 
        item['image'] = image
    return jsonify({'donelist':done_wishlist})

#해당 번호의 db 정보를 return
@app.route("/wishlist/listId", methods=["GET"])        
def wishlist_listId_get():                             #url에서 image 추출해서 전달하기
    listId_receive = request.args.get('listId')
    listId_item = db.wishlist.find_one({'listId': int(listId_receive)})
    url = listId_item['url']
    image = image_from_url(url)
    listId_item['image'] = image
    return jsonify({'listId_item':listId_item})


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
    sort_wishlist = sorted(all_wishlist, key=lambda d: d['num'])

    if len(sort_wishlist == 0):
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
@app.route("/wishlist/listId", methods=["PUT"])    #받는 변수 : url, name, price, memo, status, listId
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
        'listId' : listId_receive
    }
    db.users.update_one({'listId':int(listId_receive)},{'$set':doc})
    return jsonify({'msg':'수정 완료!'})

#상태만 수정하는 API 추가 하기

#DELETE API
#해당 번호의 db 정보를 삭제
@app.route("/wishlist/listId", methods=["DELETE"])
def wishlist_del():
    listId_receive = request.form['listId_give']
    db.wishlist.delete_one({'listId':int(listId_receive)})
    return jsonify({'msg':'삭제 완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)