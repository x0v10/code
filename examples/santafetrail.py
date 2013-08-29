import sys
from code.operators import *
from code.evodevo import Problem,EvoDevoWorkbench
from code.rencode import *
from gp_ant import *
from code.utils.config import *

class SantaFeTrail(ReNCoDeProb):
        labels = {'ant.move_forward':'M',
                  'ant.if_food_ahead':'IFA',
                  'progN':'progn',
                  'ant.turn_left':'L',
                  'ant.turn_right':'R',
                  'dummy':'dummy'}
        funs = ['ant.if_food_ahead', 'progN']
        terms = ['ant.move_forward','ant.turn_left','ant.turn_right']

        #def __init__(self, evaluate):
        #	ReNCoDeProb.__init__(self,evaluate)


def evaluateant(agent, **kwargs):
        agent.funskel = mergefun
        if len(agent) < 3:
                return 90
        routine = agent()
        log.debug(routine)
        #if len(routine) < 5000:
        ant.runstring(routine,True)
        #else:
         #       return 100
        return 89 - ant.eaten


if __name__ == '__main__':
        p = SantaFeTrail(evaluateant)
        cfg = loadconfig(parsecmd())
        edw = EvoDevoWorkbench(cfg,p)
        edw.run()
