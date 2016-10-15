'''
    Module
'''

import unittest
from tagtool import tagFix
from tagtool.TagFix import TaggingError
import re

class TestTagFix(unittest.TestCase):

    def setUp(self):
        self.tagFix = tagFix()
    
    def testNoop(self):
        txt = '<x></x>'
        res = self.tagFix.tagfix('y',txt)
        self.assertEqual(txt,res)
        
    def UPPER(self, txt):
        return txt.upper()
    
    def testTaggingError(self):
        txt = '<x>'
        try:
            res = self.tagFix.tagfix('x',txt)
        except TaggingError:
            res = 'fail'
        self.assertEqual(res,'fail')
        
    def testSingleton(self):
        txt = 'a <x b /> c'
        res = self.tagFix.tagfix('x',txt,matchfunc=self.UPPER)
        expected = 'a <X B /> c'
        self.assertEqual(res,expected)
    
    def testPairMatch(self):
        txt = 'a <path> b </path> c'
        res = self.tagFix.tagfix('path',txt,matchfunc=self.UPPER)
        expected = 'a <PATH> B </PATH> c'
        self.assertEqual(res,expected)

    def testPairNonmatch(self):
        txt = 'a <x> b </x> c'
        res = self.tagFix.tagfix('x',txt,nonmatchfunc=self.UPPER)
        expected = 'A <x> b </x> C'
        self.assertEqual(res,expected)
    
    def testInnerLevelMatch(self):
        txt = 'a0 <x> b1 <x> c2 </x> d1 <x> e2 <x> f3 </x> g2 </x> h1 </x> i0'
        res = self.tagFix.tagfix('x',txt, matchfunc=self.UPPER,level=3)
        expected = 'a0 <x> b1 <x> c2 </x> d1 <x> e2 <X> F3 </X> g2 </x> h1 </x> i0'
        self.assertEqual(res,expected)
        
    def testInnerLevelNonmatch(self):
        txt = 'a0 <x> b1 <x> careful! </x> d1 <x> e2 <x> f3 </x> g2 </x> h1 </x> i0'
        res = self.tagFix.tagfix('x',txt, nonmatchfunc=self.UPPER,level=3)
        expected = 'a0 <x> b1 <x> CAREFUL! </x> d1 <x> E2 <x> f3 </x> G2 </x> h1 </x> i0'
        self.assertEqual(res,expected)
        
    def testTopLevelMatch(self):
        txt = 'a0 <x> b1 <x> c2 </x> d1 </x> e0'
        res = self.tagFix.tagfix('x',txt, matchfunc=self.UPPER,level=1)
        expected = 'a0 <X> B1 <X> C2 </X> D1 </X> e0'
        self.assertEqual(res,expected)
        
    def testTopLevelNonmatch(self):
        txt = 'a0 <x> b1 <x> c2 </x> d1 </x> e0'
        res = self.tagFix.tagfix('x',txt, nonmatchfunc=self.UPPER,level=1)
        expected = 'A0 <x> b1 <x> c2 </x> d1 </x> E0'
        self.assertEqual(res,expected)
        
    def ADD(self, txt):
        return re.sub('([0-9]+)', self._ADD ,txt)
        
    def _ADD(self, matchobj):
        return str( int( matchobj.group(1) ) + 1 )
        
    def testRecursiveNesting(self):
        txt = '<x>1<x>1</x></x>'
        res = self.tagFix.tagfix('x', txt, matchfunc=self.ADD)
        expected = '<x>2<x>3</x></x>'
        self.assertEqual(res,expected)
        
    def testRegexSucceed(self):
        txt = '<x> a </x><x id="makeupper"> b </x>'
        regex = '.*id="makeupper".*'
        res = self.tagFix.tagfix('x', txt, matchfunc=self.UPPER, regex=regex)
        expected = '<x> a </x><X ID="MAKEUPPER"> B </X>'
        self.assertEqual(res,expected)
        
    def testRegexFail(self):
        txt = '<x> a </x><x id="makeupper"> b </x>'
        regex = '.*id="makeupperx".*'
        res = self.tagFix.tagfix('x', txt, matchfunc=self.UPPER, regex=regex)
        expected = '<x> a </x><x id="makeupper"> b </x>'
        self.assertEqual(res,expected)
        
    def testRegexMultiline(self):
        txt = '''
<x>
  <x> a </x>
  <path
     id="makeupper"
  /> b
</x>
'''
        regex = '.*id="makeupper".*'
        res = self.tagFix.tagfix('path', txt, matchfunc=self.UPPER, regex=regex)
        expected = '''
<x>
  <x> a </x>
  <PATH
     ID="MAKEUPPER"
  /> b
</x>
'''
        self.assertEqual(res,expected)
        
class TestGetMaxdepth(unittest.TestCase):
    
    def setUp(self):
        self.tagFix = tagFix()
        
    def testGetMaxDepth0(self):
        self.tagFix.txt = '''<x></x>'''
        self.tagFix.tag = 'x'
        maxdepth = self.tagFix.get_maxdepth()
        self.assertEqual(maxdepth, 1)
        
    def testGetMaxDepth3(self):
        self.tagFix.txt = '''<x><x></x><x><x></x></x></x>'''
        self.tagFix.tag = 'x'
        maxdepth = self.tagFix.get_maxdepth()
        self.assertEqual(maxdepth, 3)
        

class TestGetIndices(unittest.TestCase):

    def setUp(self):
        self.tagFix = tagFix()
        self.tagFix.txt = '''A23456789
<x>B234567890</x>
C2345678
<y>D234567890<y>E234567890</y>F234567890</y>
G23456789'''
        
    def testIndicesLevelOne(self):
        self.tagFix.tag = 'x'
        self.tagFix.get_indices( 1 )
        expect = []
        expect.append( ('start', 'cruft', 0) )
        expect.append( ('end', 'cruft', 10) )
        expect.append( ('start', 'inner', 10) )
        expect.append( ('end', 'inner', 27) )
        expect.append( ('start', 'cruft', 27) )
        expect.append( ('end', 'cruft', 91) )
        self.assertEqual(self.tagFix.indices, expect)        

    def testIndicesLevelTwo(self):
        self.tagFix.tag = 'y'
        self.tagFix.get_indices( 2 )
        expect = []
        expect.append( ('start', 'cruft', 40) )
        expect.append( ('end', 'cruft', 50) )
        expect.append( ('start', 'inner', 50) )
        expect.append( ('end', 'inner', 67) )
        expect.append( ('start', 'cruft', 67) )
        expect.append( ('end', 'cruft', 77) )
        self.assertEqual(self.tagFix.indices, expect)        

if __name__ == "__main__":
    unittest.main()
