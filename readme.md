# 🐻 Chicago Bears Scouting Dashboard

A data analytics web application that analyzes opponent defensive tendencies 
to help the Chicago Bears coaching staff make better offensive play calling decisions.

## Project Overview
This tool analyzes NFL play-by-play data from **2009-2024 (16 complete seasons)** 
to provide detailed scouting reports on every opponent the Bears face.
Built with feedback from active NFL coaches.

## Features
- Blitz Rate Analysis
- Run Defense Analysis
- Pass Defense Analysis
- 3rd Down Tendencies
- Red Zone TD Rate
- Penalty Adjusted Red Zone Analysis
- Red Zone TD% by Play Type 
- Strategic Recommendations

## Key Findings
- Bears are stronger passing than running
- BAL and KC have toughest defenses vs Bears in red zone
- BUF, SD and DAL are most favorable red zone matchups
- Pass is always better on 3rd down
- Bears waste 89%+ of opponent red zone penalties — key area for improvement
- Own penalties reduce red zone TD% significantly against most teams

## Tech Stack
- Python
- Pandas
- Matplotlib & Seaborn
- Streamlit

## Data Source
NFL Play-by-Play data from:
- NFLSavant.com (2017-2024)
- Kaggle nflscrapR (2009-2016)

## How to Run
```bash
pip install -r requirements.txt
streamlit run bears_app.py
```

## Live App
https://bears-scouting-dashboard.streamlit.app/

## Author
**Kota Srinath**  
Data Analytics | Machine Learning Enthusiast  
Chicago, IL  
[LinkedIn](https://www.linkedin.com/in/kota-srinath) | 
[GitHub](https://github.com/srikota03-DA)