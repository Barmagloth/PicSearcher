import mysql.connector
import numpy as np
import torch
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import io

#device = "cuda" if torch.cuda.is_available() else "cpu"
#model, preprocess = clip.load('ViT-B/32', device=device)



# Change this to your own path and credentials
def db_connect(host='localhost',
               user='root',
               password='1',
               database='image_db'):
    connection = None
    error = None
    try:
        connection = mysql.connector.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database,
                                     )
    except Exception as e:
        error = str(e)
    return connection, error

def create_table(cursor):
    """
    Create a table if it does not exist
    """

    result = False
    try:
        cursor.execute("SHOW TABLES")
        for db in cursor:
            if 'images' in db:
                print('Table already exists')
                result = True
        if result is False:
            print('Table does not exist yet')
            print('Creating table')
            # Создаем таблицу, если она еще не существует
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                path VARCHAR(255),
                width INT,
                height INT,
                shape VARCHAR(255),
                features BLOB,
                UNIQUE (name, path, width, height, shape)
            )
            """)
            #cursor.execute("ALTER TABLE images ADD CONSTRAINT uc_images UNIQUE (name, path, width, height, shape)")
    except Exception as e:
        print('Failed to create table')

def image_preprocessor_clip(path, device, model, preprocess):
    """
    Preprocess an image using CLIP.
    """
    image = Image.open(path)
    width, height = image.size
    if width > 99 and height > 99:
        image_input = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image_input)
    return image_features

def select_folder():
    """
    Open a dialog box to select a folder.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the TkInter window.
    folder = filedialog.askdirectory(title="Select a Folder of images to index")  # Open a dialog box to select a folder.
    return folder

def serialize(tensor):
    """
    Serialize a tensor into a string.
    """
    tensor = tensor.cpu().numpy()
    buffer = io.BytesIO()
    torch.save(tensor, buffer)
    return buffer.getvalue()

def serialize2(tensor):
    """
    Serialize a tensor into a string.
    """
    tensor_binary = tf.io.serialize_tensor(tensor).numpy()
    return tensor_binary

def deserialize(string):
    """
    Deserialize a string into a tensor.
    """
    buffer = io.BytesIO(string)
    numpy_tensor = torch.load(buffer)
    return torch.from_numpy(numpy_tensor)

def deserialize2(string):
    """
    Deserialize a string into a tensor.
    """
    tensor = tf.io.parse_tensor(string, out_type=tf.float32)
    return tensor
