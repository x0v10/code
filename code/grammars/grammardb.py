
_base_grammar = { 'exp': [['exp', 'op','exp'],
                          ['(','exp',')'],
                          ['coef'],
                          ['var']],
                  'op': [['+'],
                         ['-'],
                         ['*'],
                         ['/']],
                  'coef': [['1.0']],
                  'var': [['inp']]}

_base_grammar_alt = { 'expr': [['expr', 'op','expr'],
                               ['(','expr', 'op','expr', ')'],
                               ['pre-op','(','expr',')'],
                               ['var']],
                      'op': [['+'],
                             ['-'],
                             ['*'],
                             ['/']],
                      'pre-op': [['sin'],
                                 ['cos'],
                                 ['tan'],
                                 ['log']],
                      'var': [['inp']]}


_fixed_grammar = { 'expr': [['var', 'expr2'],
                            ['(','var','expr2', ')'],
                            ['pre-op','(','var','expr2',')']],
                   'expr2': [['op', 'var', 'expr2'],
                             ['op', 'var', 'expr2'],
                             ['op', 'var', 'expr2'],
                             ['']],
                   'op': [['+'],
                          ['-'],
                          ['*'],
                          ['|div|']],
                   'pre-op': [['sin_'],
                              ['cos_'],
                              ['exp_'],
                              ['log_']],
                   'var': [['inputs[0]'],
                           ['1.0']]}

_fixed_grammar_b = { 'expr': [['var', 'expr2'],
                              ['(','var','expr2', ')']],
                     'expr2': [['op', 'var', 'expr2'],
                               ['op', 'var']],
                     'op': [['+'],
                            ['-'],
                            ['*'],
                            ['|div|']],
                     'var': [['inputs[0]'],
                             ['1.0']]}

ant_grammar = { 'code': [['line'],
                         ['line','code']],
                'line': [['op'],
                         ['condition']],
                'line2': [['op','line2'],
                          ['condition','line2'],
                          ['op','']],
                'condition': [['if ant.sense_food():\n{\n','line2', '\n}\nelse:\n{\n' , 'line2','\n}\n']],
                'op': [['ant.turn_left;\n'],
                       ['ant.turn_right;\n'],
                       ['ant.move_forward;\n']]}
