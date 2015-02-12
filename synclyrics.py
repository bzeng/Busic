import re
import pprint
        
class SyncLyrics:
    def __init__(self, rawtext):        
        self.nonactive_color_head = '[color=#008000]'
        self.color_tail = '[/color]'
        
        self.rawtext = rawtext    
        self.reg1 = re.compile('\[\d\d?:\d\d?\.\d\d\]')
        self.reg2 = re.compile('(\[\d\d?:\d\d?\.\d\d\])+')
        self.syncdict = self.parse(self.rawtext)
        self.strippedlrc = self.get_strippedlrc()
        
    def parse(self, rawtext):
        '''
        Some examples:
        ignore for now:
        [ti:light as the breeze]
        [ar:leonard cohen ]
        [al:The Future]
        [offset:43998]
        [01:38.50][02:55.50][04:48.50]so long for your kiss
        '''
        newdict = {}
        lines = rawtext.split('\n')
        for s in lines:
            m = self.reg1.findall(s)
            if m:
                #print (m)
                i = self.reg2.match(s).end()
                #print(s[i:])
                lrc = self.nonactive_color_head + s[i:] + self.color_tail
                for t in m:
                    index1 = t.index(':')
                    index2 = t.index('.')
                    min = int(t[1:index1])
                    sec = int(t[index1+1:index2])
                    milsec = float(t[index2:-1])
                    v = min*60+sec+milsec
                    newdict[v] = lrc        
        
        #pprint.pprint(newdict)
        if newdict == {}:
            print('Not a legitimate .lrc file')
            raise ValueError
        return newdict
        
    def get_strippedlrc(self):
        s = ''
        for key in sorted(self.syncdict):
            s += self.syncdict[key] + '\n'
        return s
    
if __name__ == '__main__':
    teststr = SyncLyrics('[01:38.50][02:55.50][04:48.50]so long for your kiss')
    print(teststr.syncdict)