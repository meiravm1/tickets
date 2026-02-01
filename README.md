# International Concert Facts Streamlit App

## Project Description
This Streamlit application provides interesting facts and insights about international concert tickets, leveraging data from the Ticketmaster Discovery API. The app allows users to explore various aspects of music events, including upcoming concerts, price comparisons, event timing distributions, and genre popularity across different cities.

## Features
- **Upcoming Concerts**: View concerts happening within a specified window (e.g., next 24 hours) in various capital cities.
- **Price Comparison**: Compare minimum ticket prices for selected bands across multiple cities.
- **Hour Distribution**: Analyze the distribution of concert start times throughout the day.
- **Genre Distribution**: Visualize the popularity of different music genres within various cities using `sns.catplot`.

## Data Source
Data is sourced from the Ticketmaster Discovery API (Music events category). The application utilizes a small sample of events across selected cities.

## How to Run Locally
To run this Streamlit application on your local machine, follow these steps:

1.  **Clone the Repository (if not already done)**:
    ```bash
    git clone <repository_url>
    cd tickets # Or the name of your project directory
    ```

2.  **Set up a Python Virtual Environment with Poetry**:
    This project uses [Poetry](https://python-poetry.org/) for dependency management. If you don't have Poetry installed, you can install it by following the instructions on its official website.

    Navigate to the project's root directory and install dependencies:
    ```bash
    poetry install
    ```

3.  **Activate the Virtual Environment**:
    ```bash
    poetry shell
    ```

4.  **Run the Streamlit App**:
    ```bash
    streamlit run streamlit_app.py
    ```
    This will open the application in your default web browser.

## Project Structure
- [`streamlit_app.py`](streamlit_app.py): The main Streamlit application script.
- [`src/data_analyser.py`](src/data_analyser.py): Contains logic for data analysis and processing of event data.
- [`src/displayer.py`](src/displayer.py): Handles the display logic for various data visualizations.
- [`src/ticket_request.py`](src/ticket_request.py): Manages API requests to Ticketmaster and data loading.
- [`src/constants.py`](src/constants.py): Stores constant values used throughout the application, such as capital cities.

## Technologies Used
- Python
- [Streamlit](https://streamlit.io/)
- [Seaborn](https://seaborn.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Pandas](https://pandas.pydata.org/)
- [Poetry](https://python-poetry.org/) (for dependency management)
