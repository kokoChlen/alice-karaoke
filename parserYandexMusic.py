import requests
from bs4 import BeautifulSoup

def parseMusik(song):
    need_remove = ['/', ':', '-', '<', '>', '*', '?']
    link = 'httpsmusic.yandex.ru'
    
    tries = 0
    max_tries = 50  # Максимальное количество попыток

    while tries < max_tries:
        try:
            res = requests.get(f'https://music.yandex.ru/search?text={song}')
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                track_link = soup.find('a', class_='d-track__title deco-link deco-link_stronger')
                result = link + track_link.get('href')
                result = result.replace('/', '')
                return result
        except Exception as e:
            pass
        
        # Если возникла ошибка, увеличиваем количество попыток и продолжаем
        tries += 1

    # Если после всех попыток не удалось получить результат, возвращаем None или выполняем другие действия
    return None

