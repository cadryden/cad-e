'''
Various helper functions for converting data from the editor.

@author: Chris Alvarado-Dryden
'''
import os
import re
import pygame

class StringConversions(object):    
    @staticmethod
    def StringToIntTuple(string):
        """
        Extracts integers from the given string returns them as  a single tuple.
        
        @type  string:    C{str}
        @param string:    String to scan for integers.
        
        @rtype:           C{tuple}
        @return:          All integers that were present in the string.
        """
        reg = re.compile('\-?\\d+')
        return tuple(map(int, reg.findall(string)))

# don't really like this name - CAD    
class ReflectionFunctions(object):
    @staticmethod
    def GetPythonClass(typeName):
        """
        Gets the python class with the given name.  Assumes Module and Class have the same name.
        This should only be used with CAD-E classes, not standard python classes.
        
        @type  typeName:    C{str}
        @param typeName:    Name of the class to get.  Ex: C{MyPlayer} or C{Map.Tiles.MyTile}
        
        @rtype:             C{class}
        @return:            The python class to instantiate.
        """
        module = __import__(typeName)
        if ('.' in typeName):
            # assume fully qualified name
            # already got the outer most name, so skip it
            parts = typeName.split('.')[1:]
            # last is the class name
            className = parts[-1]
            
            # drill down
            for part in parts:
                module = getattr(module, part)
        else:
            className = typeName
                
        return getattr(module, className)
    
class XMLFunctions(object):
    @staticmethod
    def XMLFromControllers(controllers, path=None):
        """
        Creates an XML file from the given L{Controller<Utilities.Controller.Controller>}s, which
        can be used instantiate the same Controllers later.
        
        @type  controllers:        C{list}
        @param controllers:        List of L{Controller<Utilities.Controller.Controller>}s to translate
                                   to XML.
        
        @type  path:               C{str}
        @param path:               Path where the where file should be written to (should include extension).
                                   If no path is given, the file will not be written to disk.
        
        @rtype:                    C{unicode}
        @return:                   The XML representation of the controllers which is output to file
                                   if a path is given.
        """
        #CAD maybe force a file extension?
        xmlString = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xmlString += '<controllers>\n'
        n = 0
        for controller in controllers:
            xmlString += '<!-- controller ' + n.__str__() + '-->\n'
            xmlString += controller.ToXMLString()
            n += 1
        xmlString += '</controllers>\n'
        xmlString = unicode(xmlString)
        
        if path:
            path = os.path.normpath(os.path.realpath(path))
            outfile = open(path, "w")
            outfile.write(xmlString)
            outfile.close()
            
        return xmlString
    
    @staticmethod
    def XMLFromPanel(panel, path=None):
        """
        Creates an XML file from the given L{Panel<UI.Panel.Panel>}, which
        can be used instantiate the same Panel (and its attached widgets) later.
        
        @type  panel:              L{Panel<UI.Panel.Panel>}
        @param panel:              Panel to translate to XML.
        
        @type  path:               C{str}
        @param path:               Path where the where file should be written to (should include extension).
                                   If no path is given, the file will not be written to disk.
        
        @rtype:                    C{unicode}
        @return:                   The XML representation of the controllers which is output to file
                                   if a path is given.
        """
        xmlString = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xmlString += panel.ToXMLString()
        
        if path:
            path = os.path.normpath(os.path.realpath(path))
            outfile = open(path, "w")
            outfile.write(xmlString)
            outfile.close()
            
        return xmlString