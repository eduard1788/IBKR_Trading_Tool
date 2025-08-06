To refactor your code into a modular and object-oriented structure, I will:

Create a TradingApp class to encapsulate the main application logic and GUI.
Create a IBKRClient class to handle all IBKR (Interactive Brokers) API interactions.
Move utility functions into appropriate classes or modules.
Organize the code into the new trading_manager folder, splitting responsibilities for maintainability.
I will start by creating the following files in trading_manager:

ibkr_client.py: Handles IBKR API connection and data retrieval.
gui.py: Contains the main GUI logic and widget management.
utils.py: General utility functions.
__init__.py: For package initialization.
Let me create the initial structure and class skeletons.

Created ibkr_client.py

Created gui.py

Created utils.py

Created __init__.py

The initial modular and object-oriented structure is now set up in the trading_manager folder with the following files:

ibkr_client.py: Handles IBKR API connection and data retrieval.
gui.py: Contains the main GUI logic and widget management.
utils.py: General utility functions.
__init__.py: Package initializer.
Next, I can help you migrate and refactor specific logic from your current utilities.py and main.py into these new modules, organizing them for efficiency and maintainability. Let me know if you want to proceed with a specific part (e.g., connection logic, widget creation, or data processing) or the full migration.