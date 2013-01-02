import random
from functools import partial
from bitstring import BitStream
from utils import *


def transposon(code, *args, **kwargs):
    tsize = int(args[0])
    copypos = random.randint(1, len(code)-tsize)
    transp = code[copypos:copypos+tsize]
    try:
        if kwargs['excise']:
            del code[copypos:copypos+tsize]
    except KeyError: pass
    insertpos = random.randint(1, len(code)-tsize)
    code.insert(transp, insertpos)
    return code

movingtransposon = partial(transposon,
                           excise = True)

def junk(code, *args):
    tsize = int(args[0])
    instream = BitStream(bin='0b'+'0'*tsize)
    insertpos = random.randint(1, len(code)-tsize)
    code.insert(instream,insertpos)
    return code

def delete(code, *args):
    tsize = int(args[0])
    delpos = random.randint(1, len(code)-tsize)
    del code[delpos:delpos+tsize]
    return code

### for now just one point
def twopoint_xover(p1,p2, *args):
    code1 = p1.genotype.code
    code2 = p2.genotype.code
    maxl = min(len(code1),len(code2))
    p = [int(random.random() * maxl)]
    p.append(int(random.random() * maxl))
    p.sort()
    p1,p2 = p
    o1 = BitStream(bin=(code1[:p1]+code2[p1:p2]+code1[p2:]).bin)
    o2 = BitStream(bin=(code2[:p1]+code1[p1:p2]+code2[p2:]).bin)
    return o1, o2

def onepoint_xover(p1,p2,*args):
    code1 = p1.genotype.code
    code2 = p2.genotype.code
    maxl = min(len(code1),len(code2))
    p = int(random.random() * maxl)
    o1 = BitStream(bin=(code1[:p]+code2[p:]).bin)
    o2 = BitStream(bin=(code2[:p]+code1[p:]).bin)
    return o1, o2

def uniform_xover(p1, p2, *args):
    code1 = p1.genotype.code
    code2 = p2.genotype.code
    l = min(len(code1),len(code2))
    mask = reduce(lambda x,y: "%s%s"%(x,y),
                 [int(round(random.random()))
                  for i in range(l)])
    bitmask = BitStream(bin=mask)
    print bitmask.bin
    o1,o2 = '',''
    for i in range(len(bitmask.bin)):
        if bitmask[i]:
            o1 += code1.bin[i]
            o2 += code2.bin[i]
        else:
            o1 += code2.bin[i]
            o2 += code1.bin[i]
    return (BitStream(bin = o1), BitStream(bin = o2))

if __name__ == '__main__':
    a = BitStream('0b' + '00011100011100011100')
    print a.bin
    transposon(a, 5)
    print a.bin
    junk(a, 5)
    print a.bin
    delete(a, 15)
    print a.bin

    a = BitStream('0b' + '1'*10)
    b = BitStream('0b' + '0'*20)
    c,d = twopoint_xover(a,b)
    print c.bin
    print d.bin

    a = BitStream('0b' + '1'*10)
    b = BitStream('0b' + '0'*20)
    e,f = uniform_xover(a,b)
    print e.bin
    print f.bin
