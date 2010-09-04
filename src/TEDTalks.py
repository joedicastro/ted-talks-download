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
__date__ = "28/07/2010"
__version__ = "0.4"

try:
    import os
    import sys
    import json
    import urllib
    import re
    import glob
    import feedparser
    import smtplib
    import time
    import socket
    import pickle
    import platform
except ImportError:
    # Checks the installation of the necessary python modules 
    # Comprueba si todos los módulos necesarios están instalados
    print ("""An error found importing one or more modules:
    \n{0}
    \nYou need to install this module\nQuitting...""").format(sys.exc_info()[1])
    sys.exit(-2)


def send_mail(content):
    """Send the mail with the log to the user's local mailbox
    Envia el correo con el informe al buzón del usuario local"""
    # Set the local mail address for the script' user
    email = '{0}@{1}'.format(os.getenv('LOGNAME'), socket.gethostname())
    subject = 'Download TED Talks - {0}'.format(time.strftime('%A %x, %X'))
    msg = ("From: {0}\nTo: {0}\nSubject: {1}\n{2}".
           format(email, subject, content))
    server = smtplib.SMTP('localhost')
    server.sendmail(email, email, msg)
    server.quit()
    return

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

def get_sub(tt_id , tt_intro, lang):
    """Get TED Subtitle in JSON format & convert it to SRT Subtitle
    Obtiene el subtitulo de TED en formato JSON y lo convierte al formato SRT"""

    def srt_time(tst):
        """Format Time from TED Subtitles format to SRT time Format
        Convierte el formato de tiempo del subtitulo TED al formato de SRT"""
        secs, mins, hours = ((tst / 1000) % 60), (tst / 60000), (tst / 3600000)
        right_srt_time = "{0:02d}:{1:02d}:{2:02d},000".format(hours, mins, secs)
        return right_srt_time

    srt_content = ''
    tt_url = 'http://www.ted.com/talks'
    sub_url = '{0}/subtitles/id/{1}/lang/{2}'.format(tt_url, tt_id, lang)
    json_object = json.loads(urllib.urlopen(sub_url).read()) ## Get JSON sub
    if 'captions' in json_object:
        caption_idx = 1
        for caption in json_object['captions'] :
            start = tt_intro + caption['startTime']
            end = start + caption['duration']
            idx_line = '{0}'.format(caption_idx)
            time_line = '{0} --> {1}'.format(srt_time(start), srt_time(end))
            text_line = '{0}'.format(caption['content'].encode("utf-8"))
            srt_content += '\n'.join([idx_line, time_line, text_line, '\n'])
            caption_idx += 1
    return srt_content

def check_subs(ttalk, v_name):
    """Check if the subtitles for the talk are downloaded, if not try to get 
    them. Checks it for english and spanish languages
    Comprueba si los subtitulos para la charla estan descargados, si no, intenta
    obtenerlos. Lo comprueba para los idiomas español e ingles"""
    s_log = '' # Begins the log
    ## Get the names for the subtitles (for english and spanish languages) only 
    # if they not are already downloaded
    subs = (s_name for s_name in
            ("{0}.{1}.srt".format(v_name[:-4], lang) for lang in ('eng', 'spa'))
            if s_name not in glob.glob('*.srt'))

    for sub in subs:
        ## Reads the talk web page, to search the talk's intro duration
        tt_webpage = urllib.urlopen(ttalk.feedburner_origlink).read()
        tt_intro = int(re.search("introDuration:(\d+),", tt_webpage).group(1))
        subtitle = get_sub(ttalk.id.split(':')[-1], tt_intro, sub.split('.')[1])
        if subtitle:
            with open(sub, 'w') as srt_file:
                srt_file.write(subtitle)
            s_log += "\n{0} downloaded".format(sub)
    return s_log

def get_video(ttk, vid_url, vid_name):
    """Gets the TED Talk video
    Obtiene el video de la TED Talk"""
    urllib.urlretrieve(vid_url, vid_name)
    v_log = 'New TED Talk downloaded!\n'
    v_log += '{0}\n'.format('=' * 24)
    v_log += '{0}\n\n'.format(ttk.feedburner_origlink)
    v_log += '{0}'.format(ttk.subtitle)
    v_log += ' ({0})\n\n'.format(ttk.itunes_duration)
    v_log += '{0}\n\n'.format(ttk.content[0].value)
    v_log += 'file://{0}/{1}\n'.format(os.getcwd(), vid_name)
    vid_size = bes_unit_size(get_size(vid_name))
    v_log += '{0:.2f} {1}\n\n'.format(vid_size['s'], vid_size['u'])
    return v_log

def main(log=''):
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

    os.chdir(os.path.normpath(ttalk_vid_dir))

    ## Get a list of the current TED Talks downloaded in the dir
    videos = glob.glob('*.mp4')

    is_windows = True if platform.system() == 'Windows' else False

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
        log += 'An error occurred: {0}'.format(ttalk_feed.bozo_exception)
        if not is_windows:
            send_mail(log)
        sys.exit(1)

    ## If correct, process the feed entries
    for ttalk_entrie in ttalk_feed.entries:
        ## Get The video url and name
        tt_vid_url = ttalk_entrie.enclosures[0].href
        tt_vid_name = tt_vid_url.split('/')[-1]
        ## If the video is new, download it!
        if ttalk_entrie.updated_parsed > last:
            log += get_video(ttalk_entrie, tt_vid_url, tt_vid_name)
            videos.append(tt_vid_name)
            video_dates.append(ttalk_entrie.updated_parsed)
        ## If video is already downloaded, check if subs exists, if not, get it!
        if tt_vid_name in videos:
            log += check_subs(ttalk_entrie, tt_vid_name)

    ## Set the last download video date
    if video_dates:
        last = max(video_dates)
        with open('.data.pkl', 'wb') as output:
            pickle.dump(last, output)

    ## If logs any activity, sends the information mail 
    if log and not is_windows:
        send_mail(log)

if __name__ == "__main__":
    main()

