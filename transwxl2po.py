#!/usr/bin/python

import getopt, sys
import textwrap
from xml.dom import minidom
import polib

def version():
    print "transwxl2pot.py version 0.1\n"

def help():
    print textwrap.dedent("""
      Usage: transwxl2pot.py [OPTION]... WXL_SOURCE_FILE WXL_TRANSLATED_FILE POT_DEST_FILE
      Transform the file WXL_SOURCE_FILE in wxl format into a po file POT_DEST_FILE
      containing the translations from WXL_TRANSLATED_FILE
      Example: transwxl2pot.py -l LangId en-us.wxl fr-fr.wxl fr-fr.po

      Options:
        -h, --help:            print this help message and exit
        -V, --version          print version information and exit
        -l, --langid=LANGID    ignore string with Id LANGID containing the LCID
""")

def usage():
    print textwrap.dedent("""\
      Usage: transwxl2pot.py [OPTION]... WXL_SOURCE_FILE WXL_TRANSLATED_FILE POT_DEST_FILE
      Try 'transwxl2pot.py --help' for more information.
    """)


# Main

langid = ""
try:
    opts, args = getopt.getopt(sys.argv[1:], "hVl:", ["help", "version", "langid="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
output = None
verbose = False
for o, a in opts:
    if o in ("-V", "--version"):
        version()
        sys.exit()
    elif o in ("-h", "--help"):
        help()
        sys.exit()
    elif o in ("-l", "--langid"):
        langid = a
    else:
        assert False, "unhandled option"

if len(args) < 3:
    usage()
    sys.exit(1)

sourcefile = args[0]
transfile = args[1]
destfile = args[2]


transdoc = minidom.parse(transfile)

transwixloc = transdoc.getElementsByTagName("WixLocalization")[0]
transculture = transwixloc.getAttribute("Culture")

transculture = transculture[:transculture.index('-')] + '_' + transculture[(transculture.index('-') + 1):].upper()

transroot = transdoc.documentElement
transnodes = transroot.childNodes

translatedStrings = {}

for node in transnodes:
    if node.nodeType == node.ELEMENT_NODE:
        if node.tagName == "String":
            stringId = node.getAttribute("Id")
            if stringId == langid:
                continue
            stringContent = node.firstChild.data
            translatedStrings[stringId] = stringContent


doc = minidom.parse(sourcefile)

wixloc = doc.getElementsByTagName("WixLocalization")[0]
culture = wixloc.getAttribute("Culture")
codepage = wixloc.getAttribute("Codepage")

po = polib.POFile(wrapwidth=0)
po.metadata = {
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Transfer-Encoding': '8bit',
    'Language': transculture
}

root = doc.documentElement
nodes = root.childNodes

comment = ""

for node in nodes:
    if node.nodeType == node.COMMENT_NODE:
        comment = node.data
    if node.nodeType == node.ELEMENT_NODE:
        if node.tagName == "String":
            stringId = node.getAttribute("Id")
            if stringId == langid:
                continue

            stringContent = node.firstChild.data
            if stringId in translatedStrings:
                translation = translatedStrings[stringId]
            else:
                translation = stringContent; 
            entry = polib.POEntry(
                comment = comment,
                msgctxt = stringId,
                msgid = stringContent,
                msgstr = translation
            )
            po.append(entry)
            if comment != "":
                comment = ""
po.save(destfile)
