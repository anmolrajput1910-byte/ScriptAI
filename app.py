from flask import Flask, render_template, request, redirect, session, send_file
import random
from datetime import date

app = Flask(__name__)
app.secret_key = "secretkey"


# -------- Load & Filter Scripts --------

def load_scripts(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    raw_scripts = content.split("===SCRIPT===")
    scripts = []

    for s in raw_scripts:
        s = s.strip()
        if s:
            lines = s.split("\n")
            topic_line = lines[0]

            if topic_line.startswith("TOPIC:"):
                topic = topic_line.replace("TOPIC:", "").strip()
                text = "\n".join(lines[1:]).strip()
                scripts.append({"topic": topic, "text": text})

    return scripts


free_scripts = load_scripts("scripts_free.txt")
pro_scripts = load_scripts("scripts_pro.txt")


# -------- Home --------

@app.route("/")
def home():

    if "is_pro" not in session:
        session["is_pro"] = False

    if "count" not in session:
        session["count"] = 0
        session["date"] = str(date.today())

    if session["date"] != str(date.today()):
        session["count"] = 0
        session["date"] = str(date.today())

    return render_template("index.html",
                           script=None,
                           is_pro=session["is_pro"])


# -------- Generate --------

@app.route("/generate", methods=["POST"])
def generate():

    selected_topic = request.form["topic"]

    if not session["is_pro"]:
        if session["count"] >= 2:
            return render_template("index.html",
                                   script="⚠ Free limit finished (2/day). Upgrade to Pro.",
                                   is_pro=False)

        session["count"] += 1
        dataset = free_scripts
    else:
        dataset = pro_scripts

    # filter by topic
    filtered = [s for s in dataset if s["topic"].lower() == selected_topic.lower()]

    if not filtered:
        script_text = "No script available for this topic."
    else:
        script_text = random.choice(filtered)["text"]

    return render_template("index.html",
                           script=script_text,
                           is_pro=session["is_pro"])


# -------- Upgrade --------

@app.route("/upgrade")
def upgrade():
    session["is_pro"] = True
    return redirect("/")


# -------- Export PDF --------

@app.route("/export_pdf", methods=["POST"])
def export_pdf():

    text = request.form["script"]
    file_path = "script.pdf"

    doc = SimpleDocTemplate(file_path)
    story = []
    style = ParagraphStyle(name="Normal")

    for line in text.split("\n"):
        story.append(Paragraph(line, style))

    doc.build(story)

    return send_file(file_path, as_attachment=True)


# -------- Run --------

if __name__ == "__main__":
    app.run()

import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
