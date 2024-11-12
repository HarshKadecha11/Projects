from flask import Flask, render_template, request
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    current_time = None
    timezones = pytz.all_timezones
    if request.method == 'POST':
        city = request.form['city']
        timezone = request.form['timezone']
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        except pytz.UnknownTimeZoneError:
            current_time = 'Unknown timezone'
    return render_template('index.html', current_time=current_time, timezones=timezones)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)