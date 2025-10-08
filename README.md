# Realtime Chess Digitizer

> This project, developed as part of my 3rd Year Individual Project at the University of Southampton, implements a real-time computer vision system
> that detects and classifies chess pieces from live camera input 
> using Convolutional Neural Network (CNN) models. It converts physical chessboard states into digital formats (like FEN notation)
> in real time, enabling accurate move tracking and game analysis. This allows for integration with chess engines or analysis tools.
> Furthermore, attempts at creating a chess bot achieving a ranking of around 1800 elo using advanced heuristic based search algorithms.
>
> The Dataset can be downloaded (for free) at: https://www.kaggle.com/datasets/oliverbutlersu/chess-pieces-and-board-recognition/data or from the "Test Images" folder

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
**├── BoardGUI.py** # Holds (bad) code for drawing GUI  
**├── Camera.py** # Holds code for controlling camera operations  
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

Models were trained from a custom dataset from 20 games recorded from different camera angles and lightings, split into an 80:10:10 split. All data can be freely found in the "Test Images/Chess Pieces Recognition" folder where images are split into piece class and occupation.

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

---

## How It Works

### 1. Chessboard Localisation

To accurately interpret the state of a chessboard from an image or video feed, the system must first **detect and isolate the board**.  
This is achieved through a multi-step **computer vision pipeline** combining thresholding, edge detection, line detection, and geometric transformation.

---

### 1.1 Line Detection

1. **Adaptive Thresholding**  
   - Traditional Canny edge detection alone struggles under variable lighting, producing “salt-and-pepper” noise or missing detail.  
   - By applying an **adaptive threshold**, local brightness variations are normalized before edge detection.  
   - This process evaluates each pixel relative to its local neighborhood, segmenting the image more robustly under both bright and dim conditions.

2. **Canny Edge Detection**  
   - After thresholding, a **Canny edge detector** is applied to highlight contours and edges corresponding to board lines and piece outlines.  
   - The combination of adaptive threshold + Canny produces a refined, high-contrast edge map of the chessboard.

3. **Hough Transform & Line Clustering**  
   - The **Hough Line Transform** identifies all potential straight lines in the edge image.  
   - Because this often detects overlapping or redundant lines, a **line unification algorithm** is applied:  
     - Lines are grouped by proximity in ρ (distance) and θ (angle).  
     - Lines within a certain threshold are merged, producing one representative line per group.  
     - This method is adapted from *E. Fathi (2018)* for improved geometric consistency.  
   - Finally, lines are filtered by orientation, removing any that deviate significantly from the main board axes.

> *Result:* A clean set of horizontal and vertical grid lines representing the chessboard edges.

---

### 1.2 Line Intersections & Perspective Transform

1. **Finding Intersections**  
   - Each line is represented in polar coordinates:  
     **ρ = x·cos(θ) + y·sin(θ)**  
   - Using linear algebra (NumPy solver), the intersection points between horizontal and vertical lines are calculated, yielding a grid of potential square corners.  
   - Points falling outside the image bounds are discarded.

2. **Corner Detection**  
   - The outermost intersection points define the four corners of the chessboard.  
   - These serve as key reference points for transforming the image.

3. **Perspective Correction**  
   - Using **OpenCV’s perspective transform**, the image is warped and cropped so the board is perfectly centered and viewed from a top-down angle.  
   - This ensures consistent scaling and alignment for downstream tasks like piece detection and classification.

> *Result:* A normalized, front-facing view of the chessboard that can be divided into 8×8 squares for further analysis.

---

## 2. Piece and Move Detection

### 2.1 Piece and Occupancy Detection

A custom-built dataset (linked above) was made to train multiple CNN models to detect whether a square is occupied and, if so, the piece class.
More details can be found on the Kaggle page.

### 2.1 Board State Comparison
Each state is manually captured by the user pressing a button after completing a move. This approach ensures accuracy and aligns with real-world tournament play, where players use a clock or move timer.

When a new image is captured:
- Each of the 64 squares is classified by **occupancy only** (whether a piece is present), as this yields higher reliability than full piece classification.
- The system compares the **previous** and **current** occupation grids to detect changes.

Moves are then encoded using the **UCI (Universal Chess Interface)** format — for example:  
> `d7d8q` → a move from *d7* to *d8*, promoting to a queen.

From this comparison, the system identifies which squares changed:
- Squares that became empty → part of the **previous occupation list**.  
- Squares that became occupied → part of the **new occupation list**.  

Using these, the system checks which of the following **four legal move types** occurred.

---

### 2.3 Move Types

| Move Type | Description | Example |
|:-----------|:-------------|:---------|
| **Standard Move** | One square becomes empty, and one new square becomes occupied. | `e2e4` — pawn moves from e2 to e4. |
| **Attacking Move** | A piece moves onto a previously occupied square. The system checks the colour change of the target square to verify capture. | `c3d5` — knight captures a piece on d5. |
| **En Passant** | Two pieces move relative to the last board state — the pawn performing the capture and the pawn being taken. | `e5d6` — pawn performs en passant capture. |
| **Castling** | Two specific pieces (king and rook) move simultaneously. Only valid for the four standard castle moves. | `e1g1`, `e1c1`, `e8g8`, `e8c8` |
| **Promotion** | A pawn reaches the final rank and is replaced with a new piece. The piece classifier confirms the new type. | `d7d8q` — pawn promotes to a queen. |

---

### 2.4 Validation
All detected moves are cross-checked with a **chess engine’s set of legal moves**.  
If a move doesn’t correspond to a valid one from the engine, it is rejected, ensuring consistency with chess rules.

---
