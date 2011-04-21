#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
    TEDSubs.py: Downloads a TED Talk' subtitles and videos by it's url
"""

#===============================================================================
# This Script uses a TED Talk URL to download the talk's video and 
# subtitles.
#
# Este script emplea la url de una TED Talk y descarga el video y los
# subtitulos de la misma
#===============================================================================

#===============================================================================
#    Copyright 2010 joe di castro <joe@joedicastro.com>
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
__date__ = "26/01/2011"
__version__ = "1.4"

try:
    import sys
    import os
    import optparse
    import json
    import platform
    import urllib
    import urllib2
    from re import search, findall
    from subprocess import Popen, PIPE
except ImportError:
    # Checks the installation of the necessary python modules 
    # Comprueba si todos los módulos necesarios están instalados
    print((os.linesep * 2).join(["An error found importing one module:",
    str(sys.exc_info()[1]), "You need to install it", "Stopping..."]))
    sys.exit(-2)

def options():
    """Defines the command line arguments and options for the script
    Define los argumentos y las opciones de la linea de comandos del script"""
    usage = """usage: %prog [Options] TEDTalkURL
    
    Where TEDTalkURL is the url of a TED Talk webpage

    For example:

    %prog -s  http://www.ted.com/talks/lang/eng/jamie_oliver.html

    Downloads only the subs for the Jamie Oliver's TED Talk, if wants the video 
    too only needs to remove the "-s" option"""
    desc = "Downloads the subtitles and the video (optional) for a TED Talk."
    parser = optparse.OptionParser(usage=usage, version="%prog " + __version__,
                                   description=desc)

    parser.add_option("-s", "--only_subs", action='store_true', dest="no_video",
                      help="download only the subs, not the video ",
                      default=False)

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
    tt_url = 'http://www.ted.com/talks'
    sub_url = '{0}/subtitles/id/{1}/lang/{2}'.format(tt_url, tt_id, sub[-7:-4])
    ## Get JSON sub
    if FOUND:
        json_file = Popen(['wget', '-q', '-O', '-', sub_url],
                          stdout=PIPE).stdout.readlines()

        if json_file:
            for line in json_file:
                if line.find('captions') == -1 and line.find('status') == -1:
                    json_file.remove(line)
        else:
            print("Subtitle '{0}' not found.".format(sub))
    else:
        json_file = urllib2.urlopen(sub_url).readlines()

    try:
        json_object = json.loads(json_file[0])
        if 'captions' in json_object:
            caption_idx = 1
            if not json_object['captions']:
                print("Subtitle '{0}' not available.".format(sub))
            for caption in json_object['captions'] :
                start = tt_intro + caption['startTime']
                end = start + caption['duration']
                idx_line = '{0}'.format(caption_idx)
                time_line = '{0} --> {1}'.format(srt_time(start), srt_time(end))
                text_line = '{0}'.format(caption['content'].encode("utf-8"))
                srt_content += '\n'.join([idx_line, time_line, text_line, '\n'])
                caption_idx += 1
        elif 'status' in json_object:
            print("This is an error message returned by TED:{0}{0} - {1}{0}{0}"
                  "Probably because the subtitle '{2}' is not available.{0}"
                  "".format(os.linesep, json_object['status']['message'], sub))
    except ValueError:
        print("Subtitle '{0}' it's a malformed json file.".format(sub))
    return srt_content


def check_subs(tt_id, tt_intro, tt_video):
    """Check if the subtitles for the talk exists and try to get them. Checks it
    for english and spanish languages.
    Comprueba si los subtitulos para la charla existen e intenta obtenerlos. Lo 
    comprueba para los idiomas español e ingles"""
    ## Get the names for the subtitles (for english and spanish languages) only 
    # if they not are already downloaded
    subs = ("{0}.{1}.srt".format(tt_video[:-4], lang) for lang in
            ('eng', 'spa'))
    for sub in subs:
        subtitle = get_sub(tt_id, tt_intro, sub)
        if subtitle:
            with open(sub, 'w') as srt_file:
                srt_file.write(subtitle)
            print("Subtitle '{0}' downloaded.".format(sub))
    return

def get_video(vid_name, vid_url):
    """Gets the TED Talk video
    Obtiene el video de la TED Talk"""
    print("Donwloading video...")
    if FOUND:
        Popen(['wget', '-q', '-O', vid_name, vid_url], stdout=PIPE).stdout.read()
    else:
        urllib.urlretrieve(vid_url, vid_name)
    print("Video {0} downloaded.".format(vid_name))
    return

def main():
    """main section"""
    # first, parse the options & arguments
    (opts, args) = options().parse_args()
    issue_url = "http://code.joedicastro.com/ted-talks-download/issues/new"

    if not args:
        options().print_help()
    else:
        tedtalk_webpage = args[0]
        ## Reads the talk web page, to search the talk's values
        if FOUND:
            ttalk_webpage = Popen(['wget', '-q', '-O', '-', tedtalk_webpage],
                                  stdout=PIPE).stdout.read()
        else:
            try:
                ttalk_webpage = urllib2.urlopen(tedtalk_webpage).read()
            except ValueError:
                ttalk_webpage = urllib2.urlopen('http://' +
                                                tedtalk_webpage).read()
        if ttalk_webpage:
            try:
                ttalk_intro = int(search("introDuration:(\d+),",
                                         ttalk_webpage).group(1))
                ttalk_id = int(search("talkID = (\d+);",
                                      ttalk_webpage).group(1))
            except AttributeError:
                if search("Best of the Web", ttalk_webpage):
                    print("This is a video from a external website.{0}Video and"
                          " subtitles not available via this script, try at the"
                          " original video's website.".format(os.linesep))
                else:
                    print("Some data not found in this URL:{0}{1}{0}Please "
                          "report this error and provides the URL to check at:"
                          "{0}{2}{0}Thanks for helping to fix errors.{0}"
                          "".format(os.linesep * 2, tedtalk_webpage, issue_url))
                sys.exit(1)
            ttalk_dwn = ''
            try:
                ttalk_dwn = search('href="(.*)">Watch high-res video',
                                   ttalk_webpage).group(1)
            except AttributeError:
                try:
                    ttalk_dwn = search('href="(.*)">Download video to desktop',
                                       ttalk_webpage).group(1)
                except AttributeError:
                    print('This video is not available for download.')
            if ttalk_dwn:
                if FOUND:
                    ttalk_lnk = Popen(['wget', '--spider',
                                       'http://ted.com/{0}'.format(ttalk_dwn)],
                                       stderr=PIPE).stderr.read()
                    ttalk_url = search('  (http://.*/.*\.mp4)\\n',
                                       ttalk_lnk).group(1)
                else:
                    ttalk_url = urllib2.urlopen('http://ted.com' +
                                                ttalk_dwn).geturl()
                ttalk_vid = search('http://.+\/(.*\.mp4)', ttalk_url).group(1)
        else:
            print("Are you sure this is the right URL?")
            sys.exit(1)
        ## Get subs (and video)
        check_subs(ttalk_id, ttalk_intro, ttalk_vid)
        if not opts.no_video and ttalk_dwn:
            get_video(ttalk_vid, ttalk_url)


if __name__ == "__main__":
    WIN_OS = True if platform.system() == 'Windows' else False
    if not WIN_OS:
        FOUND = check_exec_posix('wget')
    main()

