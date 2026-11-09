// "מה ללבוש היום?" - Node.js backend (Express)
// מקור המידע: https://open-meteo.com  (REST API חינמי שמחזיר JSON, בלי מפתח)

const express = require("express");
const app = express();
const PORT = 3000;

const GEO_URL = "https://geocoding-api.open-meteo.com/v1/search";
const WEATHER_URL = "https://api.open-meteo.com/v1/forecast";

// שלב 1: הופכים שם עיר לקואורדינטות (קו רוחב / קו אורך)
async function getCity(name) {
  const res = await fetch(`${GEO_URL}?name=${encodeURIComponent(name)}&count=1`);
  const data = await res.json(); // המרת JSON לאובייקט
  if (!data.results) throw new Error(`City '${name}' not found`);
  const c = data.results[0];
  return { name: c.name, country: c.country, lat: c.latitude, lon: c.longitude };
}

// שלב 2: מביאים את מזג האוויר העכשווי לפי הקואורדינטות
async function getWeather(name) {
  const city = await getCity(name);
  const url = `${WEATHER_URL}?latitude=${city.lat}&longitude=${city.lon}` +
              `&current=temperature_2m,wind_speed_10m,precipitation`;
  const data = await (await fetch(url)).json();
  return {
    city: city.name,
    country: city.country,
    temperature: data.current.temperature_2m,
    wind: data.current.wind_speed_10m,
    rain: data.current.precipitation,
  };
}

// שלב 3: הלוגיקה שלנו - ממליצים מה ללבוש
function recommendOutfit(w) {
  const items = [];
  if (w.temperature >= 28) items.push("גופייה ומכנס קצר", "כובע", "בקבוק מים");
  else if (w.temperature >= 20) items.push("חולצה קצרה", "ג'ינס");
  else if (w.temperature >= 12) items.push("סווטשירט", "מכנס ארוך");
  else items.push("מעיל חם", "צעיף", "כפפות");
  if (w.rain > 0) items.push("מטרייה");
  if (w.wind > 30) items.push("מעיל רוח");
  return items;
}

// Endpoint 1: מזג אוויר + המלצת לבוש   ->  GET /outfit/Tel Aviv
app.get("/outfit/:city", async (req, res) => {
  try {
    const weather = await getWeather(req.params.city);
    res.json({ ...weather, wear: recommendOutfit(weather) });
  } catch (err) {
    res.status(404).json({ error: err.message });
  }
});

// Endpoint 2: לאיזו עיר כדאי לטוס? (הכי קרובה ל-24 מעלות)
//   ->  GET /trip?cities=London,Eilat,Paris
app.get("/trip", async (req, res) => {
  if (!req.query.cities) return res.status(400).json({ error: "send ?cities=a,b,c" });
  try {
    const names = req.query.cities.split(",");
    // כל הבקשות נשלחות במקביל
    const all = await Promise.all(names.map((n) => getWeather(n.trim())));
    all.sort((a, b) => Math.abs(a.temperature - 24) - Math.abs(b.temperature - 24));
    res.json({ bestCity: all[0].city, ranking: all.map((w) => `${w.city}: ${w.temperature}°C`) });
  } catch (err) {
    res.status(404).json({ error: err.message });
  }
});

app.listen(PORT, () => console.log(`Node server running on http://localhost:${PORT}`));
