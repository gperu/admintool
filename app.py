import os
import json
from flask import Flask, render_template, request, abort, Response, redirect,\
                  flash


import db
import cities
from roster import Person, Facts, Event, Site
from forms import EventForm
from utils import safe_float, safe_int

app = Flask(__name__)

@app.route('/cities.json')
def cities_json():
    MIN_QUERY_LENGTH = 2
    NUM_RESULTS = 5

    query = request.args.get('q', '')
    if len(query) < MIN_QUERY_LENGTH:
        abort(400)
    return Response(json.dumps([
        {'name': city.full_name,
         'lat': city.latitude,
         'long': city.longitude}
        for city in cities.find(query)[:NUM_RESULTS]
    ]), mimetype='application/json')

@app.route('/sites.json')
def sites_json():
    query = request.args.get('q', '')
    if not query:
        abort(400)
    sites = db.get_session().query(Site).filter(Site.named_like(query))
    results = json.dumps([
        {'name': s.fullname} for s in sites
    ])
    return Response(results, mimetype='application/json')

@app.route('/')
def home():
    latitude = safe_float(request.args.get('city_lat'))
    longitude = safe_float(request.args.get('city_long'))
    radius = safe_int(request.args.get('radius'))
    closest = safe_int(request.args.get('closest'))
    python = bool(request.args.get('python'))
    r = bool(request.args.get('r'))

    people = db.get_session().query(Person).join(Person.facts).\
             join(Facts.airport).\
             filter(Facts.active == True)

    if python:
        people = people.filter(Facts.python == True)
    if r:
        people = people.filter(Facts.r == True)

    if latitude is not None and longitude is not None and radius:
        people = (
            person for person in people
            if person.facts.airport.is_within_radius_of(
                radius,
                latitude,
                longitude,
                units='km'
            )
        )
    elif latitude is not None and longitude is not None and closest:
        # not searching radius but rather closest people
        people = sorted(people,
            key=lambda x: x.facts.airport.distance_from(latitude, longitude))[:closest]

    return render_template('index.html', people=people)

### Bulk Uploader
@app.route('/bulkUpload')
def bulkUpload():
    return render_template('bulkUpload.html')

@app.route('/file-upload', methods=['POST'])
def fileUpload():
    files = request.files.getlist('file')
    firstLineSkipped = False
    data = {'data': [], 'headers': None}
    for file in files:
        for line in file:
            if len(line.split('\r')) > 1:
                lines = line.split('\r')
                for l in lines:
                    if firstLineSkipped:
                        data['data'].append(l.split(','))
                    else:
                        data['headers'] = l.split(',')
                        firstLineSkipped = True
            else:
                if firstLineSkipped:
                    data['data'].append(line.split(','))
                else:
                    data['headers'] = line.split(',')
                    firstLineSkipped = True
    return json.dumps(data)

@app.route('/addUsers', methods=['POST'])
def addUsers():
    users = request.json['users']
    success = db.add_users(users)
    return json.dumps(success)
###


### Event Manager
@app.route('/events')
def events():
    events = db.get_session().query(Event).all()
    site = request.args.get('site', '').replace('+', ' ') # XXX URI quote
    if site:
        events = [e for e in events if e.site.fullname == site]
    return render_template('events/index.html', events=events)

@app.route('/events/new')
def new_event():
    event = Event()
    form = EventForm(obj=event)
    form.new_record = True
    return render_template('events/new.html', form=form)

@app.route('/events', methods=['POST'])
def create_event():
    db_session = db.get_session()

    event = Event()
    form = EventForm()
    form.new_record = True

    form.populate_obj(event)

    if form.validate_on_submit():
        db_session.add(event)
        db_session.commit()
        flash('The event has been created successfully.','alert-success')
        return redirect('events')
    else:
        return render_template('events/new.html', form=form)

@app.route('/events/<id>/edit')
def edit_event(id):
    event = db.get_session().query(Event).get(id)
    form = EventForm(obj=event)
    return render_template('events/edit.html', event=event, form=form)

@app.route('/events/<id>', methods=['POST'])
def update_event(id):
    db_session = db.get_session()

    form = EventForm()
    event = db_session.query(Event).get(id)

    form.id.data = event.id
    form.populate_obj(event)

    if form.validate_on_submit():
        db_session.add(event)
        db_session.commit()
        return redirect('events')
    else:
        return render_template('events/edit.html', event=event, form=form)

###

def create_dbs():
    cities.create_db()
    if not os.path.exists(db.ROSTER_DB_PATH):
        db.create_roster_db()

if __name__ == '__main__':
    create_dbs()

    from config import config
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    app.run()
