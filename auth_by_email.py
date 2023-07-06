from py4web.core import Fixture, Flash
from py4web import HTTP, action, request, abort, redirect, URL
from py4web.utils.form import Form
from pydal import Field
from pydal.validators import IS_EMAIL
import calendar
import time

import smtplib
from smtplib import SMTP
from email.message import EmailMessage
import os
import ssl

# Key to access the user's email in the session
EMAIL_KEY = "_user_email"

LOGIN_PATH = "auth_by_email/login"
LOGOUT_PATH = "auth_by_email/logout"
WAITING_PATH = "auth_by_email/waiting"
CONFIRMATION_PATH = "auth_by_email/confirm"

# 12 Hours expiration
# If changed, change session type in Common.py as well
EXPIRATION_TIME = 3600 * 12

class TestEmailer(object):
    # Dummy class for sending emails. Prints link instead
    def send_email(self, useremail, link):
        host = os.environ.get("SMTPEndpoint")
        user = os.environ.get("SMTPUser")
        password = os.environ.get("SMTPPassword")
        context = ssl.create_default_context()

        msg = EmailMessage()
        msg.set_content("Use this link to sign in: http://pokerating.com" + link)
        msg.add_alternative("""\
        <html>
            <body>
                <p>Hello!</p>
                <p>Use this
                    <a href="{myLink}">
                        LINK
                    </a> to sign into Pokerating.com.
                </p>
                <p>If you did not request this email, or are receiving it in error, take no action</p>
            </body>
        </html>
            """.format(myLink = "http://pokerating.com" + link), subtype="html")
        msg['Subject'] = "Login link for Pokerating.com"
        msg['From'] = "NO-REPLY@Pokerating.com"
        msg["To"] = useremail
        print("Finished Crafting message")

        with SMTP(host,2587) as server :
            # securing using tls
            server.starttls(context=context)

            # authenticating with the server to prove our identity
            server.login(user=user, password=password)

            # sending a plain text email
            print("About to send message")
            server.send_message(msg)
            server.quit()
            print("Message Sent")

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
    
    # When the fixture is requested, it will check that the users session has not expired
    # If expired, it will throw a warning, and log the user out.
    def on_request(self, context):
        activity = self.session.get("recent_activity")
        time_now = calendar.timegm(time.gmtime())
        if (self.current_user):
            if (time_now - activity > EXPIRATION_TIME):
                del self.session[EMAIL_KEY]
                self.flash.set("Login expired")
                redirect(URL(self.default_path))

    # Manages the login page
    def login(self):
        # If user is already logged in, we don't need to be here
        if self.session.get(EMAIL_KEY):
            redirect(URL(self.default_path))

        if not self.session.get("recentEmails"):
            self.session["recentEmails"] = 0

        if not self.session.get("recent_activity"):
            self.session["recent_activity"] = calendar.timegm(time.gmtime())

        form = Form([Field('email', requires=IS_EMAIL())], csrf_session = self.session)
        if form.accepted:
            # Send an email to the user asking to confirm the email by clicking on a link
            # The link will cause the user to be logged in
            activity = self.session.get("recent_activity")
            time_now = calendar.timegm(time.gmtime())
            if (time_now - activity > 300):
                self.session["recentEmails"] = 0
                self.session["recent_activity"] = calendar.timegm(time.gmtime())

            if (self.session.get("recentEmails") < 5):
                link = URL(CONFIRMATION_PATH, form.vars['email'], signer=self.url_signer)
                self.emailer.send_email(form.vars['email'], link)
                self.session["recentEmails"] += 1
                redirect(URL(WAITING_PATH))
            else:
                self.flash.set("Too many emails sent recently!")
                redirect(URL(WAITING_PATH))
        return dict(form = form)

    # Wait around!
    def wait(self):
        # Controller for waiting page
        return dict()
    
    # Controller for the confimation of sign in.
    def confirm(self, email=None):
        # Can only be accessed by a valid signed link.
        # With a valid link, will load the home page with a flash that the user signed in

        assert email is not None
        self.session[EMAIL_KEY] = email
        self.session.expiration = EXPIRATION_TIME
        self.flash.set("Successful Login")
        self.session["recent_activity"] = calendar.timegm(time.gmtime())
        redirect(URL(self.default_path))

    # Controller for the log out
    def logout(self):
        # Will load the home page with a flash that the user logged out
        del self.session[EMAIL_KEY]
        self.flash.set("Logged out")
        redirect(URL(self.default_path))

    def on_success(self, context):
        context['template_inject'] = {"user": self.current_user}


# Enforced version, if we want non-logged in requests to fail.
class AuthByEmailEnforcer(Fixture):
     
    # Created by wrapping a regular AuthByEmail as a variable of AuthByEmail enforcer
    def __init__(self, auth):
        self.auth = auth
        self.session = auth.session
        self.__prerequisites__ = [auth.session]

    def on_request(self, context):
        activity = self.session.get("recent_activity")
        time_now = calendar.timegm(time.gmtime())
        if (self.auth.current_user):
            if (time_now - activity > EXPIRATION_TIME):
                del self.session[EMAIL_KEY]
        if self.session.get(EMAIL_KEY):
            # The user is logged in
            return
        else:
            # Fail
            raise HTTP(403)

    def on_success(self, context):
        self.auth.on_success(context)