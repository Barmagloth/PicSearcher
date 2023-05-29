from CLIP import clip
from data_processors import *
import os
from PIL import Image
from torchvision.transforms import Compose, Resize, Normalize, ToTensor

min_height = int(input('Input minimal height of images: '))
min_width = int(input('Input minimal width of images: '))

images_counter = 0

# Connect to DB
connection, error = db_connect()
if error is not None:
    print('DB connection error')
    print(error)

else:
    # Create db cursor
    cursor = connection.cursor()

    # Create table if not exists
    create_table(cursor)

    # Choose root folder
    folder = select_folder()

    # Loading CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load('ViT-B/32', device=device)

    # Walk through folder and save image features
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg") or filename.endswith(".JPG") or filename.endswith(".PNG") or filename.endswith(".JPEG"):
                pass
                images_counter += 1
                try:
                    path = os.path.normpath(os.path.join(dirpath, filename))
                    #print(path)
                    image = Image.open(path)
                    width, height = image.size
                    #print(width, height)

                    # Except for images with width and height less than 64
                    if width >= min_width and height >= min_height:
                        #image.show()

                        image_input = preprocess(image).unsqueeze(0).to(device)

                        # Getting a features tensor from an image
                        with torch.no_grad():
                            image_features = model.encode_image(image_input)
                            # Shape before serialization
                            shape = str(image_features.shape[0])+' '+str(image_features.shape[1])
                            image_features_bytes = serialize(image_features)

                        # Saving image features to DB

                        sql = """
                        INSERT INTO images (name, path, width, height, shape, features)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name=VALUES(name),
                            path=VALUES(path),
                            width=VALUES(width),
                            height=VALUES(height),
                            shape=VALUES(shape),
                            features=VALUES(features)
                        """
                        params = (filename, path, width, height, shape, image_features_bytes)


                        # Ignoring duplicates

                        try:
                            duplicates = """
                            INSERT IGNORE INTO images (name, path, width, height, shape)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            dupl_params = (filename, path, width, height, shape)
                            #cursor.execute(duplicates, dupl_params)
                            cursor.execute(sql, params)
                            print(f"Image processing: {path}")

                        except Exception as e:
                            print(f"Data writing error: {e}")
                            connection.rollback()
                        else:
                            connection.commit()
                            print(f"Image processed: {path}")
                            images_counter += 1
                            print()

                except Exception as e:
                    print(f"Image not processed: {path}: {e}")
                    connection.rollback()
                    continue

if connection is not None:
    print(f"Images processed: {images_counter}")
    connection.close()
    print('Connection closed')
