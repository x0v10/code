import ConfigParser, os
import logging
import random
import numpy as np
from numpy import array as nparray
from functools import partial
from bitstring import *
from math import exp
import sys
from sys import stdout
from subprocess import call
from utils import *
from utils.bitstrutils import *

try:
    import matplotlib.pyplot as plt
    from matplotlib import collections, legend
except ImportError:
    logging.warning('matplotlib not found.')
    logging.warning('use of silentmode = 0 will result in an error...')

log = logging.getLogger(__name__)


def bindparams(config,fun):
    '''Binds the ARN configuration file parameters to a function.'''
    return partial(fun,
                   bindingsize = config.getint('default','bindingsize'),
                   proteinsize = config.getint('default','proteinsize'),
                   genesize = config.getint('default','genesize'),
                   promoter = config.get('default','promoter'),
                   excite_offset = config.getint('default','excite_offset'),
                   match_threshold = config.getint('default','match_threshold'),
                   beta = config.getfloat('default','beta'),
                   delta = config.getfloat('default','delta'),
                   samplerate = config.getfloat('default','samplerate'),
                   simtime = config.getint('default','simtime'),
                   simstep = config.getint('default','simstep'),
                   silentmode = config.getboolean('default','silentmode'),
                   initdm = config.getint('default','initdm'),
                   mutratedm = config.getfloat('default','mutratedm'),
                   overlapgenes = config.getboolean('default','overlapgenes'))

def neutralshare(arnet):
    try:
        proms = arnet.promlist + arnet.effectorproms
    except:
        proms = arnet.promlist

    neutrals = proms[0] - 88
    for i in range(0, len(proms),2):
        if proms[i] == proms[-1]:
            break
        if proms[i] + 168 < proms[i+1] - 88:
            neutrals += (proms[i+1] - 88) - (proms[i] + 168)
    neutrals += len(arnet.code) - (proms[-1]+168)
    return float(neutrals) / len(arnet.code)

def generatechromo(initdm, mutratedm, genesize, promoter,
                   excite_offset, overlapgenes,**bindargs):
    '''
    Default function to generate an ARN chromosome.
    To be used with bindparams.
    '''
    log.debug('Creating DM agent.')
    valid = False
    while True:
        genome = bitarray(getrndstr(32))
        for i in range(0,initdm):
            genome = dm_event(genome, mutratedm)
        if genome.search(bitarray(promoter)):
            break
    return genome

def generatechromo_rnd( genomesize, mutratedm, genesize, promoter,
                        excite_offset, overlapgenes, **bindargs):
    '''
    Default function to generate an ARN chromosome.
    To be used with bindparams.
    '''
    log.debug('Creating random agent.')
    valid = False
    genome = bitarray(getrndstr(genomesize))
    while not genome.search(bitarray(promoter)):
        genome = bitarray(getrndstr(genomesize))
    return genome

def displayARNresults(proteins, ccs, step=1):
    log.warning('Plotting simulation results for ' +
                str(len(proteins)) + ' genes/proteins')
    plt.clf()
    xx=[i*step for i in range(len(ccs[0]))]
    for i in range(len(proteins)):
        plt.plot(xx, ccs[i],label="%i"%(proteins[i][0],))

    plt.legend()
    plt.savefig('ccoutput.png')
    call(["open", "ccoutput.png"])
    return "ARN simulation displayed"

def buildpromlist(genome, excite_offset, genesize, promoter,
                  overlapgenes, **kwargs):
    gene_index = genome.search(bitarray(promoter))
    promsize = len(promoter)
    promlist = filter( lambda index:
                       int(excite_offset) <= index <  (genome.length()-(int(genesize)+promsize )),
                       gene_index)
    genegap = 32 + genesize + 64
    if overlapgenes:
            #promotor size only
            genegap = 32
    proms = reduce(lambda indxlst, indx:
                   indxlst + [indx] if indx-indxlst[-1] >= genegap else indxlst,
                   promlist[1:],
                   promlist[:1])
    return proms

def buildproducts(genome, promlist, excite_offset, promoter,
                  genesize, bindingsize, proteinsize, **kwargs):
     log.debug("Building ARN with " + str(len(promlist)) + " genes")
    #each protein is
    #[protein_index(=prom_index), e-bind, h-bind,
    # bind-signature, function-signature ]
     proteins = list()
     for pidx in promlist:
         proteins.append(_getprotein(pidx,
                                     bitarray(genome[pidx-excite_offset:pidx+genesize+len(promoter)]),
                                     bindingsize,
                                     genesize,
                                     proteinsize))
     return proteins


#organized in columns for the target equation
def getbindings(bindtype, proteins, match_threshold,**kwargs):
    return nparray([[XORmatching(p[3],otherps[1+bindtype],match_threshold)
                         for otherps in proteins]
                        for p in proteins],dtype=float);

def iterate(arnet,samplerate, simtime, silentmode, simstep,delta,**kwargs):
    time = 1
    while time <= simtime:
        _update(arnet.proteins,arnet.ccs,arnet.eweights,
                arnet.iweights,delta)
        if(not(silentmode) and
           (time % (simtime*samplerate) == 0)):
            log.debug('TIME: '+ str(time))
            for p in proteins:
                arnet.updatehistory()
        time+=simstep

    if not silentmode:
        displayARNresults(proteins, cchistory,simstep)

    return arnet.ccs


def _update(proteins, ccs, exciteweights, inhibitweights,delta):
    deltas = (_getSignalArray(ccs,exciteweights) -
              _getSignalArray(ccs,inhibitweights))
    deltas *= delta
    deltas *= ccs
    total = sum(ccs)+sum(deltas)
    ccs+=deltas
    ccs/=total

def _updatenonorm(proteins, ccs, exciteweights, inhibitweights,delta):
        deltas = (_getSignalArray(ccs,exciteweights) -
                  _getSignalArray(ccs,inhibitweights))
        deltas *= delta
        deltas *= ccs
        ccs+=deltas

def _getSignalArray(ccs, weightstable):
    return 1.0/len(ccs) * np.dot(ccs,weightstable)

def _getprotein(idx, code, bind_size, gene_size, protein_size):
    signature = bitarray(applymajority(code[bind_size*3:bind_size*3+gene_size],
                              protein_size))
    #EXTENDED version - Weak linkage (needs double size gene/proteins)
    #p = [code[:self.bind_size],
     #       code[self.bind_size:self.bind_size*2],
      #      signature[0:self.bind_size],
       #     signature[self.bind_size:self.protein_size]]
    #ORIGINAL version
    p = [idx,
         code[:bind_size],
         code[bind_size:bind_size*2],
         signature,
         signature]
    log.debug(p)
    return p

def _getweights(bindings, bindingsize, beta, **kwargs):
    weights = bindings - bindingsize
    weights *= beta
    return np.exp(weights)


class ARNetwork:
    def __init__(self, gcode, config, **kwargs):
        self.code = gcode
        self.simtime = config.getint('default','simtime')

        promfun = bindparams(config, buildpromlist)
        productsfun = bindparams(config, buildproducts)
        self.promlist = promfun(gcode)
        self.proteins = productsfun( gcode, self.promlist)
        self.excite_offset = config.getint('default','excite_offset')
        pbindfun = bindparams(config, getbindings)
        weightsfun = bindparams(config, _getweights)
        nump = len(self.proteins)
        self.ccs = []
        if self.promlist:
            self.ccs=nparray([1.0/nump]*nump)
            for i in range(len(self.proteins)):
                self.proteins[i].append(self.ccs[i])
            self._initializehistory()
            self._initializebindings(pbindfun)
            self._initializeweights(weightsfun)
        self.simfun = bindparams(config,iterate)
        self.delta = config.getfloat('default','delta')
        self.numtf = len(self.proteins)

    def _initializebindings(self, pbindfun):
        self.ebindings = pbindfun(0, self.proteins)
        self.ibindings = pbindfun(1, self.proteins)

    def _initializeweights(self, weightsfun):
        self.eweights = weightsfun(self.ebindings)
        self.iweights = weightsfun(self.ibindings)

    def _initializehistory(self):
        self.cchistory=nparray(self.ccs)

    def updatehistory(self):
        self.cchistory = np.column_stack((self.cchistory,
                                          self.ccs))

    def __str__(self):
        return str(self.proteins)

    def simulate(self):
        if self.simtime > 0:
            self.simfun(self)
            for i in range(len(self.proteins)):
                self.proteins[i][-1] = self.ccs[i]

    def stepsimulate(self, proteins, ccs):
         _updatenonorm(proteins, ccs, self.eweights, self.iweights, self.delta)
         return ccs

    def nstepsim(self, n = 1000):
        self.simfun(self.proteins, self.ccs,
                    self.eweights, self.iweights,simtime=n)
        for i in range(len(self.proteins)):
            self.proteins[i][-1] = self.ccs[i]

    def getneutralshare(self):
        return neutralshare(self)

    def snapshot(self):
        s = 'digraph best {\nordering = out;\n'
        shape = 'hexagon'
        labelidx = 0

        for tf in self.promlist:
            s += '%i [label="%s"];\n' % (tf, labelidx )
            for e,h,i in zip(self.ebindings[:,labelidx],
                             self.ibindings[:,labelidx],
                             range(len(self.ebindings))):
                if e > 0:
                    s += '%i -> %i [dir=back];\n' % \
                             (tf, self.promlist[i])
                if h > 0:
                    s += '%i -> %i [dir=back,style=dotted];\n' % \
                             (tf, self.promlist[i])
            labelidx += 1
        s += '}'
        return s

###########################################################################
### Test                                                                ###
###########################################################################

if __name__ == '__main__':
        arnconfigfile = '../configfiles/arnsim.cfg'
        log.setLevel(logging.DEBUG)
        cfg = ConfigParser.ConfigParser()
        cfg.readfp(open(arnconfigfile))
        proteins=[]
        nump = 0
        try:
                f = open(sys.argv[1], 'r')
                genome = BitStream(bin=f.readline())
                arnet = ARNetwork(genome, cfg)
        except:
                while nump < 4 or nump > 12:
                        genome = BitStream(float=random.random(), length=32)
                        for i in range(cfg.getint('default','initdm')):
                                genome = dm_event(genome,
                                                  .02)

                        arnet = ARNetwork(genome, cfg)
                        nump = len(arnet.promlist)

        for p in arnet.proteins: print p
        f = open('genome.save','w')
        f.write(genome.bin)
        f.close
        #print genome.bin
        arnet.simulate()



###########################################################################
### Other Helpers                                                       ###
###########################################################################
#deprecated

def generatechromoepi(init_dm, dm_mutrate,**bindargs):
    valid = False
    #initdm = random.gauss(float(init_dm),1.0)
    while not 30 > valid >= 4:
        genome = BitStream(float=random.random(),length=32);
        for i in range(0,int(init_dm)):
            genome = dm_event(genome, dm_mutrate)
        promlist = buildpromlist(genome, bindargs['excite_offset'],
                                 bindargs['genesize'], bindargs['promoter'])
        valid = len(promlist)

    proteins = buildproducts(genome, promlist,
                             bindargs['excite_offset'],
                             len(bindargs['promoter']),
                             bindargs['genesize'],
                             bindargs['bindingsize'],
                             bindargs['proteinsize'])
    cromatines = [1.0/float(valid)]*valid
    return (genome,dict(zip(promlist,proteins)),
            dict(zip(promlist,cromatines)),10000,0)

#deprecated
def buildpromlistEPI(genome, excite_offset, genesize, promoter):
    gene_index = genome.findall(promoter)
    promsize = len(promoter)
    promlist = filter( lambda index:
                       excite_offset <= index <  (genome.length-(genesize+promsize )),
                       gene_index)
    proms = reduce(lambda indxlst, indx:
                   indxlst + [indx] if(indx-indxlst[-1] >= genesize+3*32) else indxlst,
                   promlist,
                   [0])
    return proms[1:]
