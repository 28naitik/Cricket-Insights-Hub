# 🏏 Cricket Insights Hub

**Cricket Insights Hub** is a comprehensive, data-driven Django web application that provides interactive tools to analyze cricket player statistics, compare players, and predict match outcomes using rule-based logic. It offers a visually appealing HTML/CSS front-end interface without JavaScript and integrates external cricket APIs for live news and updates.

---

## 🚀 Features

- 🔍 **Player Stats Viewer**  
  Format-wise stats (ODI, T20I, Test) for individual players with short bios and photos.

- 🆚 **Player Comparison Tool**  
  Side-by-side comparison of two players based on selected formats.

- 🧠 **Match Prediction System**  
  Predict match winners using rule-based logic based on team/player performance.

- 📰 **Live Cricket News Feed**  
  Integration with NewsAPI.org to fetch and display the latest cricket news.

- 💬 **Post & Comment System**  
  Users can create posts, like, and comment — enabling community engagement.

- 🎨 **Modern UI/UX**  
  Designed using pure HTML and CSS for responsive and clean interface.

---

## 🛠️ Tech Stack

| Layer      | Technology               |
|------------|--------------------------|
| Backend    | Django (Python)          |
| Frontend   | HTML5, CSS3              |
| Data Source| CSV files, NewsAPI.org   |
| Database   | SQLite (default Django)  |

---

## 📂 Project Structure

cricket_insights_hub/
├── analyzer/ # Main Django app
│ ├── views.py
│ ├── models.py
│ ├── urls.py
│ ├── templates/
│ │ ├── home.html
│ │ ├── player_stats.html
│ │ ├── player_compare.html
│ │ └── match_predictor.html
│ └── static/
│ ├── css/
│ └── images/
├── db.sqlite3
├── manage.py
└── README.md
---

## 📦 Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/28naitik/cricket-insights-hub.git
cd cricket-insights-hub
Create and activate a virtual environment

bash
Copy
Edit
python -m venv venv
venv\Scripts\activate  # On Windows
Install dependencies


📈 Future Enhancements
🧪 Add machine learning model for smarter predictions.

🧾 Admin dashboard to manage players/posts.

🌐 Add internationalization support.

📊 Graphical analytics using Matplotlib or Plotly.

🙋‍♂️ About the Developer
Made by Naitik Saxena
GitHub: @28naitik
Leetcode: Naitik12

