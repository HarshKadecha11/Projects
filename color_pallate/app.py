import numpy as np
from PIL import Image, ImageOps
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///colors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ColorPalette(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color_code = db.Column(db.String(7), nullable=False)
    color_type = db.Column(db.String(3), nullable=False)

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def give_most_hex(file_path, code):
    my_image = Image.open(file_path).convert('RGB')
    size = my_image.size
    if size[0] >= 400 or size[1] >= 400:
        my_image = ImageOps.scale(image=my_image, factor=0.2)
    elif size[0] >= 600 or size[1] >= 600:
        my_image = ImageOps.scale(image=my_image, factor=0.4)
    elif size[0] >= 800 or size[1] >= 800:
        my_image = ImageOps.scale(image=my_image, factor=0.5)
    elif size[0] >= 1200 or size[1] >= 1200:
        my_image = ImageOps.scale(image=my_image, factor=0.6)
    my_image = ImageOps.posterize(my_image, 2)
    image_array = np.array(my_image)

    unique_colors = {}  # (r, g, b): count
    for column in image_array:
        for rgb in column:
            if tuple(rgb) in unique_colors:
                unique_colors[tuple(rgb)] += 1
            else:
                unique_colors[tuple(rgb)] = 1

    sorted_colors = sorted(unique_colors.items(), key=lambda x: x[1], reverse=True)
    top_colors = sorted_colors[:10]

    if code == 'hex':
        return [rgb_to_hex(color[0]) for color in top_colors]
    else:
        return [color[0] for color in top_colors]

@app.route('/', methods=['GET', 'POST'])
def index():
    colors_list = []
    code = 'rgb'
    image_url = None
    if request.method == 'POST':
        file = request.files['file']
        code = request.form['colour_code']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image_url = file_path
            colors_list = give_most_hex(file_path, code)
            for color in colors_list:
                new_color = ColorPalette(color_code=color, color_type=code)
                db.session.add(new_color)
            db.session.commit()
    return render_template('index.html', colors_list=colors_list, code=code, image_url=image_url)

@app.route('/colors', methods=['GET', 'POST'])
def colors():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    if search_query:
        colors = ColorPalette.query.filter(
            (ColorPalette.color_code.contains(search_query)) |
            (ColorPalette.color_type.contains(search_query))
        ).paginate(page=page, per_page=10)
    else:
        colors = ColorPalette.query.paginate(page=page, per_page=10)
    return render_template('colors.html', colors=colors, search_query=search_query)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_color(id):
    color = ColorPalette.query.get_or_404(id)
    if request.method == 'POST':
        color.color_code = request.form['color_code']
        color.color_type = request.form['color_type']
        db.session.commit()
        return redirect(url_for('colors'))
    return render_template('edit_color.html', color=color)

@app.route('/delete/<int:id>')
def delete_color(id):
    color = ColorPalette.query.get_or_404(id)
    db.session.delete(color)
    db.session.commit()
    return redirect(url_for('colors'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True)