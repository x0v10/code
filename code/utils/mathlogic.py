from math import log,exp,tan,tanh,sqrt,cos,sin,cosh,sinh
import operator

#### MATH ###
def add_(*args):
    return reduce(lambda x,y: operator.add(x,y), args)

def sub_(*args):
    return reduce(lambda x,y: operator.sub(x,y), args)

def mul_(*args):
    return reduce(lambda x,y: operator.mul(x,y), args)

def div_(*args):
    return reduce(lambda x,y: div__(x,y), args)

#def add__(x1 = 1.0, x2 = 0):
#    return operator.add(x1,x2)

#def sub__(x1 = 1.0, x2 = 0):
#    return operator.sub(x1,x2)

#def mul__(x1 = 1, x2 = 1):
#    return operator.mul(x1,x2)

def div__(x = 1, y = 1):
    if(y==0): return 1.0
    try:
        return float(x) / y
    except OverflowError:
        return 1.0

def tanh_(*args):
    inp = sum(args)
    return tanh(inp)

def tan_(*args):
    try:
        inp = sum(args)
        return tan(inp)
    except ValueError:
        return 1.0

def sin_(*args):
    try:
        inp = sum(args)
        return sin(inp)
    except ValueError:
        return 1.0

def cos_(*args):
    try:
        inp = sum(args)
        return cos(inp)
    except ValueError:
        return 1.0

def sinh_(*args):
    try:
        inp = sum(args)
        return sinh(inp)
    except OverflowError:
        return 1.0

def cosh_(*args):
    try:
        inp = sum(args)
        return cosh(inp)
    except OverflowError:
        return 1.0

def log_(*args):
    x = sum(args)#/float(len(args))
    if x <= 0: return 1e6
    return log(x)

def exp_(*args):
    x= sum(args)
    try:
        return exp(x)
    except:
        return 1e6

def sqrt_(*args):
    x = sum(args)
    try:
            return sqrt(x)
    except:
        return 1e6

def max_(*inputs):
    return max(inputs)

def min_(*inputs):
    return min(inputs)

def sigmoid(x):
    try:
        return 1.0 / (1.0 + exp(-x))
    except OverflowError:
        return 1e6

def reciprocalsum(*args):
        sum = 0
        for a in args:
            if a == 0:
                a = 1e6
            sum += (1.0/a)
        return sum

#For creativity, centered u=0, with a = 1, sigma=.2
def gaussian(*args):
    if len(args) > 1:
        x = sum(args)
    else:
        x = args[0]
    try:
        return exp(-(pow(x,2)/(2.0*pow(.2,2))))
    except OverflowError:
        return 1.0

def identity(*args):
    if len(args) > 1:
        x = sum(args)
    else:
        x = args[0]
    return x

def symmetric(*args):
    if len(args) > 1:
        x = sum(args)
    else:
        x = args[0]
    return (1.0 - x) if x > 0 else (1.0 + x)

### LOGIC ###
#def nand(*args):
#    return reduce(lambda x,y: not(x and y), args)

#def and_(*args):
#    return reduce(lambda x,y: x and y, args)
    #print r, args


#def or_(*args):
#    return reduce(lambda x,y: x or y, args)
    #print r,args

#d#ef nor(*args):
#    return reduce(lambda x,y: not(x or y), args)

def iand(in1, in2 = True):
    return (not in1) and in2

def xor(in1, in2 = False):
    if in1 == in2:
        return 0
    else: return 1

def nand(in1, in2 = True):
    result = not(and_(in1, in2))
    #print 'in1=', in1, ' in2=',in2, ' r=',result
    return result

def nor(in1, in2 = False):
    result = not(or_(in1, in2))
    #print 'in1=', in1, ' in2=',in2, ' r=',result
    return result

def and_(in1, in2 = True):
    result = (int(in1) and int(in2))
    #print 'in1=', in1, ' in2=',in2, ' r=',result
    return result

def or_(in1, in2 = False):
    result = (int(in1) or int(in2))
    #print 'in1=', in1, ' in2=',in2, ' r=',result
    return result

def if_(*args):
    if len(args) == 1:
        return args[0]
    elif len(args) == 2:
        if args[0]:
            return args[1]
        else:
            return not args[1]
    else:
        if args[0]:
            return args[1]
        else:
            return args[2]

### CLASSIFICATION ###

def mcc(tp, tn, fp, fn):
    '''Matthews Correlation Coefficient'''
    den = sqrt((tp + fp)*(tp + fn)*(tn + fp)*(tn + fn))
    if not den:
        den = 1
    return (tp * tn - fp * fn) / den

def fmeasure(tp, fp, fn):
    precision = tp / float(tp + fp)
    recall = tp / float(tp + fn)
    return 2 * precision * recall / (precision + recall)


#FROM http://code.activestate.com/recipes/384122-infix-operators/
# definition of an Infix operator class
# this recipe also works in jython
# calling sequence for the infix is either:
#  x |op| y
# or:
# x <<op>> y
class Infix:
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, value1, value2):
        return self.function(value1, value2)

#this was used with grammars to evaluate expressions
div = Infix(div_)

if __name__=='__main__':
    print 8 |_div_| 2
    print 9.0 |_div_| 2
    print 8 |_div_| 0
    print 8 / 0
