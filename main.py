import PySimpleGUI as sg
import ctypes
import Progress as pr
import shutil
import os
from OpenCV import NN

layout = [[sg.Text('Выберите, откуда читать данные(архив или папка):')],
          [sg.Radio('Архив', "RADIO1", default=False, key="Archive"),
           sg.Input(size=(100, 1), key="InputPathToArchive"), sg.FileBrowse(button_text='Выбрать файл')],
          [sg.Radio('Папка', "RADIO1", default=True, key="Folder"),
           sg.Input(size=(100, 1), key="InputPathToFolder"), sg.FolderBrowse(button_text='Выбрать папку')],

          [sg.Text('Место выгрузки обработанных фотографий:')],
          [sg.Input(do_not_clear=True, size=(111, 1)), sg.FolderBrowse(button_text='Выбрать папку')],
          [sg.Button('Начать обработку', button_color=('white', 'green')),  sg.Button('Выход')]]


window = sg.Window('Обработка фотографий', size=(950, 200)).Layout(layout).Finalize()


ImagePreprocessor = NN()


while True:  # Event Loop
    event, values = window.Read()
    print(event, values)

    if event is None or event == 'Выход':
        break

    # path_to_result = values['Выбрать папку0']
    path_to_result = 'C:/Users/genri/Desktop/WildHack/Result'
    if len(path_to_result) == 0:
        ctypes.windll.user32.MessageBoxW(0, "Вы не выбрали путь до места выгрузки", "Ошибка", 0)
        continue

    if event is None or event == 'Начать обработку':

        # Архив
        if values["Archive"]:
            pathToArchive = values["InputPathToArchive"]
            last = pathToArchive[-4:]

            if len(pathToArchive) == 0:
                ctypes.windll.user32.MessageBoxW(0, "Вы не выбрали архив", "Ошибка", 0)

            elif last != ".zip" and last != ".rar":
                ctypes.windll.user32.MessageBoxW(0, "Формат архива должен быть rar или zip", "Ошибка", 0)

            else:
                # ======================================================================================================
                # Здесь обработка архива
                #

                countImages = 1000
                for i in range(countImages):
                    #

                    #
                    if not pr.OneLineProgressMeter('Обработка:',
                                                      i + 1, countImages,
                                                      'Обработано фотографий',
                                                      orientation='h',
                                                      # no_titlebar=True,
                                                      # grab_anywhere=True,
                                                      bar_color=('white', 'red'),
                                                      ):
                        break


                if i == countImages - 1:
                    # Обработка завершена.
                    # Результаты.
                    ctypes.windll.user32.MessageBoxW(0, "Обработка закончена!",
                                                 "Сообщение", 0)
                else:
                    ctypes.windll.user32.MessageBoxW(0, "Вы отменили обработку.",
                                                     "Ошибка", 0)
                # ======================================================================================================



        # Папка
        if values["Folder"]:
            print(values)
            # InputPathToFolder = values["InputPathToFolder"]
            InputPathToFolder = 'C:/Users/genri/Desktop/WildHack/Фото/1'

            if len(InputPathToFolder) == 0:
                print(1)
                ctypes.windll.user32.MessageBoxW(0, "Вы не выбрали папку", "Ошибка", 0)


            else:
                # ======================================================================================================
                # Здесь обработка папки
                #

                if not os.path.exists(os.path.join(path_to_result, 'Есть Животные')):
                    os.mkdir(os.path.join(path_to_result, 'Есть Животные'))


                if not os.path.exists(os.path.join(path_to_result, 'Нет Животных')):
                    os.mkdir(os.path.join(path_to_result, 'Нет Животных'))



                imagesList = os.listdir(InputPathToFolder)

                countImages = len(imagesList)

                i = 0
                countGod = 0
                countBed = 0

                break_i = 0
                for name in imagesList:


                    if name[-4:].casefold() == ".png" or name[-4:].casefold() == ".jpg" or name[-5:].casefold() == ".jpeg":
                        if ImagePreprocessor.ProcessImage(os.path.join(InputPathToFolder, name)):
                            countGod += 1
                            # shutil.move(os.path.join(InputPathToFolder, name), os.path.join(path_to_result, 'Есть Животные') )
                            shutil.copy(os.path.join(InputPathToFolder, name), os.path.join(path_to_result, 'Есть Животные') )
                        else:
                            countBed += 1
                            # shutil.move( os.path.join(InputPathToFolder, name), os.path.join(path_to_result, 'Нет Животных'))
                            shutil.copy(os.path.join(InputPathToFolder, name), os.path.join(path_to_result, 'Нет Животных') )



                    if not pr.OneLineProgressMeter('Обработка:',
                                                   i + 1, countImages,
                                                   'Обраматываемая фотография:',
                                                   'Обработано фотографий:',
                                                   orientation='h',
                                                   # no_titlebar=True,
                                                   # grab_anywhere=True,
                                                   bar_color=('white', 'red'),
                                                   ):
                        break

                    i += 1
                if i == countImages - 1:
                    # Обработка завершена.
                    # Результаты.
                    ctypes.windll.user32.MessageBoxW(0, "Обработка закончена!\nКоличество фотографий с животными: {}\n"
                                                        "Количество фотографий без животных: {}".format(countGod, countBed),
                                                     "Сообщение", 0)
                else:
                    ctypes.windll.user32.MessageBoxW(0, "Вы отменили обработку.",
                                                     "Ошибка", 0)
                # ======================================================================================================



