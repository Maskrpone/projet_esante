from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'data')

db = SQLAlchemy(app)
ma = Marshmallow(app)

# On regarde si le dossier existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDERS'])

# Classe Image (test)
class Image(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(100), unique=True,nullable=False)

    def __init__(self, filename):
        self.filename = filename

class ImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Image

image_schema = ImageSchema()
images_schema = ImageSchema(many=True)


@app.route('/upload', methods=['POST'])
def upload_image():
        if 'image' not in request.files:
            return jsonify({"error": "No image part in the request"}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_image = Image(filename=filename)
            db.session.add(new_image)
            db.session.commit()
            return image_schema.jsonify(new_image)
    
@app.route('/image/<int:id>', methods=['GET'])
def get_image(id):
    image = Image.query.get(id)
    if not image:
        return jsonify({"error": "Image not found"}), 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], image.filename)

# Route pour obtenir toutes les images
@app.route('/images', methods=['GET'])
def get_images():
    all_images = Image.query.all()
    result = images_schema.dump(all_images)
    return jsonify(result)

# Initialise the DB
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
