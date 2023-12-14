from flask import Flask, request, jsonify
from parserYandexMusic import parseMusik
from bitmaker import separate
from textShare import geniusText
#from timecodes import timecodes
from printText import turn_on

app = Flask(__name__)
ask_song = False
karaoke_condition = []
greeting = ['салам', 'привет', 'привт', 'приветик']
asks = ['Караоке', 'Включи караоке', 'Алиса, включи караоке', 'алиса караоке', 'алиса включи караоке']
@app.route('/webhook', methods=['POST'])
def webhook():
    global karaoke_condition
    global ask_song
    data = request.get_json()
    query = data['request']['command']
    if ask_song == True:
        track = music_share(query)
        ask_song = False
        json_track = {
            'response': {
                'text': track,
                'end_session': False
            },
            'version': '1.0'
        }

        return jsonify(json_track)
    
    if karaoke_condition != []:
        
        separate(karaoke_condition[0])
        geniusText(karaoke_condition[0], karaoke_condition[1])
        #timecodes(karaoke_condition[0])
        turn_on(karaoke_condition[0])
        karaoke_condition = []
        
    response = handle_request(query)
    json_response = {
        'response': {
            'text': response,
            'end_session': False
        },
        'version': '1.0'
    }
    
    return jsonify(json_response)


def handle_request(query):
    global ask_song
    if any(i.lower() in query.lower() for i in greeting):
        response = "Привет! Я Яндекс Алиса, чем могу помочь?"
        return response
    
    if 'караоке' in query.lower():
        response = 'Конечно, какую песню вы хотите спеть?'
        ask_song = True
        return response
    
    else:
        response = 'Укажите корректный запрос'
        return response


def music_share(song):
    global karaoke_condition
    tracklink = parseMusik(song) #Находим ссылку на песню в Яндекс музыке
    karaoke_condition.append(tracklink)
    karaoke_condition.append(song)
    return 'Песня найдена, введите "включить" для запуска!'

if __name__ == '__main__':
    app.run()
