from py4web.core import Fixture, Flash
from py4web import HTTP, action, request, abort, redirect, URL
from py4web.utils.form import Form
from pydal import Field
from pydal.validators import IS_EMAIL
import calendar
import time
from datetime import date

import smtplib
from smtplib import SMTP
from email.message import EmailMessage
import os
import ssl


class emailer(Fixture):
    def __init__(self, session, spam_db):
        self.session = session
        self.db = spam_db

    def active(self):
        if not self.session.get("recentEmails"):
            self.session["recentEmails"] = 0

        if not self.session.get("recent_activity"):
            self.session["recent_activity"] = calendar.timegm(time.gmtime())

        activity = self.session.get("recent_activity")
        time_now = calendar.timegm(time.gmtime())
        self.session["recent_activity"] = calendar.timegm(time.gmtime())
        if (time_now - activity > 300):
            self.session["recentEmails"] = 0

    def canEmail(self, target, myip):
        rows = self.db((self.db.daily.day) == date.today().strftime("%m/%d/%Y")).select()
        if (len(rows) != 0):
            row = rows[0]
            if (row.codessent >= 10000):
                return False

        rows = self.db((self.db.ips.ip) == myip).select()
        if (len(rows) != 0):
            row = rows[0]
            if (calendar.timegm(time.gmtime()) - row.lastcodesent > 900):
                self.db.ips.update_or_insert(
                    ((self.db.ips.ip == myip)),
                    ip = myip,
                    codeswithoutresponse = 0
                )
                row = self.db((self.db.ips.ip) == myip).select()[0]
            if (row.codeswithoutresponse >= 15):
                return False

        rows = self.db((self.db.emails.email) == target).select()
        if (len(rows) != 0):
            row = rows[0]
            if (calendar.timegm(time.gmtime()) - row.lastcodesent > 600):
                self.db.emails.update_or_insert(
                    ((self.db.emails.email == target)),
                    email = target,
                    codeswithoutresponse = 0
                )
                row = self.db((self.db.emails.email) == target).select()[0]
            if (row.codeswithoutresponse >= 5):
                return False

        if (self.session.get("recentEmails") >= 5):
            return False
        return True
    
    def codeSent(self, target):
        today = date.today().strftime("%m/%d/%Y")

        self.db.emails.update_or_insert(
            ((self.db.emails.email == target)),
            email = target,
            lastcodesent = calendar.timegm(time.gmtime())
        )
        mySql = "UPDATE emails SET codessent = codessent + 1, codeswithoutresponse = codeswithoutresponse + 1 WHERE email='" + target + "'"
        result = self.db.executesql(mySql)

        self.db.daily.update_or_insert(
            ((self.db.daily.day == today)),
            day = today,
        )
        mySql = "UPDATE daily SET codessent = codessent + 1 WHERE day='" + today + "'"
        result = self.db.executesql(mySql)

        self.session["recentEmails"] += 1
        self.db.commit()

    def codeSentIP(self, myip):
        self.db.ips.update_or_insert(
            ((self.db.ips.ip == myip)),
            ip = myip,
            lastcodesent = calendar.timegm(time.gmtime())
        )
        mySql = "UPDATE ips SET codessent = codessent + 1, codeswithoutresponse = codeswithoutresponse + 1 WHERE ip='" + myip + "'"
        result = self.db.executesql(mySql)
        self.db.commit()

    def codeUsed(self, target):
        self.db.emails.update_or_insert(
            ((self.db.emails.email == target)),
            email = target,
            lastcodeused = calendar.timegm(time.gmtime()),
            codeswithoutresponse = 0
        )
        mySql = "UPDATE emails SET codesused = codesused + 1 WHERE email='" + target + "'"
        result = self.db.executesql(mySql)

        self.session["recentEmails"] = 0
        self.db.commit()

    def codeUsedIP(self, myip):
        self.db.ips.update_or_insert(
            ((self.db.ips.ip == myip)),
            email = myip,
            lastcodeused = calendar.timegm(time.gmtime()),
            codeswithoutresponse = 0
        )
        mySql = "UPDATE ips SET codesused = codesused + 1 WHERE ip='" + myip + "'"
        result = self.db.executesql(mySql)
        self.db.commit()

    def sendLoginEmail(self, target, link, sourceip):
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
        msg["To"] = target
        #print("Finished Crafting message")

        with SMTP(host,2587) as server :
            # securing using tls
            server.starttls(context=context)

            # authenticating with the server to prove our identity
            server.login(user=user, password=password)

            # sending a plain text email
            #print("About to send message")
            server.send_message(msg)
            server.quit()
            self.codeSent(target)
            self.codeSentIP(sourceip)
            #print("Message Sent")

        #print("Use this link " + link)

    def sendDeleteEmail(self, target, link, sourceip):
        host = os.environ.get("SMTPEndpoint")
        user = os.environ.get("SMTPUser")
        password = os.environ.get("SMTPPassword")
        context = ssl.create_default_context()

        msg = EmailMessage()
        msg.set_content("Use this link to delete all info: http://pokerating.com" + link)
        msg.add_alternative("""\
        <html>
            <body>
                <p>Hello!</p>
                <p>Use this
                    <a href="{myLink}">
                        LINK
                    </a> to delete all information associated with this email on Pokerating.com.
                </p>
                <p>If you did not request this email, or are receiving it in error, take no action</p>
            </body>
        </html>
            """.format(myLink = "http://pokerating.com" + link), subtype="html")
        msg['Subject'] = "Delete link for Pokerating.com"
        msg['From'] = "NO-REPLY@Pokerating.com"
        msg["To"] = target
        #print("Finished Crafting message")

        with SMTP(host,2587) as server :
            # securing using tls
            server.starttls(context=context)

            # authenticating with the server to prove our identity
            server.login(user=user, password=password)

            # sending a plain text email
            #print("About to send message")
            server.send_message(msg)
            server.quit()
            self.codeSent(target)
            self.codeSentIP(sourceip)
            #print("Message Sent")
