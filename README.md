# מה ללבוש היום? 🌤️

שרת backend שמקבל שם של עיר, מביא את מזג האוויר מ-[Open-Meteo](https://open-meteo.com) (REST API שמחזיר JSON)
וממליץ מה ללבוש. כתוב פעמיים: ב-Node.js וב-Python.

## הרצה

**Node.js**
```
npm install
node server.js
```
פותחים בדפדפן: http://localhost:3000/outfit/Tel%20Aviv

**Python**
```
pip install flask requests
python3 server.py
```
פותחים בדפדפן: http://localhost:5001/outfit/Tel%20Aviv

## כתובות
| כתובת | מה היא עושה |
|---|---|
| `/outfit/<עיר>` | מזג אוויר + המלצה מה ללבוש |
| `/trip?cities=London,Eilat,Paris` | איזו עיר הכי נעימה לטיול (קרובה ל-24 מעלות) |
