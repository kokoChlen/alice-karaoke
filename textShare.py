import requests
from bs4 import BeautifulSoup

def fullName(song):

    while True:
        try:
            res = requests.get(f'https://music.yandex.ru/search?text={song}')
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                song_autor = soup.find('a', class_ = 'deco-link deco-link_muted')
                autor = song_autor.get('title')
                full_song = soup.find('div', class_ = 'd-track__name')
                song = full_song.get('title')
                full_Track = autor + ' ' + song
                return full_Track
            break
        except:
            pass


def getGeniusLink(song):
    fName = fullName(song)
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent" : USER_AGENT}
    res = requests.get(f'https://www.google.com/search?q={fName}+genius lyrics', headers = headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        geniusLink = soup.find('a', jsname = 'UWckNb')
        geniusLink = geniusLink['href']
        return (geniusLink)


def should_exclude_line(line):
    # Проверяем, находится ли строка в квадратных скобках (сторка припев, куплети т.д.)
    if '[' in line and ']' in line:
        return True

    return False

def geniusText(song_link, song):
    geniusLink = getGeniusLink(song)
    res = requests.get(geniusLink)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        lyrics_containers = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
        for lyrics_container in lyrics_containers:
            # Открываем файл для записи
            with open(f'C:\\proect\\songs_data\{song_link}\\{song_link}.txt', 'a', encoding='utf-8') as file: 
                # Ищем все строки текста песни
                lines = lyrics_container.stripped_strings
                # Записываем только те строки, которые не подпадают под условия исключения
                for line in lines:
                    if not should_exclude_line(line):
                        file.write(line + '\n')

        print('Текст успешно записан')
        
