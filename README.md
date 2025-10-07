# Realtime Chess Digitizer

> This project, developed as part of my 3rd Year Individual Project at the University of Southampton, implements a real-time computer vision system
> that detects and classifies chess pieces from live camera input 
> using Convolutional Neural Network (CNN) models. It converts physical chessboard states into digital formats (like FEN notation)
> in real time, enabling accurate move tracking and game analysis. This allows for integration with chess engines or analysis tools.
> Furthermore, attempts at creating a chess bot achieving a ranking of around 1800 elo using advanced heuristic based search algorithms.
---

## Demo

Click the video below to watch a demo

[![Watch the video](https://img.youtube.com/vi/leD5OC5vZQ4/0.jpg)](https://youtu.be/leD5OC5vZQ4)
<!-- You can also embed YouTube demos using: [![Watch the video](https://img.youtube.com/vi/leD5OC5vZQ4/0.jpg)](https://youtu.be/leD5OC5vZQ4) -->

---

## Features
- Detects and classifies chess pieces in real-time from video input
- Deep learning–based models (VGG16, Xception) for piece recognition  
- Includes a custom dataset (given in the "Test Images/Chess Pieces Recognition" folder) of over 20 games and 200,000 images
- Converts camera frames into FEN board notation  
- Optional GUI or command-line visualization
 
---

## How To Run And Project Structure

Requires python 3.9  
Jupyter notebook code (seen in .ipynb) includes code for training models, testing board, move and image recognition as well as code for the chess AI.  
To run, install necessary requirements and run GUIMain.py for a GUI application or ConsoleMain.py for a console based application.

Realtime-Chess-Digitizer/  
**├── Assets/** # Holds visual assets for GUI  
**├── Models/** # Pretrained .keras models  
**├── Test Images/**  
**│ ├── Chess Board Recognition** # Images of chessboards for testing recogntion  
**│ ├── Chess Games/** # Holds raw images of chess games with a moves.txt file  
**│ ├── Chess Pieces Recognition/** Images used to train CNN models for both piece class and occupancy
**├── ChessAI.py** # Code that the chess AI uses to calculate best moves
**├── ChessBoardCorners.py** # Used to calculate the position of the corners of a board from the webcam  
**├── ChessConstants.py** # Constants used by ChessAI.py  
**├── ChessImageClassifier.py** # Used to classify piece occupation and class  
**├── ConsoleMain.py** # Run for a console application  
**├── Engine.py** # Background engine for running application
**├── GUIMain.py** # Run for a GUI application  
**├── ImageToChessboard.py** # Code for converting the image of a chessboard to FEN notation  
**├── LegalMoveDetector.py** # Used to calculate legal moves from images  
**└── README.md**

---

## CNN Results

Two CNN models are used for classified if a square is occupied, and if so, the class the piece is.  
Models in bold (VGG16 and Xception) are the ones used in the final program

The occupancy classifier was trained using a fully connected network (FCN) with the following configuration:  
**Dense(500) → Dense(250) → Dropout(0.3)**, trained for **10 epochs**.  
The table below summarizes the performance of each base CNN model.

| **Model**   | **Train Accuracy** | **Validation Accuracy** | **Test Accuracy** | **Training Time** | **Prediction Speed (ms/step)** |
|:------------|:------------------:|:------------------------:|:-----------------:|:-----------------:|:-------------------------------:|
| **VGG16**   | 99.94% | 100.00% | 100.00% | 33.0 min | 3 ms |
| VGG19       | 99.86% | 100.00% | 99.98% | 33.8 min | 4 ms |
| InceptionV3 | 99.98% | 99.98% | 99.97% | 30.6 min | 12 ms |
| Xception    | 99.98% | 100.00% | 99.91% | 35.8 min | 5 ms |
| MobileNetV2 | 99.98% | 100.00% | 99.98% | 34.3 min | 5 ms |
| ResNet50    | 98.05% | 99.07% | 99.75% | 33.4 min | 9 ms |


The piece classifier used the same FCN structure (**Dense(500) → Dense(250) → Dropout(0.3)**) but was trained for **20 epochs**.  
Performance metrics for each base architecture are presented below.

| **Model**    | **Train Accuracy** | **Validation Accuracy** | **Test Accuracy** | **Training Time** | **Prediction Speed (ms/step)** |
|:-------------|:------------------:|:------------------------:|:-----------------:|:-----------------:|:-------------------------------:|
| VGG16        | 97.62% | 91.98% | 89.26% | 26.3 min | 3 ms |
| VGG19        | 95.36% | 85.60% | 85.36% | 26.8 min | 4 ms |
| InceptionV3  | 98.18% | 93.70% | 90.76% | 26.0 min | 12 ms |
| **Xception** | 99.09% | 91.46% | 92.25% | 26.3 min | 5 ms |
| MobileNetV2  | 99.01% | 94.24% | 88.50% | 26.9 min | 5 ms |
| ResNet50     | 66.50% | 62.17% | 66.50% | 25.7 min | 9 ms |