#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
    TEDTalks.py: Automate download new HD TED Talks by its RSS Feed
"""

#===============================================================================
# This Script uses the TED Talks HD RSS Feed to download the talks' videos and 
# subtitles.
#
# Este script emplea la fuente RSS de las TED Talks en HD, para descargar los
# videos y los subtitulos para las charlas
#===============================================================================

#===============================================================================
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
#
#
#    Este programa es software libre: usted puede redistribuirlo y/o modificarlo
#    bajo los términos de la Licencia Publica General GNU publicada 
#    por la Fundación para el Software Libre, ya sea la versión 3 
#    de la Licencia, o (a su elección) cualquier versión posterior.
#
#    Este programa se distribuye con la esperanza de que sea útil, pero 
#    SIN GARANTIA ALGUNA; ni siquiera la garantía implícita 
#    MERCANTIL o de APTITUD PARA UN PROPOSITO DETERMINADO. 
#    Consulte los detalles de la Licencia Publica General GNU para obtener 
#    una información mas detallada. 
#
#    Deberla haber recibido una copia de la Licencia Publica General GNU 
#    junto a este programa. 
#    En caso contrario, consulte <http://www.gnu.org/licenses/>.
#
#===============================================================================

__author__ = "joe di castro - joe@joedicastro.com"
__license__ = "GNU General Public License version 3"
__date__ = "25/11/2010"
__version__ = "1.0"

try:
    import os
    import sys
    import json
    import urllib
    import urllib2
    import glob
    import feedparser
    import smtplib
    import time
    import socket
    import pickle
    import platform
    from re import search, findall
    from subprocess import Popen, PIPE
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.utils import COMMASPACE, formatdate
except ImportError:
    # Checks the installation of the necessary python modules 
    # Comprueba si todos los módulos necesarios están instalados
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
        ending = {'=':'', '_':os.linesep}[decor]
        end = {'=': '=' * 80, '_':''}[decor]
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
        (str) msg -- Message to show into the header. To Provide any useful info

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
        local_email = '@'.join([os.getenv('LOGNAME'), socket.gethostname()])
        if not send_from:
            send_from = local_email
        if not dest_to:
            dest_to = [local_email]

        dest_to_addrs = COMMASPACE.join(dest_to) # receivers mails
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


def check_exec_posix_win(prog):
    """Check if the program is installed.

    Returns three values:
    
    (boolean) found - True if the program is installed 
    (dict) windows_paths - a dictionary of executables/paths (keys/values)
    (boolean) is_windows - True it's a Windows OS, False it's a *nix OS

    """
    found = True
    windows_paths = {}
    is_windows = True if platform.system() == 'Windows' else False
    # get all the drive unit letters if the OS is Windows
    windows_drives = findall(r'(\w:)\\',
                             Popen('fsutil fsinfo drives', stdout=PIPE).
                             communicate()[0]) if is_windows else None
    if is_windows:
        # Set all commands to search the executable in all drives
        win_cmds = ['dir /B /S {0}\*{1}.exe'.format(letter, prog) for letter in
                    windows_drives]
        # Get the first location (usually in C:) of the all founded where
        # the executable exists
        exe_paths = (''.join([Popen(cmd, stdout=PIPE, stderr=PIPE,
                                    shell=True).communicate()[0] for
                                    cmd in win_cmds])).split(os.linesep)[0]
        # Assign the path to the executable or report not found if empty
        if exe_paths:
            windows_paths[prog] = exe_paths
        else:
            found = False
    else:
        try:
            Popen([prog, '--help'], stdout=PIPE, stderr=PIPE)
        except OSError:
            found = False
    return found, windows_paths, is_windows

def bes_unit_size(f_size):
    """Get a size in bytes and convert it for the best unit for readability.
    
    Return two values:
    
    (int) bu_size -- Size of the path converted to the best unit for easy read
    (str) unit -- The units (IEC) for bu_size (from bytes(2^0) to YiB(2^80))
    
    """
    for exp in range(0, 90 , 10):
        bu_size = f_size / pow(2.0, exp)
        if int(bu_size) < 2 ** 10:
            unit = {0:'bytes', 10:'KiB', 20:'MiB', 30:'GiB', 40:'TiB', 50:'PiB',
                    60:'EiB', 70:'ZiB', 80:'YiB'}[exp]
            break
    return {'s':bu_size, 'u':unit}

def get_size(the_path):
    """Get size of a directory tree or a file in bytes."""
    path_size = 0
    if os.path.isfile(the_path):
        path_size = os.path.getsize(the_path)
    for path, dirs, files in os.walk(the_path):
        for fil in files:
            filename = os.path.join(path, fil)
            path_size += os.path.getsize(filename)
    return path_size

def get_sub(tt_id , tt_intro, sub):
    """Get TED Subtitle in JSON format & convert it to SRT Subtitle
    Obtiene el subtitulo de TED en formato JSON y lo convierte al formato SRT"""

    def srt_time(tst):
        """Format Time from TED Subtitles format to SRT time Format
        Convierte el formato de tiempo del subtitulo TED al formato de SRT"""
        secs, mins, hours = ((tst / 1000) % 60), (tst / 60000), (tst / 3600000)
        right_srt_time = "{0:02d}:{1:02d}:{2:02d},000".format(hours, mins, secs)
        return right_srt_time

    srt_content = ''
    sub_log = ''
    tt_url = 'http://www.ted.com/talks'
    lang = sub.split('.')[1]
    sub_url = '{0}/subtitles/id/{1}/lang/{2}'.format(tt_url, tt_id, lang)
    ## Get JSON sub
    if FOUND:
        json_file = Popen([WGET, '-q', '-O', '-', sub_url],
                          stdout=PIPE).stdout.readlines()

        if json_file:
            for line in json_file:
                if line.find('captions') == -1 and line.find('status') == -1:
                    json_file.remove(line)
        else:
            sub_log += "Subtitle '{0}' not found".format(sub)
    else:
        json_file = urllib2.urlopen(sub_url).readlines()
    try:
        json_object = json.loads(json_file[0])
        if 'captions' in json_object:
            caption_idx = 1
            if not json_object['captions']:
                sub_log += "Subtitle '{0}' not completed".format(sub)
            for caption in json_object['captions'] :
                start = tt_intro + caption['startTime']
                end = start + caption['duration']
                idx_line = '{0}'.format(caption_idx)
                time_line = '{0} --> {1}'.format(srt_time(start), srt_time(end))
                text_line = '{0}'.format(caption['content'].encode("utf-8"))
                srt_content += '\n'.join([idx_line, time_line, text_line, '\n'])
                caption_idx += 1
        elif 'status' in json_object:
            sub_log += os.linesep.join(["TED error message ({0}):".format(sub),
                                        '', json_object['status']['message'],
                                        os.linesep])
    except ValueError:
        sub_log += "Subtitle '{0}' it's a malformed json file".format(sub)
    return srt_content, sub_log

def check_subs(ttalk, v_name):
    """Check if the subtitles for the talk are downloaded, if not try to get 
    them. Checks it for english and spanish languages
    Comprueba si los subtitulos para la charla estan descargados, si no, intenta
    obtenerlos. Lo comprueba para los idiomas español e ingles"""
    ## Get the names for the subtitles (for english and spanish languages) only 
    # if they not are already downloaded
    subs = (s_name for s_name in
            ("{0}.{1}.srt".format(v_name[:-4], lang) for lang in ('eng', 'spa'))
            if s_name not in glob.glob('*.srt'))
    s_log = ''
    for sub in subs:
        ## Reads the talk web page, to search the talk's intro duration
        if FOUND:
            tt_webpage = Popen([WGET, '-q', '-O', '-',
                                ttalk.feedburner_origlink],
                                stdout=PIPE).stdout.read()
        else:
            tt_webpage = urllib2.urlopen(ttalk.feedburner_origlink).read()
        tt_intro = int(search("introDuration:(\d+),", tt_webpage).group(1))
        subtitle, get_log = get_sub(ttalk.id.split(':')[-1], tt_intro, sub)
        s_log += get_log
        if subtitle:
            with open(sub, 'w') as srt_file:
                srt_file.write(subtitle)
            s_log += "\n{0} downloaded".format(sub)
    return s_log

def get_video(ttk, vid_url, vid_name):
    """Gets the TED Talk video
    Obtiene el video de la TED Talk"""
    if FOUND:
        Popen([WGET, '-q', '-O', vid_name, vid_url], stdout=PIPE).stdout.read()
    else:
        urllib.urlretrieve(vid_url, vid_name)
    v_log = '{0} ({1})\n'.format(ttk.subtitle, ttk.itunes_duration)
    v_log += '{0}\n\n'.format('=' * (len(ttk.subtitle) + 11))
    v_log += '{0}\n\n'.format(ttk.feedburner_origlink)
    v_log += '{0}\n\n'.format(ttk.content[0].value)
    v_log += 'file://{0}\n'.format(os.path.join(os.getcwd(), vid_name))
    vid_size = bes_unit_size(get_size(vid_name))
    v_log += '{0:.2f} {1}\n\n'.format(vid_size['s'], vid_size['u'])
    return v_log

def main():
    """main section"""

#===============================================================================
# SCRIPT PARAMETERS
#===============================================================================

    ## The directory to store the videos and subs. 
    # For Windows change the character '\' for the character '/', I know is 
    # akward but is because how escape strings python
    ttalk_vid_dir = '/your/path/to/TED/Talks/Videos'

#===============================================================================
# END PARAMETERS
#===============================================================================

    # initalize the log
    log = Logger()

    # log the header
    url = 'http://code.joedicastro.com/ted-talks-download'
    msg = 'Download TED Talks from HD RSS Feed'
    log.header(url, msg)

    # log the start time
    log.time('Start Time')

    os.chdir(os.path.normpath(ttalk_vid_dir))

    ## Get a list of the current TED Talks downloaded in the dir
    videos = glob.glob('*.mp4')

    ## Get the last download Talk video date
    try:
        with open('.data.pkl', 'rb') as pkl_file:
            last = pickle.load(pkl_file)
    except (EOFError, IOError, pickle.PickleError):
        last = time.localtime(time.time() - 86400)
    video_dates = []

    ## The TED Talks HD RSS feed
    ttalk_feed_url = 'http://feeds.feedburner.com/tedtalksHD'
    ttalk_feed = feedparser.parse(ttalk_feed_url)

    ## If the feed is erroneous or occurs a http or network error, log and exit!
    if ttalk_feed.bozo:
        log.list('An error occurred', str(ttalk_feed.bozo_exception))
        if not WIN_OS:
            log.send('Download TED Talks')
        sys.exit(1)

    ## If correct, process the feed entries
    vids_log, subs_log = '', ''
    for ttalk_entrie in ttalk_feed.entries:
        ## Get The video url and name
        tt_vid_url = ttalk_entrie.enclosures[0].href
        tt_vid_name = tt_vid_url.split('/')[-1]
        ## If the video is new, download it!
        if ttalk_entrie.updated_parsed > last:
            vids_log += get_video(ttalk_entrie, tt_vid_url, tt_vid_name)
            videos.append(tt_vid_name)
            video_dates.append(ttalk_entrie.updated_parsed)
        ## If video is already downloaded, check if subs exists, if not, get it!
        if tt_vid_name in videos:
            subs_log += check_subs(ttalk_entrie, tt_vid_name)
    log.list('Talks downloaded', vids_log)
    log.list('Subs downloaded', [subs_log])

    ## Set the last download video date
    if video_dates:
        last = max(video_dates)
        with open('.data.pkl', 'wb') as output:
            pickle.dump(last, output)

    log.time('End time')
    ## If logs any activity, sends the information mail 
    if not WIN_OS:
        log.send('Download TED Talks')
    log.write(False)


if __name__ == "__main__":
    FOUND, WIN_EXECS, WIN_OS = check_exec_posix_win('wget')
    if FOUND:
        WGET = WIN_EXECS['wget'] if WIN_OS else 'wget'
    main()

