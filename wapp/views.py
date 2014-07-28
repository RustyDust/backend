
from flask import render_template, jsonify, flash, redirect, url_for, request, Response

from app import app
from auth import auth
from models import User, Location, Testing
from flask_wtf import Form
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Optional


choices = [
    ('1', 'Alice'),
    ('2', 'Bob'),
    ('3', 'Carol'),
]

class Jform(Form):
    name = TextField('Name', description='Your name')
    number = TextField('Number', description='Number as text', validators=[Required()])
    spec = SelectField('Pic name', choices=choices)
    ulist = SelectField('User name', validators=[Optional()])

    submit_button = SubmitField('Submit Form')

@app.route('/', methods = ['GET', 'POST'])
def start():
    # Determine whether user is logged in and redirect if not
    me = auth.get_logged_in_user()
    if me:
        if me.username == 'admin' or me.admin:
            return show_userlist()
        else:
            return show_user_devices(me.username)
    else:
        return render_template('welcome.html')

@app.route('/userlist')
@app.route('/userlist/')
@auth.login_required
def show_userlist():
    if auth.get_logged_in_user().admin:
        user_list = Location.select(Location.username, Location.device, Location.topic).distinct().order_by(Location.username.asc())
        return render_template('userlist.html', users = user_list, cur_user = auth.get_logged_in_user())
    else:
        # Only admins can get the full userlist
        # so go away. shoo, shoo.
        return redirect('/devicelist/%s' % auth.get_logged_in_user().username, 302)

@app.route('/devicelist')
@app.route('/devicelist/')
@auth.login_required
def check_and_redirect():
    if auth.get_logged_in_user():
        return redirect('/devicelist/%s' % auth.get_logged_in_user().username, 302)
    else:
        return redirect('/')

@app.route('/devicelist/<username>')
@auth.login_required
def show_user_devices(username):
    device_list = Location.select(Location.device, Location.topic).distinct().where(Location.username == username).order_by(Location.device.asc())
    return render_template('devicelist.html', devices = device_list, cur_user = auth.get_logged_in_user())

@app.route('/oldroot', methods = ['GET', 'POST'])
def mainpage():
    
    form = Jform()
    print request.args
    print form.is_submitted()
    form.spec.data = '2' # pre-select choice

    # user_q = User.select()
    user_q = User.select(User.id, User.username).distinct().where(User.username != 'admin')
    user_q = user_q.order_by(User.username.asc())


    # form.ulist.choices = [ (u.id, u.username) for u in user_q]
    form.ulist.choices = [ (str(u.id), u.username) for u in user_q]
    print form.ulist.choices

    if form.validate_on_submit():
        tt = Testing(name=form.name.data,
                     number=form.number.data,
                     spec=form.spec.data,
                     ulist=form.ulist.data,
                     author='xxxx') #author=users.get_current_user())
        tt.save()
        flash('Thanks, babe!')
        return redirect(url_for('mainpage'))

    return render_template('welcome.html', form=form)

@app.route('/register')
def register_new_user():
    if request.method == 'POST' and request.form['username']:
        try:
            user = User.select().where(User.username==request.form['username']).get()
            flash('That username is already taken')
        except User.DoesNotExist:
            user = User(
                username=request.form['username'],
                email=request.form['email'],
                join_date=datetime.datetime.now()
            )
            user.set_password(request.form['password'])
            user.save()

            auth.login_user(user)
            return redirect(url_for('start'))

    return render_template('register.html')
    
@app.route('/list')
def hello_world(cur_user):
    username = 'stefan'
    device = 'Note3'
    from_date = '2013-10-08'
    to_date = '2015-12-31'

    query = Location.select().where(
                (Location.username == username) &
                (Location.device == device) &
                (Location.tst.between(from_date, to_date))
            )
    query = query.order_by(Location.tst.asc())

    print query

    return render_template('base.html', location=query)

@app.route('/map')
def show_map():
    return render_template('map.html')

# An isodate filter for Jinja2. Gets a datetime object
# passed to it, and returns an ISO format (Zulu)
@app.template_filter('isodate')
def _jinja2_filter_datetime(dt):
    return dt.isoformat()[:19]+'Z'

@app.route('/gpx/<username>/<device>/<from_date>/<to_date>')
def gpx_generate(username, device, from_date, to_date):
    
    query = Location.select().where(
                (Location.username == username) &
                (Location.device == device) &
                (Location.tst.between(from_date, to_date))
            )
    query = query.order_by(Location.tst.asc())

    result = render_template('gpx.html', data=query)

    return Response(result, mimetype='text/xml')
