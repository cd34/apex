#import deform
#import colander
#import formencode

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.url import route_url
from pyramid.url import current_route_url
from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid

from pyrapex.models import DBSession
from pyrapex.lib.auth import AuthUser
from pyrapex.lib.auth import AuthGroup
#from pyrapex.lib.libs import merge_session_with_post

def email_validate(address):
    try:
        valid = formencode.validators.Email().to_python(address)
        return True
    except Exception as message:
        return unicode(message)

def user_validate(username):
    dbsession = DBSession()
    user = dbsession.query(AuthUser).filter(AuthUser.username==username).first()
    if user:
        return u'Username exists, please choose another'
    return True

def userpass_validate(form, value):
    dbsession = DBSession()
    auth = dbsession.query(AuthUser).filter(AuthUser.username==value['username']).first()
    if auth:
        if not auth.validate_password(value['password']):
            exc = colander.Invalid(form, 'Username not found or password didn\'t match')
            raise exc

def user_or_email_validate(form, value):
     if not value['username'] and not value['email']:
          exc = colander.Invalid(
              form, 'A value for either Email or Username is required')
          exc['username'] = 'Required if email is not supplied'
          exc['email'] = 'Required if username is not supplied'
          raise exc

"""
class LoginSchema(colander.Schema):
    came_from = colander.SchemaNode(colander.String(),
        widget = deform.widget.HiddenWidget(),
    )
    username = colander.SchemaNode(
        colander.String(),
        widget = deform.widget.TextInputWidget(size=40),
    )
    password = colander.SchemaNode(colander.String(),
               validator=colander.Length(min=5, max=100),
               widget=deform.widget.PasswordWidget(size=40),
    )

class PasswordSchema(colander.Schema):
    came_from = colander.SchemaNode(colander.String(),
        widget = deform.widget.HiddenWidget(),
    )
    oldpassword = colander.SchemaNode(colander.String(),
               validator=colander.Length(min=5, max=100),
               widget=deform.widget.PasswordWidget(size=40),
               title = 'Old Password',
    )
    newpassword = colander.SchemaNode(colander.String(),
               validator=colander.Length(min=5, max=100),
               widget=deform.widget.CheckedPasswordWidget(size=40),
               title = 'New Password',
    )

class ForgotSchema(colander.Schema):
    came_from = colander.SchemaNode(colander.String(),
        widget = deform.widget.HiddenWidget(),
    )
    username = colander.SchemaNode(
        colander.String(),
        missing=u'',
        widget = deform.widget.TextInputWidget(size=40),
    )
    email = colander.SchemaNode(
        colander.String(),
        missing=u'',
        widget = deform.widget.TextInputWidget(size=60),
        validator = colander.Function(email_validate),
    )

class RegisterSchema(colander.Schema):
    came_from = colander.SchemaNode(colander.String(),
        widget = deform.widget.HiddenWidget(),
    )
    username = colander.SchemaNode(
        colander.String(),
        widget = deform.widget.TextInputWidget(size=40),
        validator = colander.Function(user_validate),
    )
    password = colander.SchemaNode(colander.String(),
               validator=colander.Length(min=5, max=100),
               widget=deform.widget.CheckedPasswordWidget(size=40),
               description='Enter a password',
    )
    email = colander.SchemaNode(colander.String(),
        widget = deform.widget.TextInputWidget(size=60),
        validator = colander.Function(email_validate),
    )
    plan = colander.SchemaNode(colander.String(),
        widget = deform.widget.RadioChoiceWidget(values=(
            ('0-5','FREE for 60 days, 5 Active Codes'), 
            ('10-60','$10.00 for 30 days, 60 Active Codes'),
            ('30-200','$30.00 for 30 days, 200 Active Codes'),
        )) 
    )
"""

def login(request):
    title = 'Log in'
    dbsession = DBSession()
    schema = LoginSchema(validator=userpass_validate)
    form = deform.Form(schema, buttons=('Log in',))
    login_url = route_url('login', request)
    referrer = request.referrer
    if referrer == login_url or not referrer:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    if request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except deform.ValidationFailure, e:
            return {'form':e.render(), 'title':title}
        auth_id = dbsession.query(AuthUser.id).filter(AuthUser.username==request.POST['username']).first()[0]
        headers = remember(request, auth_id)
        return HTTPFound(location = came_from,
                         headers = headers)
    appstruct = {'came_from':came_from}
    return {'form':form.render(appstruct=appstruct), 'title':title}

def logout(request):
    headers = forget(request)
    return HTTPFound(location = route_url('home', request),
                     headers = headers)

def forbidden_view(request):
    return HTTPFound(location = '%s?came_from=%s' % 
                                (route_url('login', request),
                                 current_route_url(request)) )

def password(request):
    title = 'Change Password'
    dbsession = DBSession()
    schema = PasswordSchema()
    form = deform.Form(schema, buttons=('Change Password',))
    login_url = route_url('password', request)
    referrer = request.referrer
    if referrer == login_url or not referrer:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    if request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except deform.ValidationFailure, e:
            return {'form':e.render(), 'title':title}
        auth = dbsession.query(AuthUser).filter(AuthUser.id==authenticated_userid(request)).first()
        auth.password = appstruct['newpassword']
        dbsession.merge(auth)
        return HTTPFound(location = came_from)

    appstruct = {'came_from':came_from}
    return {'form':form.render(appstruct=appstruct), 'title':title}

def forgot(request):
    title = 'Forgot my Password'
    dbsession = DBSession()
    schema = ForgotSchema(validator=user_or_email_validate)
    form = deform.Form(schema, buttons=('Reset my Password',))

    login_url = route_url('login', request)
    referrer = request.referrer
    if referrer == login_url or not referrer:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)

    if request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except deform.ValidationFailure, e:
            return {'form':e.render(), 'title':title}

    appstruct = {'came_from':came_from}
    return {'form':form.render(appstruct=appstruct), 'title':title}

def register(request):
    title = 'Create an Account'
    dbsession = DBSession()
    schema = RegisterSchema()
    form = deform.Form(schema, buttons=('Add Account',))

    login_url = route_url('login', request)
    referrer = request.referrer
    if referrer == login_url or not referrer:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    plan = request.params.get('plan', '0-5')

    appstruct = {'came_from':came_from, 'plan':plan}

    if request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except deform.ValidationFailure, e:
            return {'form':e.render(), 'title':title}
        record = AuthUser(username=appstruct['username'], 
                          password=appstruct['password'],
                          email=appstruct['email'],
                          parent_id = request.cookies.get('refer',0),
                          plan = appstruct['plan'])
        dbsession.add(record)
        group = dbsession.query(AuthGroup).filter(AuthGroup.name=='user').one()
        group.users.append(record)
        dbsession.flush()
        make_qr_code(record.id, 
            '/var/www/pyramid/go2re/go2re/static/codes/refer/')
        headers = remember(request, record.id)
        return HTTPFound(location = came_from,
                         headers = headers)
  
    return {'form':form.render(appstruct=appstruct), 'title':title}

def groupfinder(userid, request):
    dbsession = DBSession()
    auth = dbsession.query(AuthUser).filter(AuthUser.id==userid).first()
    if auth:
        return [('group:%s' % group.name) for group in auth.groups]

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'authenticated'),
                (Allow, 'group:user', 'user'),
                (Allow, 'group:admin', 'admin') ]
    def __init__(self, request):
        if request.matchdict:
            self.__dict__.update(request.matchdict)
