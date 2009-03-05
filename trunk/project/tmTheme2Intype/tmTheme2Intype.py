"""
 TMTheme to ITTheme
 Converts a Textmate Theme to an Intype Theme. May not be perfect,
 but its a start.

 Author:    Mario Parris
 E-Mail:    marioparris [at] gmail [dot] com / theboy [at] theboywhorawred [dot] com
 URL:       http://theboywhorawred.com/intype/

 Author:    Jason Lee <http://huacn.blogbus.com>
 Email:     huacnlee [at] gmail.com

 Changes
 -------
     0.4.1
        - Add auto convert method,there well auto find the Textmate theme files to convert.
        
     0.4
        - Fix: No longer adds more than empty scope element. The first empty scope element should only be used to provide the base theme settings.
               Some themes such as BBCP basically had two, which cause problems with the background colours.
        - Fix: No longer adds those odd '----------------------' elements from the tmTheme to the itTheme. Fixes line_highlight problems. Thanks dflock!
        - Fix: Strips newline characters and replaces them with spaces. Not sure how this affects themes, nothing bad has happened from doing this.
     0.3
        - Now uses ElementTree to parse tmThemes
        - Intype supports the 8 digit hex codes which allow for alpha depth. `sixIsHexy` is no longer called on setting values.
        - Now handles Unicode better, through no fault of my own. Probably elementtree :o) 
        - Intype themes are saved in UTF-8, because of above reason.
    
    0.2
        - Creation of the theme elements 'title' and 'scope' are no longer mandatory. They are now created if they are in the tmTheme, if they
          aren't, they're simply skipped. This might not be the best solution.  

"""

# Standard Python Libs
import sys
import base64
import datetime
import re
from os import path

# ElementTree & cElementTree Lib
# http://effbot.org/downloads/

try:
    import cElementTree as ET
    from cStringIO import StringIO
except ImportError:
    try:
        import elementtree.ElementTree as ET
    except ImportError:
        print "Uh oh! The elementtree module couldn't be imported. You need to install elementree from http://effbot.org/downloads/ (ImportError)"

unmarshallers = {

    # collections
    "array": lambda x: [v.text for v in x],
    "dict": lambda x:
        dict((x[i].text, x[i+1].text) for i in range(0, len(x), 2)),
    "key": lambda x: x.text or "",

    # simple types
    "string": lambda x: x.text or "",
    "data": lambda x: base64.decodestring(x.text or ""),
    "date": lambda x: datetime.datetime(*map(int, re.findall("\d+", x.text))),
    "true": lambda x: True,
    "false": lambda x: False,
    "real": lambda x: float(x.text),
    "integer": lambda x: int(x.text),

}



# Matches those unexplained series of dashes in the theme settings
TM_THEME_COMMENT = re.compile(r"^----")
# Matches line breaks so we can replace them with spaces
LINEBREAKS = re.compile(r"[\n|\r]+")


def tidyWhitey(string):
    """Cleans line breaks from the scope selectors, replacing them with spaces"""
    return LINEBREAKS.sub(" ", string)



    
def removeHump(match):
    """
    Takes a regex match, converts the string to lowercase and prefixes it with
    an underscore. Essentially, it removes any humps!
    """
    return "_" + match.group().lower()



def removeHumps(string):
    """
    Converts camelCase to camel_case. Used to convert key names like 'fontStyle'
    to 'font_style'.
    """
    r = re.compile('[A-Z]')
    return r.sub(removeHump, string)    



def sixIsHexy(string):
    """
    Strips the last the last 2 digits off of an 8 digit hex colour code. 
    Those last 2 digits are apparently for alpha (transparency?). 
    
    Turns out, Intype does support the alpha codes, so this function
    is no longer called on values. Its just here for er, historical
    reasons :)
    """

    r = re.compile(r"^#([\d\w]{6})([\d\w]{2})$")
    match = r.match(string)  

    if match:
        return "#" + match.group(1)
    else:
        return string



def load(file):
    """ 
    Loads an Apple Property List (XML) and parses it 
    Source: http://effbot.org/zone/element-iterparse.htm
    """
    parser = ET.iterparse(file)
    for action, elem in parser:
        unmarshal = unmarshallers.get(elem.tag)
        if unmarshal:
            data = unmarshal(elem)
            elem.clear()
            elem.text = data
        elif elem.tag != "plist":
            raise IOError("Unknown plist type: %r" % elem.tag)
    return parser.root[0].text
    

def convert(tmTheme,outinfo=False):

    try:
        plist = load(tmTheme)
    
        # print "Attempting to convert %s to an Intype Theme... " % (plist['name'])
    
        themeElements = plist['settings']
    
        # Creates the main theme settings
        themeSettings = themeElements[0]['settings']
        # print themeSettings
        themeSettingsText = "\n\t\t\t\t" + "\n\t\t\t\t".join(["%s : '%s'" % (removeHumps(k), v) for k, v in themeSettings.items()])
        # print themeSettingsText
    
        themeScopes = []
    
        
        # Create a list of theme scopes
        for i in range(1, len(themeElements)):
            themeElement = themeElements[i]
            
            if 'scope' in themeElement:
                # Create the scope element
                elementText = "{"
    
                for key, value in themeElement.items():
                    # create title, scope & settings triples
                    # changes 'name' in tmTheme to 'title' in itTheme

                    if key == 'name' and TM_THEME_COMMENT.match(value):
                        # don't add scopes with a name like '------------------' since those seem to cause problems
                        break
                    else:
                        if key != 'settings':
                            elementText += "\n\t\t\t%s : '%s'" % (('title' if key =='name' else key), tidyWhitey(value))
                        # create scope settings
                        else:
                            elementText += "\n\t\t\t" + key + " : { \n\t\t\t\t"
                            # Setting details
                            elementTextSettings = "\n\t\t\t\t".join(["%s : '%s'" % (removeHumps(k), v) for k, v in value.items()])
                            elementTextSettings += "\n\t\t\t}"

                            # Add settings onto the rest of the text
                            elementText += elementTextSettings
                    
                # Close the scope    
                elementText += "\n\t\t}"
    
                # Add scope element to the list, don't add empty scopes
                if elementText != "{\n\t\t}":
                    themeScopes.append(elementText)
            else:
                print "Empty Scope ignored"
    
        # Put together the itTheme
        themeInfoText = "{\n\ttitle: '%s' \n\tsettings: [\n\t\t{\n\t\t\tsettings : { \n\t\t\t\t" % (plist['name'])
    
        themeScopesText = "\n\t\t".join(themeScopes)
    
        themeText = themeInfoText + themeSettingsText + "\n\t\t\t}\n\t\t}\n\t\t" + themeScopesText +  "\n\t]\n\tuuid : '%s' \n}" % (plist['uuid'])
    
        if outinfo:
            print themeText.encode('utf-8')
    
        # Determine the file name for the new itTheme
    
        tmThemePath, tmThemeFile = path.split(tmTheme)
    
        itThemeFile = path.splitext(tmThemeFile)[0] + '.itTheme'
        print "Saving Intype theme as: " + itThemeFile
    
        # Save the itTheme in the same directory as the original tmTheme
        out = open(path.normpath(path.join(tmThemePath, itThemeFile)), "w")
        out.write(themeText.encode('utf-8'))
        out.close()
        
    except IOError, e:
        print "%s (IO Error)" % (e)
    except Exception, e:
        print "There was an exception. If you want, you can contact with me the theme you're trying to convert and I'll see whats up."
        print e
        
def auto_process_files(dir):	
    dir = str.replace(dir,'\\','/')
    files = os.listdir(dir)
    for f in files:
        # Check the sub directorys
        if((os.path.isdir(f)) and (f != packed_dir_name) ):			
            # If found it,follow it
            print '\r\n@ Found a directory: %s' % f			
            auto_process_files(dir + '/' + f,packed_dir_name)
        else:
            if(f[-8:] == '.tmTheme'):
                # Process file and save it
                old_file_name = dir + '/'+ f
                
                convert(old_file_name)
        
if __name__ == '__main__':
    import os
    print __doc__
    raw_input('Press any key to run me.')
    print 'Progress running..\r\n'    
    auto_process_files(os.getcwd())
    print '\r\nThe process successed.'
    raw_input('Press any key to exit.')
    