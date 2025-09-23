## Nifty 500 EMA Crossover Scanner with Telegram Alerts

This document provides instructions on how to set up and run the Nifty 500 stock scanner.

The scanner identifies stocks from the Nifty 500 index that have just experienced a bullish or bearish EMA crossover event and sends alerts to a Telegram chat.

### Features

-   **Stock Universe:** Nifty 500 stocks (from `nifty500.txt`).
-   **Bullish Alert:** Triggers once when the 9-day EMA crosses *above* the 21-day EMA, and the stock's open price is also above the 9-day EMA.
-   **Bearish Alert:** Triggers once when the 9-day EMA crosses *below* the 21-day EMA, and the stock's open price is also below the 9-day EMA.
-   **Alerts:** Sends real-time alerts to a configured Telegram chat.
-   **Scheduling:** Automatically runs every 10 minutes during Indian market hours (9:15 AM - 3:30 PM IST, Monday-Friday).

### Prerequisites

-   Python 3.x
-   `pip` for installing packages
-   A Telegram account

### Setup

1.  **Install Dependencies:**
    Open a terminal and run the following command to install the necessary Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up Telegram Bot:**
    To receive alerts, you need to provide your Telegram Bot credentials.
    a. Create a new file named `config.ini` in the root directory of this project.
    b. Copy the contents of `config.ini.example` into your new `config.ini` file.
    c. Replace the placeholder values (`YOUR_BOT_TOKEN_HERE` and `YOUR_CHAT_ID_HERE`) with your actual Telegram Bot Token and Chat ID.

    *Note: The `config.ini` file is included in `.gitignore` and will not be committed to version control, keeping your credentials safe.*

### Running the Scanner

1.  **Execute the script:**
    Once the setup is complete, you can run the scanner with the following command:
    ```bash
    python nifty_scanner.py
    ```

2.  **Operation:**
    -   The script will initialize and perform an initial scan.
    -   It will then enter a loop, checking the time every minute.
    -   During market hours (9:15 AM to 3:30 PM IST, Monday to Friday), it will run the scan every 10 minutes.
    -   If any new crossover events are detected, it will send an alert to your configured Telegram chat.
    -   To stop the scanner, press `Ctrl+C` in the terminal.
