import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow import keras
import cv2
import numpy as np


class ChessImageClassifier:

    occ_model = None
    piece_model = None

    occ_labels = ["0", "."]
    piece_labels = ['b', 'k', 'n', 'p', 'q', 'r', 'B', 'K', 'N', 'P', 'Q', 'R']

    def __init__(self):
        # Load both models from a file
        self.occ_model = keras.models.load_model('Models/VGG16_Occupation.keras')
        self.piece_model = keras.models.load_model('Models/Xception_Piece.keras')

    # Preprocess an image to be classified
    def preprocess_cnn_image(self, images):
        # Resize each image to 125x125 and return as numpy array
        images = list(map(lambda img: cv2.cvtColor(img, cv2.COLOR_GRAY2RGB), images))
        images = list(map(lambda img: cv2.resize(img, (125, 125)), images))
        images = list(map(lambda img: img / 255.0, images))
        return np.array(images)

    # Classify if an image has a piece occupied
    def classify_occupation(self, images):
        # Preprocess the images
        images = self.preprocess_cnn_image(images)

        # Predict the class
        occ_classes = self.occ_model.predict(images).argmax(axis=-1)

        # Label each prediction
        return list(map(lambda num: self.occ_labels[num], occ_classes))

    # Classify the piece class of an image
    def classify_piece_image(self, piece_image):
        # Preprocess the images
        piece_image = self.preprocess_cnn_image([piece_image])

        # Predict the class
        piece_classes = self.piece_model.predict(piece_image).argmax(axis=-1)

        # Label each prediction
        return self.piece_labels[piece_classes[0]]

    # Classify pieces using the occupations and images
    def classify_pieces(self, images, occupations):
        piece_images = []

        # Get all images that are occupied with a piece
        for i in range(len(occupations)):
            if (occupations[i] == '0'):
                piece_images.append(images[i])

        # Classify all the piece images
        piece_images = self.preprocess_cnn_image(piece_images)
        piece_classes = self.piece_model.predict(piece_images).argmax(axis=-1)
        piece_classes = list(map(lambda num: self.piece_labels[num], piece_classes))

        # Turn the occupation board into an occupation piece board
        # by replacing all 0 with the piece symbol
        pieces = occupations
        num_occ = 0
        for i in range(len(pieces)):
            if (occupations[i] == '0'):
                pieces[i] = piece_classes[num_occ]
                num_occ += 1
        return pieces

    def get_occ_model(self):
        return self.occ_model

    def get_piece_model(self):
        return self.piece_model
