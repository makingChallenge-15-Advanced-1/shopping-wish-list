from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://sayhong_db:happy*721@cluster0.cnaox23.mongodb.net/?retryWrites=true&w=majority', 27017, tlsCAFile=ca)
db = client.dbsparta

@app.route('/')
def home():
   return render_template('index.html')

#모든 db 정보 list를 return
@app.route("/shop?list=All", methods=["GET"])                                          
def item_get():                               #url에서 image 추출해서 전달하기
    url = "url"
    image = image_from_url(url) 
    return jsonify({'msg':'접속 성공'})

#url에서 image 추출하는 함수
def image_from_url(url):                   
    return "이것이 이미지"

#db에 새로운 정보를 추가
@app.route("/shop", methods=["POST"])
def item_post():                              #받는 변수 : url, name, price, memo, status
    url_receive = request.form['url_give']    #listId 부여하는 식 넣기
    image = image_from_url(url_receive)       #db 저장 : url, name, price, memo, status, listId
    return jsonify({'msg':'저장 완료!'})

#db의 특정 정보를 수정
@app.route("/shop/listId", methods=["PUT"])    #받는 변수 : url, name, price, memo, status, listId
def item_modify():
    url_receive = request.form['url_give']      #db 저장 : url, name, price, memo, status, listId
    image = image_from_url(url_receive)
    return jsonify({'msg':'수정 완료!'})

#해당 번호의 db 정보를 return
@app.route("/shop/listId", methods=["GET"])        
def item_listId_get():                             #url에서 image 추출해서 전달하기
    listId_receive = request.args.get('listId')
    url = "url"
    image = image_from_url(url)
    return jsonify({'msg':'전달 완료!'})

#해당 번호의 db 정보를 삭제
@app.route("/shop/listId", methods=["DELETE"])
def meta_del():
    listId_receive = request.form['listId_give']
    return jsonify({'msg':'삭제 완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)