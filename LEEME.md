# TED Talks Download

Son un par de scripts escritos en python que sirven para descargar vídeos y
subtítulos de las famosas charlas **[TED Talks](http://ted.com)**


## TEDTalks.py

Este script descarga automáticamente (programando su ejecución) los vídeos y
subtítulos de las nuevas charlas publicadas en TED. Lo hace en calidad HD y
emplea la propia [fuente RSS de TED en HD](http://feeds.feedburner.com/tedtalksHD)
para conocer cuales son las últimas charlas publicadas.

Está basado en la idea de un
[script anterior](http://fci-h.blogspot.com/2010/05/python-script-to-download-ted-talks.html),
también escrito en python, por
[Shereef Sakr](http://www.blogger.com/profile/14485464016030085189).
Aunque realmente el funcionamiento de este es más parecido al de TEDSubs.py,
este me inspiró para crear este script y posteriormente el otro. Shereef,
gracias por tú trabajo.

## TEDSubs.py

Este script descarga el vídeo y/o los subtítulos de una charla determinada, que
le indicamos a través de la dirección web de la misma. Los subtítulos los
descarga en los idiomas inglés y español, si están disponibles.


## Requisitos previos y dependencias

Lógicamente, lo primero que necesitamos para ejecutarlos es
[python](http://www.python.org/). Si estamos en Linux o en Mac, normalmente
viene instalado por defecto y no es un problema. Si nos encontramos en Windows,
entonces nos lo podemos bajar de [aquí.](http://www.python.org/download/)

La versión de python necesaria para ejecutar ambos scripts es la 2.6

TEDTalks.py emplea varios módulos que están presentes en la biblioteca estándar
de python, excepto uno, [feedparser](http://www.feedparser.org/), que deberemos
instalar necesariamente.

El maravilloso módulo feedparser de
[Mark Pilgrim](http://en.wikipedia.org/wiki/Mark_Pilgrim), suele venir por
defecto en los repositorios de las distribuciones linux más populares, por lo
que solo sería necesario instalarlo.

Por ejemplo para debian/Ubuntu sería así:

    sudo aptitude install python-feedparser

Para Windows, lo bajaríamos de
[aquí](http://code.google.com/p/feedparser/downloads/list) y lo instalaríamos:

    (ruta en donde has instalado python)\python.exe setup.py install

TEDsubs.py solo emplea módulos de la biblioteca estándar de python, por lo que
no necesita ninguna instalación adicional.

## Instrucciones

### TEDTalks.py

Este es el más sencillo de utilizar, ya que no hay que hacer nada, solo
ejecutarlo. Esta pensado para que se ejecute automáticamente de forma programada,
es decir, que se ejecutara todos los días a una misma hora.

Para ello emplearíamos por ejemplo las Tareas programadas en Windows y cron en
linux o Mac para establecer una programación diaria del script.

Si lo ejecutamos sin pasarle ningún parámetro utiliza la carpeta desde donde
está siendo ejecutado como lugar donde almacenar las charlas y los subtítulos.
Si en cambio, queremos emplear una ruta distinta, simplemente tenemos que
pasarsela como un parametro.

La sintaxis del comando es la siguiente:

    python TEDTalks.py [path]

donde `path` es la ruta opcional donde queremos almacenar las charlas.

Si ejecutamos el comando con la opción `-h` nos saldría la ayuda del mismo:

    $ python TEDTalks.py -h
    usage: TEDTalks.py [-h] [-v] [path]

    Automate download new HD TED Talks by its RSS Feed

    positional arguments:
      path           The path to store the TED Talks videos

    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit

Cuando se ejecute por primera vez, se bajara el vídeo del día anterior (si
hubiese alguno) y los subtítulos en ingles o español que estén disponibles para
el mismo. En las siguientes ejecuciones del script se descargara el último vídeo
publicado en la fuente RSS en HD y además comprobara la disponibilidad de
subtítulos (ingles y español) para todos los vídeos recientemente descargados
(los que aún aparecen en las entradas del RSS) que aún se encuentren en la
carpeta. Si está disponible algún subtitulo que aún no ha sido descargado, lo
descarga.

Si se descarga algo, tanto subtítulos como vídeos, envía un correo al usuario
local de la maquina con el resultado del mismo (esto solo funciona en linux, no
lo he probado en Mac)


### TEDSubs.py

Este script requiere de un parámetro para su ejecución y dispone de una opción
(descargar solo los subtítulos).
La sintaxis de la línea de comandos es la siguiente:

    python TEDSubs.py [Options] TEDTalkURL

donde la opción es `-s` (ó `--only_subs`) y `TEDTalkURL` es la dirección web de la charla.

Si ejecutáramos el comando sin ningún parámetro, nos saldría la ayuda del mismo, así

    $ python TEDSubs.py
    Usage: TEDSubs.py [Options] TEDTalkURL

    Where TEDTalkURL is the url of a TED Talk webpage

    For example:

    TEDSubs.py -s  http://www.ted.com/talks/lang/eng/jamie_oliver.html

    Downloads only the subs for the Jamie Oliver's TED Talk, if wants the video too
    only needs to remove the "-s" option

    Downloads the subtitles and the video (optional) for a TED Talk.

    Options:
      --version        show program's version number and exit
      -h, --help       show this help message and exit
      -s, --only_subs  download only the subs, not the video

Donde se ve un ejemplo de como bajar solo los subtítulos de la
[charla de Jamie Oliver](http://www.ted.com/talks/lang/spa/jamie_oliver.html)

    python TEDSubs.py -s  http://www.ted.com/talks/lang/eng/jamie_oliver.html

Si quisiéramos bajarnos también el vídeo, solo tendríamos que eliminar la opción `-s`

    python TEDSubs.py http://www.ted.com/talks/lang/eng/jamie_oliver.html

Y así con todas las charlas, lo único necesario es substituir la dirección web
de la charla de Oliver por la que deseemos descargar.

## Como obtenerlos

El código está alojado en un repositorio Git en GitHub, emplea este comando para
poder clonarlo:

    git clone git://github.com/joedicastro/ted-talks-download.git


## Características

Los vídeos de las charlas se descargan en formato .mp4 en calidad HD
(normalmente 850 x 450 pixels) y los subtítulos se transforman del original
formato en json a el común formato .srt en que son guardados.

## Alternativas

Si mis scripts no encajan con lo que quieres, aquí tienes un resumen de alternativas (las que conozco)

* __TEDTalks.py__

  - Lenguaje: Python
  - Tipo: script
  - Características: Automatiza las descargas de las TED Talks & subtítulos (ing/esp) por medio de su fuente RSS en HD
  - Autor: Yo

* __TEDSubs.py__

  - Lenguaje: Python
  - Tipo: script
  - Características: Descarga los videos & subtítulos (eng/spa) de las TED Talks por su direccion web
  - Autor: Yo

* __[TEDSubtitles.py](http://fci-h.blogspot.com/2010/05/python-script-to-download-ted-talks.html)__

  - Lenguaje: Python
  - Tipo: script
  - Características: Descarga los subtítulos de TED Talks por su dirección web para un idioma dado
  - Autor: [Shereef Sakr](http://www.blogger.com/profile/14485464016030085189)

* __[metaTED](http://bitbucket.org/petar/metated)__

  - Lenguaje: Python
  - Tipo: web
  - Características: Crea ficheros metalink de las TED talks para una descarga sencilla
  - Autor: [Petar Marić](http://www.petarmaric.com/)

* __[tedget.py](http://bitbucket.org/johannes/tedget)__

  - Lenguaje: Python
  - Tipo: script
  - Características: Descarga los vídeos de TED Talks por su url o id
  - Autor: [Johannes Hoff](http://johanneshoff.com/)

* __[Ted Talk Subtitle Download](http://tedtalksubtitledownload.appspot.com/)__

  - Lenguaje: Python
  - Tipo: Web
  - Características: Descarga subtítulos de TED Talks por su dirección web
  - Autor: [Esteban Ordano](http://estebanordano.com.ar/)

* __[Miro](http://www.getmiro.com)__

  - Lenguaje: Python & GTK
  - Tipo: Aplicación escritorio
  - Características: Agregador RSS, Reproductor de Vídeo & cliente Bittorrent. Puede descargar los vídeos de TED Talks y reproducirlos
  - Autor: [Participatory Culture Foundation](http://participatoryculture.org/)


## Contribuciones

Las contribuciones y las ideas son bienvenidas. Para contribuir a la mejora y
evolución de este script, puedes enviar sugerencias o errores a través de el
sistema de issues.

## Licencia

Ambos scripts están sujetos a la [Licencia GPLv3 ](http://www.gnu.org/licenses/gpl.html)
