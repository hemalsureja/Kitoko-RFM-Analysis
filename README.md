# Kitoko E-Commerce Data Analytics & RFM Segmentation

## Overview
This project is an automated data pipeline and dashboard generator designed for e-commerce performance analytics. It processes raw Amazon Order Details and Advertising Campaign Data to generate a highly professional, recruiter-ready "Bento Box" style interactive dashboard. 

The pipeline specifically focuses on:
- **RFM (Recency, Frequency, Monetary) Customer/Product Segmentation**
- **Advertising Efficiency (ACOS vs ROAS) Tracking**
- **Revenue & Marketing Conversion Funnels**
- **ARIMA-based Time Series Revenue Forecasting**

## Key Features
1. **Automated ETL Pipeline (`data_pipeline.py`)**: 
   - Cleans and parses raw Amazon reports.
   - Calculates RFM scores to rank ASINs into 5 distinct segments (Top Performer, High Value, Recent Favorite, Mid Performer, At Risk).
2. **Predictive Analytics**:
   - Uses `statsmodels` ARIMA (AutoRegressive Integrated Moving Average) modeling to project sales 14 days into the future based on historical trends.
3. **Interactive Plotly Dashboard (`generate_visuals.py`)**:
   - Outputs a standalone, fully responsive `kitoko_dashboard.html` file.
   - Modern Glassmorphism & Bento Box grid layout.
   - Key visual metrics including dual-axis charts, funnels, horizontal bar charts, and pie charts.

## Technologies Used
- **Language**: Python 3.x
- **Data Manipulation**: Pandas, OpenPyXL
- **Data Visualization**: Plotly (Express & Graph Objects)
- **Time Series Forecasting**: Statsmodels (ARIMA)
- **Frontend**: Vanilla HTML/CSS (Embedded inside the Python generator)

## Project Structure
- `run_everything.py`: The main orchestrator script. Runs the installation, pipeline, and visual generator sequentially.
- `data_pipeline.py`: Handles data cleaning and the RFM segmentation logic.
- `generate_visuals.py`: Loads the cleaned data, fits the forecasting models, and generates the Plotly/HTML dashboard.
- `requirements.txt`: Python package dependencies.
- `kitoko_dashboard.html`: The final generated interactive dashboard.

## How to Run
1. Ensure Python 3.x is installed on your machine.
2. Clone this repository.
3. Place your raw data files (`Kitoko_Campaign_Data.xlsx` and `Kitoko order details.xlsx`) in the same directory.
4. Run the orchestrator script:
   ```bash
   python run_everything.py
   ```
5. Once the script completes successfully, open the newly generated `kitoko_dashboard.html` in any modern web browser to view the interactive dashboard.
