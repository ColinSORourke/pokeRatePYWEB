from py4web.core import Fixture, Flash
from py4web import HTTP, action, request, abort, redirect, URL
from py4web.utils.form import Form
from pydal import Field
from pydal.validators import IS_EMAIL
import calendar
import time

# Key to access the email in the session
EMAIL_KEY = "_user_email"

LOGIN_PATH = "auth_by_email/login"
LOGOUT_PATH = "auth_by_email/logout"
WAITING_PATH = "auth_by_email/waiting"
CONFIRMATION_PATH = "auth_by_email/confirm"

EXPIRATION_TIME = 900

class TestEmailer(object):
    # Dummy class for sending emails. Prints link instead
    def send_email(self, email, link):
        print("Use this link " + link)

class AuthByEmail(Fixture):

    def __init__(self, session, url_signer, emailer=None, default_path='home'):
        self.session = session
        self.emailer = emailer or TestEmailer()
        self.url_signer = url_signer
        self.default_path = default_path
        self.__prerequisites__ = [session]
        self.flash = Flash()
        
        # Register path to login
        f = action.uses("auth_by_email_login.html", self.flash, session, url_signer)(self.login)
        action(LOGIN_PATH, method=["GET", "POST"])(f)
        # Register path to waiting
        f = action.uses("auth_by_email_wait.html", self.flash, session)(self.wait)
        action(WAITING_PATH, method=["GET"])(f)
        # Register path to confimation
        f = action.uses("auth_by_email_wait.html", self.flash, session, url_signer.verify())(self.confirm)
        action(CONFIRMATION_PATH + "/<email>", method=["GET"])(f)

        f = action.uses("auth_by_email_login.html", self.flash, session)(self.logout)
        action(LOGOUT_PATH, method=["GET"])(f)

    @property
    def current_user(self):
        # If not logged in, returns None
        # If logged in, returned a dictionary containing only the email
        if self.session.get(EMAIL_KEY):
            return dict(email=self.session.get(EMAIL_KEY))
        else:
            return None
        
    def enforce(self):
        # Returns a fixture that enforces log-in via email
        return AuthByEmailEnforcer(self)
    
    @property
    def login_url(self):
         return URL(LOGIN_PATH)
    
    def on_request(self, context):
        activity = self.session.get("recent_activity")
        time_now = calendar.timegm(time.gmtime())
        if (self.current_user):
            if (time_now - activity > EXPIRATION_TIME):
                print("Session expired")
                del self.session[EMAIL_KEY]
                self.flash.set("Login expired")
                redirect(URL(self.default_path))

    def login(self):

        if self.session.get(EMAIL_KEY):
            redirect(URL(self.default_path))

        form = Form([Field('email', requires=IS_EMAIL())], csrf_session = self.session)
        if form.accepted:
            # Send an email to the user asking to confirm the email by clicking on a link
            # The link will cause the user to be logged in
            link = URL(CONFIRMATION_PATH, form.vars['email'], signer=self.url_signer)
            self.emailer.send_email(form.vars['email'], link)
            redirect(URL(WAITING_PATH))
        return dict(form = form)

    def wait(self):
        # Controller for waiting page
        return dict()
    
    def confirm(self, email=None):
        # Controller for the confirmation page
        # If the link is valid, tells the user they are logged in, creates session

        assert email is not None
        self.session[EMAIL_KEY] = email
        self.session.expiration = EXPIRATION_TIME
        self.flash.set("Successful Login")
        self.session["recent_activity"] = calendar.timegm(time.gmtime())
        redirect(URL(self.default_path))

    def logout(self):
        del self.session[EMAIL_KEY]
        self.flash.set("Logged out")
        redirect(URL(self.default_path))

    def on_success(self, context):
        context['template_inject'] = {"user": self.current_user}



class AuthByEmailEnforcer(Fixture):
     
    def __init__(self, auth):
        self.auth = auth
        self.session = auth.session
        self.__prerequisites__ = [auth.session]

    def on_request(self, context):
        activity = self.session.get("recent_activity")
        time_now = calendar.timegm(time.gmtime())
        if (self.auth.current_user):
            if (time_now - activity > EXPIRATION_TIME):
                print("Session expired")
                del self.session[EMAIL_KEY]
        if self.session.get(EMAIL_KEY):
            # The user is logged in
            return
        else:
            # Fail
            raise HTTP(403)

    def on_success(self, context):
        self.auth.on_success(context)