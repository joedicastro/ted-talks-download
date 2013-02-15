#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
    TEDTalks.py: Automate download new HD TED Talks by its RSS Feed
"""

#==============================================================================
# This Script uses the TED Talks HD RSS Feed to download the talks' videos and
# subtitles.
#==============================================================================

#==============================================================================
#       Copyright 2010 joe di castro <joe@joedicastro.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================

__author__ = "joe di castro - joe@joedicastro.com"
__license__ = "GNU General Public License version 3"
__date__ = "21/11/2012"
__version__ = "2.0"

try:
    import feedparser
    import getpass
    import glob
    import json
    import os
    import pickle
    import platform
    import re
    import socket
    import smtplib
    import sys
    import time
    import urllib
    import urllib2
    from argparse import ArgumentParser
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.utils import COMMASPACE, formatdate
    from subprocess import Popen, PIPE
    from textwrap import fill
except ImportError:
    # Checks the installation of the necessary python modules
    print((os.linesep * 2).join(["An error found importing one module:",
          str(sys.exc_info()[1]), "You need to install it", "Stopping..."]))
    sys.exit(-2)


class Logger():
    """

    Create a log object to log script messages.

    These messages can be sended via email or writed in a log file

    """

    def __init__(self):
        """Create the object Logger itself and set two variables.

        This variable is about this python file:

        __script_name = The script name
        filename = the log file's name

        """
        self.__log = ''
        self.__script_name = os.path.basename(__file__).split('.')[0]
        self.filename = '{0}.log'.format(self.__script_name)

    def __len__(self):
        return len(self.__log)

    def __format__(self, tit, cont, decor):
        """Format a block or a list of lines to enhance comprehension.

        (str) tit -- title for the block or list
        (str or iterable) cont -- line/s for the list/block content
        ('=' or '_') decor - define if it's list or block and decorate it

        make the looks of self.block() and self.list()

        """
        ending = {'=': '', '_': os.linesep}[decor]
        end = {'=': '=' * 80, '_': ''}[decor]
        begin = ' '.join([tit.upper(), (80 - (len(tit) + 1)) * decor]) + ending
        cont = [cont] if isinstance(cont, str) else cont
        sep = os.linesep
        self.__log += sep.join([begin, sep.join(cont), end, sep])

    def block(self, title, content):
        """A block of text lines headed and followed by a line full of '='.

        (str) title -- The title that start the first line of '='
        (str or iterable) content -- The line/s between the '=' lines

        There's not any empty line between the '=' lines and content, e.g.:

        TITLE ==================================================
        content
        ========================================================

        """
        if content:
            self.__format__(title, content, '=')

    def list(self, title, content):
        """A list of text lines headed by a line full of '_'.

        (str) title -- The title that start the line of '_'
        (str or iterable) content -- The line/s after the '_' line

        After the '_' line is a empty line between it and the content, e.g.:

        TITLE __________________________________________________

        content

        """
        if content:
            self.__format__(title, content, '_')

    def free(self, content):
        """Free text unformatted.

        (str) content -- Text free formated

        """
        if isinstance(content, str):
            self.__log += content + os.linesep * 2

    def time(self, title):
        """A self.block() formated line with current time and date.

        (str) title -- Title for self.block()

        Looks like this, the data and time are right-justified:

        TITLE ==================================================
                                       Friday 09/10/10, 20:01:39
        ========================================================

        """
        self.block(title, '{0:>80}'.format(time.strftime('%A %x, %X')))

    def header(self, url, msg):
        """A self.block() formated header for the log info.

        (str) url -- The url of the script
        (str) msg -- Message to show into the header to provide any useful info

        It looks like this:

        SCRIPT =================================================
        script name and version
        url

        msg
        ========================================================

        """
        script = '{0} (ver. {1})'.format(self.__script_name, __version__)
        self.block('Script', [script, url, '', msg])

    def get(self):
        """Get the log content."""
        return self.__log

    def send(self, subject, send_from='', dest_to='', mail_server='localhost',
             server_user='', server_pass=''):
        """Send a email with the log.

        Arguments:
            (str) send_from -- a sender's email address (default '')
            (str or list) dest_to -- a list of receivers' email addresses ('')
            (str) subject -- the mail's subject
            (str) mail_server -- the smtp server (default 'localhost')
            (str) server_user -- the smtp server user (default '')
            (str) server_pass --the smtp server password (default '')

        If 'send_from' or 'dest_to' are empty or None, then script user's
        mailbox is assumed instead. Useful for loggin scripts

        """
        local_email = '@'.join([getpass.getuser(), socket.gethostname()])
        if not send_from:
            send_from = local_email
        if not dest_to:
            dest_to = [local_email]

        dest_to_addrs = COMMASPACE.join(dest_to)  # receivers mails
        message = MIMEMultipart()
        message['Subject'] = '{0} - {1}'.format(subject,
                                                time.strftime('%A %x, %X'))
        message['From'] = send_from
        message['To'] = dest_to_addrs
        message['Date'] = formatdate(localtime=True)
        message.preamble = "You'll not see this in a MIME-aware mail reader.\n"
        message.attach(MIMEText(self.__log))

        # initialize the mail server
        server = smtplib.SMTP()
        # Connect to mail server
        try:
            server.connect(mail_server)
        except socket.gaierror:
            self.list('mail error', 'Wrong server, are you sure is correct?')
        except socket.error:
            self.list('mail error', 'Server unavailable or connection refused')
        # Login in mail server
        if mail_server != 'localhost':
            try:
                server.login(server_user, server_pass)
            except smtplib.SMTPAuthenticationError:
                self.list('mail error', 'Authentication error')
            except smtplib.SMTPException:
                self.list('mail error', 'No suitable authentication method')
        # Send mail
        try:
            server.sendmail(send_from, dest_to_addrs, message.as_string())
        except smtplib.SMTPRecipientsRefused:
            self.list('mail error', 'All recipients were refused.'
                      'Nobody got the mail.')
        except smtplib.SMTPSenderRefused:
            self.list('mail error', 'The server didn’t accept the from_addr')
        except smtplib.SMTPDataError:
            self.list('mail error', 'An unexpected error code, Data refused')
        # Disconnect from server
        server.quit()

    def write(self, append=False):
        """Write the log to a file.

        The name of the file will be like this:

        script.log

        where 'script' is the name of the script file without extension (.py)

        (boolean) append -- If true appends log to file, else writes a new one

        """
        mode = 'ab' if append else 'wb'
        with open(self.filename, mode) as log_file:
            log_file.write(self.__log)


def arguments():
    """Defines the command line arguments for the script."""
    desc = """Automate download new HD TED Talks by its RSS Feed"""

    parser = ArgumentParser(description=desc)
    parser.add_argument("path", default=os.getcwd(), nargs='?',
                        help="The path to store the TED Talks videos")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s {0}".format(__version__),
                        help="show program's version number and exit")
    return parser


def check_exec_posix(prog):
    """Check if the program is installed in a *NIX platform.

    Returns one value:

    (boolean) found - True if the program is installed

    """
    found = True
    try:
        Popen([prog, '--help'], stdout=PIPE, stderr=PIPE)
    except OSError:
        found = False
    return found


def best_unit_size(bytes_size):
    """Get a size in bytes & convert it to the best IEC prefix for readability.

    Return a dictionary with three pair of keys/values:

    's' -- (float) Size of path converted to the best unit for easy read
    'u' -- (str) The prefix (IEC) for s (from bytes(2^0) to YiB(2^80))
    'b' -- (int / long) The original size in bytes

    """
    for exp in range(0, 90, 10):
        bu_size = abs(bytes_size) / pow(2.0, exp)
        if int(bu_size) < 2 ** 10:
            unit = {0: 'bytes', 10: 'KiB', 20: 'MiB', 30: 'GiB', 40: 'TiB',
                    50: 'PiB', 60: 'EiB', 70: 'ZiB', 80: 'YiB'}[exp]
            break
    return {'s': bu_size, 'u': unit, 'b': bytes_size}


def get_size(the_path):
    """Get size of a directory tree or a file in bytes."""
    path_size = 0
    for path, directories, files in os.walk(the_path):
        for filename in files:
            path_size += os.lstat(os.path.join(path, filename)).st_size
        for directory in directories:
            path_size += os.lstat(os.path.join(path, directory)).st_size
    path_size += os.path.getsize(the_path)
    return path_size


def get_sub(tt_id, tt_intro, sub):
    """Get TED Subtitle in JSON format & convert it to SRT Subtitle."""

    def srt_time(tst):
        """Format Time from TED Subtitles format to SRT time Format."""
        secs, mins, hours = ((tst / 1000) % 60), (tst / 60000), (tst / 3600000)
        right_srt_time = "{0:02d}:{1:02d}:{2:02d},000".format(hours, mins,
                                                              secs)
        return right_srt_time

    srt_content = ''
    sub_log = ''
    tt_url = 'http://www.ted.com/talks'
    sub_url = '{0}/subtitles/id/{1}/lang/{2}'.format(tt_url, tt_id, sub[-7:-4])
    # Get JSON sub
    if FOUND:
        json_file = Popen(['wget', '-q', '-O', '-', sub_url],
                          stdout=PIPE).stdout.readlines()

        if json_file:
            for line in json_file:
                if line.find('captions') == -1 and line.find('status') == -1:
                    json_file.remove(line)
        else:
            sub_log += "Subtitle '{0}' not found.{1}".format(sub, os.linesep)
    else:
        json_file = urllib2.urlopen(sub_url).readlines()
    if json_file:
        try:
            json_object = json.loads(json_file[0])
            if 'captions' in json_object:
                caption_idx = 1
                if not json_object['captions']:
                    sub_log += ("Subtitle '{0}' not available.{1}".
                                format(sub, os.linesep))
                for caption in json_object['captions']:
                    start = tt_intro + caption['startTime']
                    end = start + caption['duration']
                    idx_line = '{0}'.format(caption_idx)
                    time_line = '{0} --> {1}'.format(srt_time(start),
                                srt_time(end))
                    text_line = '{0}'.format(caption['content'].
                                             encode('utf-8'))
                    srt_content += '\n'.join([idx_line, time_line, text_line,
                                             '\n'])
                    caption_idx += 1
            elif 'status' in json_object:
                sub_log += ("This is an error message returned by TED:{0}{0} "
                            "- {1} {0}{0}Probably because the subtitle '{2}' "
                            "is not available.{0}{0}{0}"
                            "".format(os.linesep,
                                      json_object['status']['message'],
                                      sub))

        except ValueError:
            sub_log += ("Subtitle '{0}' it's a malformed json file.{1}".
                        format(sub, os.linesep))
    return srt_content, sub_log


def check_subs(ttalk, v_name):
    """Check if the subtitles for the talk are downloaded, if not try to get
    them. Checks it for english and spanish languages."""
    # Get the names for the subtitles (for english and spanish languages) only
    # if they not are already downloaded
    subs = (s_name for s_name in
            ("{0}.{1}.srt".format(v_name[:-4], lang) for lang in ('eng',
                                                                  'spa'))
            if s_name not in glob.glob('*.srt'))
    s_log = ''
    for sub in subs:
        # Reads the talk web page, to search the talk's intro duration
        if FOUND:
            tt_webpage = Popen(['wget', '-q', '-O', '-',
                                ttalk.feedburner_origlink],
                               stdout=PIPE).stdout.read()
        else:
            tt_webpage = urllib2.urlopen(ttalk.feedburner_origlink).read()
        regex = re.compile('introDuration%22%3A(\d+)%2C')
        tt_intro = (int(regex.findall(tt_webpage)[0]) + 1) * 1000
        subtitle, get_log = get_sub(ttalk.id.split(':')[-1], tt_intro, sub)
        s_log += get_log
        if subtitle:
            with open(sub, 'w') as srt_file:
                srt_file.write(subtitle)
            s_log += "{0}{1} downloaded.{0}".format(os.linesep, sub)
    return s_log


def get_video(ttk, vid_url, vid_name):
    """Gets the TED Talk video."""
    if FOUND:
        Popen(['wget', '-q', '-O', vid_name, vid_url],
              stdout=PIPE).stdout.read()
    else:
        urllib.urlretrieve(vid_url, vid_name)
    v_log = u'{0} ({1})\n'.format(ttk.subtitle, ttk.itunes_duration)
    v_log += u'{0}\n\n'.format('=' * (len(ttk.subtitle) + 11))
    v_log += u'{0}\n\n'.format(ttk.feedburner_origlink)
    v_log += u'{0}\n\n'.format(fill(ttk.content[0].value, 80))
    v_log += u'file://{0}\n'.format(os.path.join(os.getcwd(), vid_name))
    vid_size = best_unit_size(int(ttk.media_content[0]['filesize']))
    v_log += u'{0:.2f} {1}\n\n'.format(vid_size['s'], vid_size['u'])
    return v_log.encode('utf8')


def main():
    """main section"""

    # The directory to store the videos and subs
    args = arguments().parse_args()
    ttalk_vid_dir = args.path

    # initalize the log
    log = Logger()

    # log the header
    url = 'http://joedicastro.com'
    msg = 'Download TED Talks from HD RSS Feed'
    log.header(url, msg)

    # log the start time
    log.time('Start Time')

    os.chdir(os.path.normpath(ttalk_vid_dir))

    # Get a list of the current TED Talks downloaded in the dir
    videos = glob.glob('*.mp4')

    # Get the last download Talk video date
    try:
        with open('.data.pkl', 'rb') as pkl_file:
            last = pickle.load(pkl_file)
    except (EOFError, IOError, pickle.PickleError):
        last = time.localtime(time.time() - 86400)
    video_dates = []

    # The TED Talks HD RSS feed
    ttalk_feed_url = 'http://feeds.feedburner.com/tedtalksHD'
    ttalk_feed = feedparser.parse(ttalk_feed_url)

    # If the feed is erroneous or occurs a http or network error, log and exit!
    if ttalk_feed.bozo:
        log.list('An error occurred', str(ttalk_feed.bozo_exception))
        if not WIN_OS:
            log.send('Download TED Talks')
        sys.exit(1)

    # If correct, process the feed entries
    vids_log, subs_log = '', ''
    for ttalk_entrie in ttalk_feed.entries:
        # Get The video url and name
        tt_vid_url = ttalk_entrie.media_content[0]['url']
        tt_vid_name = tt_vid_url.split('/')[-1].split('?')[0]
        # If the video is new, download it!
        if ttalk_entrie.published_parsed > last and tt_vid_name not in videos:
            vids_log += get_video(ttalk_entrie, tt_vid_url, tt_vid_name)
            videos.append(tt_vid_name)
            video_dates.append(ttalk_entrie.published_parsed)
        # If video is already downloaded, check if subs exists, if not, get it!
        if tt_vid_name in videos:
            subs_log += check_subs(ttalk_entrie, tt_vid_name)
    log.list('Talks downloaded', vids_log)
    log.list('Subs downloaded', [subs_log])

    # Set the last download video date
    if video_dates:
        last = max(video_dates)
        with open('.data.pkl', 'wb') as output:
            pickle.dump(last, output)

    log.time('End time')
    # If logs any activity, sends the information mail
    if not WIN_OS:
        log.send('Download TED Talks')
    log.write(False)


if __name__ == "__main__":
    WIN_OS = True if platform.system() == 'Windows' else False
    if not WIN_OS:
        FOUND = check_exec_posix('wget')
    main()
