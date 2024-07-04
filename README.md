# Supermarket Product Optimizer

This project is a Human-Machine Interface (HMI) application that optimizes supermarket product selection based on user input.

## Features

- Web scraping of supermarket product data
- Product optimization based on user-defined budget
- User-friendly interface for search and result display

## Setup

1. Ensure you have Python 3.8+ installed.
2. Clone this repository:
   ```
   git clone [your-repo-url]
   cd [your-repo-name]
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main application:

```
python src/main.py
```

1. Enter a product search term and budget in the interface.
2. Click "Search" to initiate the scraping and optimization process.
3. View the optimized product selection in the results area.

## Project Structure

- `src/`: Source code
  - `scraper/`: Web scraping module
  - `optimizer/`: Product optimization module
  - `ui/`: User interface components
- `data/`: Stores scraped product data
- `requirements.txt`: Project dependencies
- `README.md`: This file
