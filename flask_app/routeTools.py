import functools

from flask import session, redirect, request, url_for, render_template as real_render_template
from flask_app.utils.globalUtils import _deleteTempDirectory, _openJSONDirectoriesFile

def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if not session.get('user_info', None) or not session['user_info'].get('username', None):
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def clear_temp(func):
    @functools.wraps(func)
    def clear_temp_folder(*args, **kwargs):
        if session.get('user_info', None):
            if "username" in session['user_info']:
                _deleteTempDirectory()
        return func(*args, **kwargs)
    return clear_temp_folder

def loggedIn():
    username, role = False, False
    if 'user_info' in session:
        username = session['user_info']['username']
        role = session['user_info']['role']

    return True if username and role else False

def render_template(*args, **kwargs):
    username, role = False, False
    if loggedIn():
        username, role = session['user_info']['username'], session['user_info']['role']
    
    return real_render_template(*args, **kwargs, user=username, role=role, 
                                cond_routes=_openJSONDirectoriesFile()['conditionally-included-routes'])

def cond_render_template(*args, **kwargs):
    if kwargs['cond_statement']:
        return render_template(*args, **kwargs)
    else:
        return redirect('/')