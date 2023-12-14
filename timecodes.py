import subprocess
def timecodes(song):
    vocal_locate = f'C:\\proect\\songs_data\{song}\\{song}.mp3_Vocals.wav'
    text_locate = f'C:\\proect\\songs_data\{song}\\{song}.txt'
    command = f'python -m aeneas.tools.execute_task {vocal_locate} {text_locate} "task_language=rus|os_task_file_format=srt|is_text_type=plain" C:\\proect\\songs_data\{song}\\subs.txt'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

    # Вывести результат
    print(result.stdout)
