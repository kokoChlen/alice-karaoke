import time 
import pygame 
import sys 
from pygame.locals import QUIT, USEREVENT 
 
def read_timecodes(timecode_file): 
    with open(timecode_file, 'r', encoding='utf-8') as file: 
        lines = file.readlines() 
        timecodes_and_lyrics = [] 
 
        for i in range(0, len(lines), 4): 
            line_number = int(lines[i].strip()) 
 
            start_time_str, end_time_str = map(lambda x: x.strip(), lines[i + 1].split('-->')) 
            start_time = convert_time_to_seconds(start_time_str) 
            end_time = convert_time_to_seconds(end_time_str) 
 
            lyric = lines[i + 2].strip() 
 
            timecodes_and_lyrics.append((start_time, end_time, lyric)) 
         
        return timecodes_and_lyrics 
 
def convert_time_to_seconds(time_str): 
    h, m, s = map(float, time_str.replace(',', '.').split(':')) 
    return h * 3600 + m * 60 + s 
 
def display_lyrics_with_audio(timecodes_and_lyrics, audio_file): 
    pygame.mixer.init() 
    pygame.mixer.music.load(audio_file) 
    pygame.mixer.music.play(0) 
 
    pygame.init() 
    width, height = 800, 600 
    screen = pygame.display.set_mode((width, height)) 
    font = pygame.font.Font(None, 36) 
 
    clock = pygame.time.Clock() 
 
    start_time = time.time() 
    current_index = 0 
 
    while current_index < len(timecodes_and_lyrics): 
        current_time = time.time() - start_time 
 
        for event in pygame.event.get(): 
            if event.type == QUIT: 
                pygame.quit() 
                sys.exit() 
 
        start_timecode, end_timecode, lyric = timecodes_and_lyrics[current_index] 
 
        if current_time < start_timecode: 
            # Ожидаем начала следующей строки 
            continue 
        elif current_time < end_timecode: 
            # Отображаем текст 
            screen.fill((0, 0, 0)) 
 
            # Рендерим красный текст 
            red_text = font.render(lyric, True, (255, 0, 0)) 
 
            # Рендерим серый текст следующей строки 
            next_lyric = "" 
            if current_index + 1 < len(timecodes_and_lyrics): 
                next_lyric = timecodes_and_lyrics[current_index + 1][2] 
            gray_font = pygame.font.Font(None, 30) 
            gray_text = gray_font.render(next_lyric, True, (128, 128, 128)) 
 
            # Размещаем текст на экране 
            screen.blit(red_text, (width // 2 - red_text.get_width() // 2, height // 2 - red_text.get_height() // 2)) 
            screen.blit(gray_text, (width // 2 - gray_text.get_width() // 2, height // 2 - gray_text.get_height() // 2 + 50)) 
 
            pygame.display.flip() 
        else: 
            # Ждем следующего тайм-кода 
            current_index += 1 
 
        clock.tick(30)  # 30 FPS 
 
def turn_on(song_link): 
    timecode_file = f"C:\\proect\\songs_data\{song_link}\\subs.txt" 
    lyrics_and_timecodes = read_timecodes(timecode_file) 
    audio_file = f'C:\\proect\\songs_data\{song_link}\\{song_link}.mp3_Instruments.wav' 
    display_lyrics_with_audio(lyrics_and_timecodes, audio_file)
