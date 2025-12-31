# Python Binance Trading Bot

This is a Python-based trading bot that uses the Binance API to execute trading strategies.

## Features

- **Backtesting:** Test your trading strategies on historical data.
- **Live Trading (WIP):** Execute trades in real-time.
- **Extensible:** Easily add new trading strategies.

## Getting Started

### Prerequisites

- Python 3.8+
- Binance API Key and Secret

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    -   Create a `.env` file in the root directory of the project.
    -   Add your Binance API key and secret to the `.env` file:
        ```
        BINANCE_API_KEY=your_api_key
        BINANCE_API_SECRET=your_api_secret
        ```

### Usage

#### Backtesting

To run a backtest of your trading strategy, use the following command:

```bash
python main.py --mode backtest --start-date "1 month ago UTC"
```

You can customize the start date for the backtest by changing the `--start-date` argument.

#### Live Trading

Live trading is not yet implemented.

## Project Structure

```
├── config/         # Configuration files
├── data/           # Data files (e.g., historical data)
├── src/            # Source code
│   ├── api/        # API clients (e.g., Binance)
│   ├── trading/    # Trading strategies and backtesting
│   └── utils/      # Utility functions (e.g., logger)
├── tests/          # Test files
├── main.py         # Main entry point of the application
├── requirements.txt # Project dependencies
└── README.md       # This file
```

## Disclaimer

This project is for educational purposes only. Do not use it for live trading without understanding the risks involved.