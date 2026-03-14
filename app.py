from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from googletrans import Translator
import requests

app = Flask(__name__)

# OpenAI API
translator=Translator()
client = OpenAI(api_key="sk_7hT5ePBFTlavOgMnBp9CWGdyb3FYQf4il0vnWMOTsirFHBwcMTvd")

translator = Translator()

# Weather helper
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=0940b693c15896bdd258befc71790b68&units=metric"
    res = requests.get(url).json()

    if "main" in res:
        temp = res["main"]["temp"]
        desc = res["weather"][0]["description"]
        return f"Weather in {city}: {temp}°C, {desc}"

    return "City not found."


# AI answer helper
def ai_answer(question, lang="en"):

    if lang != "en":
        question_en = translator.translate(question, src=lang, dest="en").text
    else:
        question_en = question

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question_en}]
        )

        answer_en = response.choices[0].message.content

    except Exception as e:
        return f"Error contacting OpenAI: {e}"

    if lang != "en":
        answer = translator.translate(answer_en, src="en", dest=lang).text
    else:
        answer = answer_en

    return answer


# Routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    data = request.json
    question = data.get("question", "")

    if not question:
        return jsonify({"answer": "Please enter a question."})

    detected_lang = translator.detect(question).lang

    answer = ai_answer(question, lang=detected_lang)

    return jsonify({"answer": answer, "lang": detected_lang})


@app.route("/weather", methods=["POST"])
def weather():

    city = request.json.get("city", "")

    info = get_weather(city)

    return jsonify({"weather": info})


if __name__ == "__main__":
    app.run(debug=True)