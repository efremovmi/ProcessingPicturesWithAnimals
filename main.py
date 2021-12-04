from NN import NN

import PySimpleGUI as sg
import ctypes
import Progress as pr
import tkinter

import os
import shutil

import patoolib
import zipfile

tkinter.Tk().withdraw()

button1 = sg.Input(size=(80, 1), key="InputPath")
button2 = sg.Input(size=(80, 1), key="OutputPath")

layout = [[button1], [sg.Button('Брать из папки'), sg.Button('Брать из архива')],
           [sg.Text('Место выгрузки обработанных фотографий:')],
           [button2], [sg.Button('  Выбрать папку выгрузки   ')],
           [sg.Button('Начать обработку', button_color=('white', 'green')), sg.Button('Выход', button_color=('white', 'red'))]]

window = sg.Window('Обработка фотографий', layout, size=(450, 180))


ImagePreprocessor = NN.NN()
isFolder = True
InputPathToFolder = ""
pathToArchive = ""
path_to_result = ""
while True:  # Event Loop
    event, values = window()
    correct_input = True

    if event is None or event == 'Выход':
        break

    if event == 'Брать из папки' or event == 'Брать из папки0':
        button1.Update(value=tkinter.filedialog.askdirectory())
        isFolder = True
        continue

    if event == 'Брать из архива' or event == 'Брать из архива1':
        button1.Update(value=tkinter.filedialog.askopenfilename())
        isFolder = False
        continue

    if event == '  Выбрать папку выгрузки   ':
        button2.Update(value=tkinter.filedialog.askdirectory())
        continue


    if event is None or event == 'Начать обработку':
        if isFolder:
            InputPathToFolder = values["InputPath"]
        else:
            pathToArchive = values["InputPath"]

        path_to_result = values["OutputPath"]
        if len(path_to_result)  == 0:
            ctypes.windll.user32.MessageBoxW(0, "Вы не выбрали путь до места выгрузки", "Ошибка", 0)

            continue

        # Архив
        if not isFolder:
            pathToArchive = values["InputPath"]
            last = pathToArchive[-4:]

            if len(pathToArchive) == 0:
                ctypes.windll.user32.MessageBoxW(0, "Вы не выбрали архив", "Ошибка", 0)
                correct_input = False

            elif last == ".rar":
                if not os.path.exists(pathToArchive[:-4]):
                    os.mkdir(pathToArchive[:-4])
                patoolib.extract_archive(pathToArchive, outdir=pathToArchive[:-4])
                InputPathToFolder = pathToArchive[:-4]

            elif last == '.zip':
                animalZip = zipfile.ZipFile(pathToArchive)
                animalZip.extractall(pathToArchive[:-4])
                animalZip.close()
                InputPathToFolder = pathToArchive[:-4]

            else:
                ctypes.windll.user32.MessageBoxW(0, "Формат архива должен быть rar или zip", "Ошибка", 0)
                correct_input = False
        else:
            if len(InputPathToFolder) == 0:
                ctypes.windll.user32.MessageBoxW(0, "Вы не выбрали папку", "Ошибка", 0)
                correct_input = False


        if correct_input:
        # ==============================================================================================================


            if not os.path.exists(os.path.join(path_to_result, 'Есть Животные')):
                os.mkdir(os.path.join(path_to_result, 'Есть Животные'))


            if not os.path.exists(os.path.join(path_to_result, 'Нет Животных')):
                os.mkdir(os.path.join(path_to_result, 'Нет Животных'))


            countImages = 0
            for top, dirs, files in os.walk(InputPathToFolder):
                for nm in files:
                    countImages += 1


            i = 0
            countGod = 0
            countBed = 0

            break_i = 0
            exitFlag = False
            print(InputPathToFolder)
            for top, dirs, files in os.walk(InputPathToFolder):
                if exitFlag:
                    break

                for nm in files:
                    if os.path.join(top, nm)[-4:].casefold() == ".png" or os.path.join(top, nm)[-4:].casefold() == ".jpg" or \
                            os.path.join(top, nm)[-5:].casefold() == ".jpeg":


                        flag = ImagePreprocessor.ProcessImage(os.path.join(top, nm))
                        if flag:
                            countGod += 1
                            if not os.path.exists(os.path.join(path_to_result, 'Есть Животные', nm)):
                                shutil.move(os.path.join(top, nm), os.path.join(path_to_result, 'Есть Животные') )
                            #shutil.copy(os.path.join(top, nm),
                            #            os.path.join(path_to_result, 'Есть Животные'))

                        else:
                            countBed += 1
                            if not os.path.exists(os.path.join(path_to_result, 'Нет Животных', nm)):
                                shutil.move(os.path.join(top, nm), os.path.join(path_to_result, 'Нет Животных'))
                            #shutil.copy(os.path.join(top, nm),
                            #            os.path.join(path_to_result, 'Нет Животных'))


                        if not pr.OneLineProgressMeter('Обработка:',
                                                       i + 1, countImages,
                                                       'Обраматываемая фотография:',
                                                       'Обработано фотографий:',
                                                       orientation='h',
                                                       bar_color=('white', 'red'),
                                                       ):
                            exitFlag = True
                            break

                        i += 1

            if i == countImages - 1:
                # Processing end
                # Output results
                ctypes.windll.user32.MessageBoxW(0, "Обработка закончена!\nКоличество фотографий с животными: {}\n"
                                                    "Количество фотографий без животных: {}".format(countGod, countBed),
                                                    "Сообщение", 0)
            else:
                ctypes.windll.user32.MessageBoxW(0, "Вы отменили обработку.\nКоличество фотографий с животными: {}\n"
                                                    "Количество фотографий без животных: {}".format(countGod, countBed),
                                                    "Ошибка", 0)
        # ======================================================================================================
        if not isFolder:
            shutil.rmtree(pathToArchive[:-4])