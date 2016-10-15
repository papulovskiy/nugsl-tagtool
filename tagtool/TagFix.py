#!/usr/bin/python
'''
    This module addresses the irritating problem of applying
    simple regular expressions to balanced environments in
    an XML document.
'''
import re,sys
from exceptions import Exception

class LevelError(Exception):
    pass

class TaggingError(Exception):
    pass

class tagFix:
    def __init__(self, debug=False):
        self.debug = debug
        
    def get_indices(self, target_level):
        '''
            Get a list of the starting indices of tag at the
            specified level.  Result is returned as a list of
            tuples, with 'start' for start or 'end' for end
            as the first element, the nesting level as the
            second element, the starting or ending index, as
            appropriate, as the third.
        '''
        
        iterator = self.get_iterator()
        
        self.indices = []

        if target_level < 1:
            raise LevelError
        elif target_level == 1:
            self.indices.append( ('start', 'cruft', 0) )
        
        level = 0
        for i in iterator:
            #
            # Singleton
            if i.group(1)[-2] == '/':
                ttype = 'start'
                level += 1
                self.handle_index( target_level, ttype, level, i )
                ttype = 'end'
                self.handle_index( target_level, ttype, level, i )
                level += -1
            #
            # End tag of pair
            elif i.group(1)[1] == '/':
                ttype =  'end'
                self.handle_index( target_level, ttype, level, i )
                level += -1
            #
            # Start tag of pair
            else:
                ttype = 'start'
                level += 1
                self.handle_index( target_level, ttype, level, i )
        
        if target_level == 1:
            self.indices.append( ('end', 'cruft', len(self.txt)) )


    def get_iterator(self):
        rextext = '(<%s[^>]*>|</%s>|<%s[^>]*>|</%s>)' \
                       %(self.tag.lower(), self.tag.lower(), \
                       self.tag.upper(), self.tag.upper())
        rex = re.compile( rextext, re.M|re.S)
        return re.finditer(rex, self.txt)
            
    def handle_index(self, target_level, ttype, level, mtch ):
        if ttype == 'start' and level == target_level:
            self.indices.append( ('end', 'cruft', mtch.start()) )
            self.indices.append( ('start', 'inner', mtch.start()) )
        if ttype == 'end' and level == target_level:
            self.indices.append( ('end', 'inner', mtch.end()) )
            self.indices.append( ('start', 'cruft', mtch.end()) )
        if ttype == 'start' and level == target_level - 1:
            self.indices.append( ('start', 'cruft', mtch.end()) )
        if ttype == 'end' and level == target_level - 1:
            self.indices.append( ('end', 'cruft', mtch.start()) )

    def get_maxdepth(self):
        '''
            Get the maximum depth of tag nesting
        '''
        iterator = self.get_iterator()
        maxdepth = 0
        level = 0
        for i in iterator:
            if i.group(1)[1] == '/':
                level += -1
            elif i.group(1)[-2] == '/':
                level += 1
                if maxdepth < level:
                    maxdepth = level
                level += -1
            else:
                level += 1
                if maxdepth < level:
                    maxdepth = level
        return maxdepth

    def donothing(txt):
        return txt
    
    def tagfix(self, tag, txt, 
                 matchfunc=donothing, 
                 nonmatchfunc=donothing, 
                 regex=None, 
                 invert=False,
                 level=None):
        ''' 
        
            When MATCHFUNC is set, invoke the given function once For
	    every balanced tag region identified, using the string
	    within that region as sole argument.  Replace the region
	    with the return value of MATCHFUNC. By default, inner tags
	    are processed first. 
            
            When NONMATCHFUNC is set, regions falling beyond and
	    between the given tag set at top level are processed.
            In this case, the tagging in the text for processing
            may not have balanced tags.
            
            Both modes return the full text of the XML document after
	    processing.
            
        '''
        self.tag = tag
        self.txt = txt
        
        if level:
            levels = [level]
        else:
            levels = range(self.get_maxdepth(), 0, -1)

        if regex and type(regex) != type(re.compile('rex')):
            regex = re.compile(regex, re.M|re.S)

        for level in levels:
            buffer = ''
            txtpos = 0

            self.get_indices( level )
            if not self.indices:
                continue
            
            for blockpos in range(0,len(self.indices),1):
                if self.indices[blockpos][0] == 'end':
                    continue
                # Validate
                if blockpos + 1 > len(self.indices) -1:
                    raise TaggingError
                if self.indices[blockpos + 1][0] != 'end':
                    raise TaggingError
                if self.indices[blockpos][1] != self.indices[blockpos+1][1]:
                    raise TaggingError
                # Get vars
                spos = self.indices[blockpos][2]
                epos = self.indices[blockpos+1][2]
                btype = self.indices[blockpos][1]
                # Stash to buffer
                if txtpos < spos:
                    buffer += self.txt[txtpos:spos]
                if btype == 'cruft':
                    buffer += nonmatchfunc( self.txt[spos:epos] )
                elif btype == 'inner':
                    if regex:
                        if invert:
                            match = re.match( regex, self.txt[spos:epos] )
                        else:
                            match = not re.match( regex, self.txt[spos:epos] )
                    else:
                        match = False
                    if match:
                        buffer += self.txt[spos:epos]
                    else:
                        buffer += matchfunc( self.txt[spos:epos] )
                txtpos = epos

            if buffer:
                buffer += self.txt[epos:]
                self.txt = buffer
                
        return self.txt
