from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return f"Fuck you, and have a nice day <br> <iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3989.818320343149!2d-0.0021886860044996763!3d3.5083546467077066e-15!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0xbc6dbea4e5fc3562!2zMMKwMDAnMDAuMCJOIDDCsDAwJzAwLjAiRQ!5e0!3m2!1spl!2spl!4v1655217717031!5m2!1spl!2spl\" width=\"600\" height=\"450\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>"

if __name__ == '__main__':
    app.run(debug=True)
