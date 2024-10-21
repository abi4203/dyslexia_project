from flask import Flask, render_template

from game.game2 import module1_blueprint
from speech2text.app import module2_blueprint
from summariser.sum import module3_blueprint
from text2img.t2img import module4_blueprint
from text2speech.t2s import module5_blueprint

app = Flask(__name__, static_folder='static')


# Register blueprints from each module
app.register_blueprint(module1_blueprint, url_prefix='/module1')
app.register_blueprint(module2_blueprint, url_prefix='/module2')
app.register_blueprint(module3_blueprint, url_prefix='/module3')
app.register_blueprint(module4_blueprint, url_prefix='/module4')
app.register_blueprint(module5_blueprint, url_prefix='/module5')

@app.route('/')
def home():
    return render_template('landing.html')  

if __name__ == '__main__':
    app.run(debug=True)
