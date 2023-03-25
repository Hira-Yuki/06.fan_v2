from bson.objectid import ObjectId
from bson.json_util import dumps
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
from pymongo import MongoClient
import certifi # 인증서와 관련된 라이브러리
import requests

ca = certifi.where() # 맥 개발 환경에서 몽고디비에 접속할 수 없을때 사용하는 추가 코드 'tlsCAFile=ca'와 세트임.
client = MongoClient('mongodb+srv://sparta:test@cluster0.ervhju3.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta # DB에서 dbsparta 클라이언트를 사용할 것임을 나타냄

# 크롤링 url : https://www.genie.co.kr/search/searchMain?query=

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/guestbook", methods=["POST"])
def guestbook_post():
    name_receive = request.form['name_give']
    comment_receive = request.form['comment_give']
    likes_receive = int(request.form['likes_give'])
    select_artist_receive = request.form['select_artist_give']
    doc = {
        'name' : name_receive,
        'comment' : comment_receive,
        'likes' : likes_receive,
        'artist': select_artist_receive
    }
    db.fan.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})

@app.route("/guestbook", methods=["GET", "POST"])
def guestbook_get():
    
    artist = request.args.get('artist')
    if artist:
        all_comments = list(db.fan.find({"artist": artist}))
    else:
        all_comments = list(db.fan.find())
    
    # all_comments = list(db.fan.find())

    for comment in all_comments:
        comment['_id'] = str(comment['_id']) # ObjectId를 str 형태로 변환합니다.
    return dumps({'result': all_comments})

@app.route("/popular", methods=["GET", "POST"])
def popular(): # 인기곡 10개를 가져오기 위한 코드

    url = "https://www.genie.co.kr/detail/artistInfo?xxnm=67872918"

    artist = request.args.get('artist')
    if artist == 'IU' :
        url = "https://www.genie.co.kr/detail/artistInfo?xxnm=67872918"
    elif artist == 'bts' :
        url = "https://www.genie.co.kr/detail/artistInfo?xxnm=80221635"
    elif artist == 'hyoshin' :
        url = "https://www.genie.co.kr/detail/artistInfo?xxnm=14945862"
    else :
        url = "https://www.genie.co.kr/detail/artistInfo?xxnm=67872918"

    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url,headers=headers)
    
    soup = BeautifulSoup(data.text, 'html.parser')
    song_list = soup.select('#body-content > div.songlist-box > div.music-list-wrap > table > tbody > tr')
    pop_music = []
    for i in song_list:
        pop_music.append(i.select_one('td.info > a.title.ellipsis').text.replace("TITLE","").strip())

    pop_music_dict_list = []
    for song in pop_music:
        song_dict = {"song": song}
        pop_music_dict_list.append(song_dict)

    return jsonify({'result': pop_music_dict_list})

@app.route('/add_like', methods=['POST'])
def add_like_post(): #좋아요 버튼을 누르면 해당 좋아요 값이 1씩 증가함
    search_id_receive = request.form['search_id_give']
    db.fan.update_one({'_id': ObjectId(search_id_receive)}, {'$inc': {'likes': 1}})
    
    return jsonify({'msg': '좋아요!를 했습니다.'})

@app.route('/artist_select', methods=['POST'])
def select():
    artist_name_receive = request.form['artist_name_give']
    print(artist_name_receive)
    return jsonify({'result':'success', 'msg': '이 요청은 POST!'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True)