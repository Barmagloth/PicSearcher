import torch
from PIL import Image
import numpy as np
from CLIP import clip
import pymysql.cursors
#from clip.simple_tokenizer import SimpleTokenizer
from scipy.spatial import distance
from data_processors import *

def search_tag(input_text='cat', treshold_percent=95):
    """
    Searching for the images that have the features similar to the input text
    :param input_text:
    :param treshold_percent:
    :return:
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, transform = clip.load("ViT-B/32", device=device)

    threshold = 0.95  # Defines the default treshold for the similarity
    matching_paths = []
    dist = []
    names = []
    treshold = treshold_percent/100

    text_encoded = clip.tokenize(input_text).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_encoded)

    # Connect to DB
    connection, error = db_connect()


    if error is not None:
        print('DB connection error')
        print(error)

    else:
        cursor = connection.cursor()

        # Extract all the images features from the DB
        cursor.execute("SELECT path, features FROM images")
        rows = cursor.fetchall()
        for row in rows:
            path = row[0]
            features = row[1]
            image_features = deserialize(features)
            image_features = image_features.to(device)

            # Compare the image features with the text features
            dist.append(100.0 * image_features @ text_features.T)
            names.append(path)

        dist = torch.cat(dist)

        min_val = dist.min()
        max_val = dist.max()

        # Normalize the distance
        normalized_tensor = (dist - min_val) / (max_val - min_val)

        noramalized_list = normalized_tensor.tolist()
        for index, num in enumerate(noramalized_list):
            if num[0] > treshold:
                matching_paths.append(names[index])
                #print()
                
    #  Close the connection
    if connection is not None:
        connection.close()
        print('Connection closed')

    return matching_paths