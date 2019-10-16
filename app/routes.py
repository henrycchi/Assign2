import subprocess
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, SpellForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SpellForm()
    if form.validate_on_submit():
        temptext = form.inputtext.data
        with open('userinput.txt', 'w') as file:
            file.write(temptext)
            file.close()
        textoutput = subprocess.run(['./a.out', 'userinput.txt', 'wordlist.txt'], stdout=subprocess.PIPE, check=True, universal_newlines=True)
        textmisspell = textoutput.stdout.replace("\n", ", ")[:-2]
        if textmisspell == "":
            textmisspell = "No words were misspelled."
            return render_template('spellcheck.html', textoutput=temptext, textmisspell=textmisspell, form=form)
        else:
            textmisspell = temptext
            return render_template('spellcheck.html', textoutput=textoutput.stdout, textmisspell=textmisspell, form=form)
    return render_template('spellcheck.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
       return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect username, or password')
            return redirect(url_for('login'))
        if not user.check_twofa(form.twofa.data):
            flash('Two -factor failure')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        flash('success')
        next_page = url_for('index')
        return redirect(next_page)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.set_twofa(form.twofa.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
