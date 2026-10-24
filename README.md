# Py Desktop App

एक modern Python Desktop Application starter project — PySide6, SQLite और custom QSS styling के साथ।

## Features
- Modern dark dashboard और animated UI elements
- Sidebar navigation: Dashboard, Tasks, Notes, Settings
- Tasks जोड़ना, पूरा करना और हटाना
- Notes बनाना और हटाना
- SQLite database: डेटा आपके कंप्यूटर पर स्थानीय रूप से सेव होता है
- Search/filter, live clock, responsive layouts
- Windows पर PyInstaller से EXE बनाने की configuration

## अभी PC पर कुछ डाउनलोड करने की ज़रूरत नहीं
यह repository source code को ऑनलाइन store करती है। Python desktop GUI को GitHub Pages पर सीधे नहीं चलाया जा सकता। ऐप चलाने या Windows EXE बनाने के लिए बाद में Windows PC पर Python और project dependencies install करनी होंगी।

## Requirements
- Python 3.10+
- PySide6

## Windows पर चलाएँ
PowerShell में repository डाउनलोड/क्लोन करने के बाद project folder में:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## EXE बनाएँ
```powershell
python -m pip install pyinstaller
pyinstaller --noconfirm --windowed --name PyDesktopApp main.py
```
EXE `dist/PyDesktopApp/` के अंदर बनेगी (PyInstaller के default mode के अनुसार)।

## Project structure
```
Py-desktop-app/
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── assets/
│   └── README.md
├── ui/
│   └── README.md
├── core/
│   └── README.md
└── tests/
    └── README.md
```

## Data & privacy
Task और note data SQLite database में local application data folder में रखा जाता है। यह ऐप किसी external API को data नहीं भेजता।

## License
MIT
