Overview
This project is a Tetris game built using Tkinter, Python's standard GUI library, along with the Pillow (PIL) library for image manipulation. The game implements the classic Tetris mechanics with some modern features like dark/light theme switching, score tracking, and a pause menu.

Features
Classic Tetris Gameplay: The player can rotate and move blocks to complete lines and earn points.
Pause Menu: Users can pause, resume, restart, or quit the game.
Dark/Light Theme Toggle: Switch between dark and light themes during gameplay.
High Score Tracking: Keeps track of the player's highest score across sessions.
Debug Mode: Allows setting the score manually for testing purposes.
Responsive UI: The game adapts based on screen size and user input.
Requirements
Python 3.x
Required Python libraries:
tkinter (usually comes pre-installed with Python)
Pillow (PIL) for image handling

How to Play
Movement:

Left/Right arrow keys to move the blocks horizontally.
Up arrow key to rotate the block.
Down arrow key to speed up the block's fall.
Spacebar to drop the block instantly.
Pause the game: Press P to open the pause menu.

Restart: Press R after game over or via the pause menu.

Quit: Press Q after game over or via the pause menu.

Folder Structure
tetris.py: The main game file that contains the game logic and UI elements.
highscore.txt: Stores the high score between game sessions.
TetrisIcon.ico: The game window's icon (optional).
Future Improvements
Additional Features: Add multiplayer support, more themes, or power-ups.
Refactor Code: Modularize the game logic for better maintainability.
Contributions
Feel free to contribute to this project by submitting issues or pull requests on the GitHub repository.

License
This project is open-source and available under the MIT License.
