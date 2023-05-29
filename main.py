from Searcher import *
import PySimpleGUI as sg
from PIL import Image
import io
import base64

sg.theme('DarkBrown')

def convert_to_bytes(file_or_bytes, resize=None):
    """
    Converts a file or bytes to bytes
    :param file_or_bytes:
    :param resize:
    :return:
    """
    if isinstance(file_or_bytes, str):
        img = Image.open(file_or_bytes)
    else:
        try:
            img = Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), Image.LANCZOS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

# Define layout
layout1 = [[sg.Text("Text"), sg.Input(key='-TEXT-')],
           [sg.Column(
               [[sg.Text("Threshold percent: ", size=(15,1))]], vertical_alignment='b',),
            sg.Column(
                [[sg.Slider(range=(0,100), orientation='h', default_value = 97, key='-THRESHOLD-', size=(23,20))]])],
           [sg.Button("OK", size = (10,1)), sg.Button("\\/",  size = (10,1)), sg.Button("/\\", size = (10,1))],
           [sg.Listbox(values=[], enable_events=True, size=(49,38), horizontal_scroll=True, key='-FILE LIST-')]] # set fixed size for image
layout2 = [[sg.Image(key='-IMAGE-', size=(800, 800))]]
layout = [[sg.pin(sg.Column(layout1, size = (400,800))), sg.Column(layout2)]]
window = sg.Window("PicSearcher by Barmagloth, 2023", layout,  size=(1200,800))

# Initialise current selected index

file_list = None

# Event Loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == 'OK': # Search for files with the given text and threshold
        selected_index = 0
        text = values['-TEXT-']
        if text == '':
            text = 'cat'
        file_list = search_tag(text, int(values['-THRESHOLD-']))
        #print(f"File list:  {file_list}")
        window['-FILE LIST-'].update(file_list)
        if file_list:
            print(file_list)
            filename = file_list[selected_index]
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(800, 800)))
            window['-FILE LIST-'].update(set_to_index=selected_index)
        else:
            sg.MsgBox("No files found")
    if file_list:  # Check if there are files to display

        if event == '\\/' or event == 'Down:40':  # Event triggered when the \/ or down arrow key is pressed
            if file_list and selected_index < len(file_list) - 1:  # Check if there are files and index is not at the end
                selected_index += 1
                filename = file_list[selected_index]
                #print(selected_index, filename)
                window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(800, 800)))
                window['-FILE LIST-'].update(set_to_index=selected_index)


        if event == '/\\' or event == 'Up:38':  # Event triggered when the /\ or up arrow key is pressed
            if file_list and selected_index > 0:  # Check if there are files and index is not at the beginning
                selected_index -= 1
                filename = file_list[selected_index]
                #print(selected_index, filename)
                window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(800, 800)))
                window['-FILE LIST-'].update(set_to_index=selected_index)
        if event == '-FILE LIST-':  # Event triggered when a file is chosen from the listbox
            try:
                filename = values['-FILE LIST-'][0]
                selected_index = file_list.index(filename)
                window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(800, 800)))
            except Exception as E:
                print(f"** Error {E} **")
            pass                    # An error happened trying to open the file. Skip this file

window.close()
