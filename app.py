from flask import Flask, render_template, request
import urllib.request
import urllib.parse
import json
from fuzzywuzzy import fuzz

app = Flask(__name__)

# 네이버 API 정보
client_id = "XnCjDjHWqFXcYPoVmYLz"
client_secret = "mIcP8kec4f"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        korean_name = request.form['korean_name']

        encText = urllib.parse.quote(korean_name)
        url = "https://openapi.naver.com/v1/krdict/romanization?query=" + encText

        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", client_id)
        req.add_header("X-Naver-Client-Secret", client_secret)

        response = urllib.request.urlopen(req)
        rescode = response.getcode()

        if rescode == 200:
            response_body = response.read()
            json_dict = json.loads(response_body.decode('utf-8'))

            result = json_dict['aResult'][0]
            name_items = result['aItems']

            names = [name_item['name'] for name_item in name_items]

            english_name = names[0]
            print("영어 이름:", english_name)

            json_file_path = 'popular_embeddings.json'
            input_name = english_name

            with open(json_file_path, 'r') as json_file:
                name_data = json.load(json_file)

            similarity_scores = []
            for name, embedding in name_data.items():
                score = fuzz.ratio(input_name.lower(), name.lower())
                similarity_scores.append((name, score))

            similarity_scores.sort(key=lambda x: x[1], reverse=True)
            most_similar_names = [score[0] for score in similarity_scores[:5]]

            return render_template('result.html', input_name=korean_name, english_name=english_name, similarity_scores=similarity_scores[:5])

        else:
            return "API 요청 실패"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)