import ply.lex as lex
import ply.yacc as yacc
import math
import random
from rollhistory import rollhistory

fudgehigh = 0
fudgelow = 0
fudgemiddle = 0

def rollDie(n):
	global fudgehigh
	global fudgelow
	global fudgemiddle
	if n > 0:
		if fudgehigh > 0:
			fudgeamount = int(n*0.25)

			if fudgeamount < 2:
				fudgeamount = 2
			fudgehigh -= 1

			return (n-fudgeamount) + random.randrange(1,fudgeamount+1)
		if fudgelow > 0:
			fudgeamount = int(n*0.25)

			if fudgeamount < 2:
				fudgeamount = 2
			fudgelow -= 1

			return random.randrange(1,fudgeamount+1)
		if fudgemiddle > 0:
			fudgeamount = int(n*0.25)

			if fudgeamount < 2:
				fudgeamount = 2
			fudgemiddle -= 1

			return (n-fudgeamount)//2 + random.randrange(1,fudgeamount+1)

		return random.randrange(1,n+1)
	else:
		return -random.randrange(1,(-n)+1)

def rollDice(quantity, size):
	if size == 1:
		return quantity
	if size == 0 or quantity == 0:
		return 0
	if size < 0:
		return list(map(lambda x: -x, rollDice(quantity, -size)))
	if quantity < 0:
		return list(map(lambda x: -x, rollDice(-quantity, size)))
	if quantity > 10000:
		raise Exception("Why on earth do you need that many dice")

	return [rollDie(size) for x in range(quantity)]

def killFudge():
	fudgelow = 0
	fudgemiddle = 0
	fudgehigh = 0

tokens = ('NUMBER', 'LPAREN', 'RPAREN', 'ROLL', 'COMPARISON')

literals = "+-*/^c!"
t_ROLL = r'd+'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_COMPARISON(t):
	r'<=|>=|==|<|>|=|[bB][eE][aA][tT][sS]'
	if t.value == '<':
		t.value = lambda x,y: x<y
	if t.value == '<=':
		t.value = lambda x,y: x<=y
	if t.value == '>':
		t.value = lambda x,y: x>y
	if t.value == '=' or t.value == '==':
		t.value = lambda x,y: x==y
	else:
		t.value = lambda x,y: x>=y

	return t

def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t

t_ignore = ' '

def t_error(t):
	t.value = 'Illegal character \'' + t.value[0] + '\''
	t.lexer.skip(1)
	return t

lexer = lex.lex()

precedence = (
		('left', '+', '-'),
		('left', '*', '/'),
		('left', '^', '!'),
		('right', 'ROLL'),
		('right', 'UMINUS')
	)

def p_expr(p):
	'''expr : NUMBER'''
	p[0] = rollhistory(int(p[1]), [])

def p_expr_c(p):
	'''expr : 'c' '''
	p[0] = [299792458, []]

def p_expr_arithmetic(p):
	'''expr : expr '+' expr
			| expr '-' expr
			| expr '*' expr
			| expr '/' expr
			| expr '^' expr'''
	if p[2] == '+':
		p[0] = p[1] + p[3]
	elif p[2] == '-':
		p[0] = p[1] - p[3]
	elif p[2] == '*':
		p[0] = p[1] * p[3]
	elif p[2] == '/':
		p[0] = p[1] // p[3]
	elif p[2] == '^':
		p[0] = p[1] ** p[3]

def p_expr_dice(p):
	'''expr : expr ROLL expr'''
	val = rollDice(p[1].val, p[3].val)
	tmp = ""
	if math.fabs(p[1].val) > 1:
		tmp = "Rolling {0}d{1}s: {2} ({3})".format(p[1].val, p[3].val, sum(val), str(val)[1:-1])
	else:
		tmp = "Rolling 1d{0}: {1}".format(p[3].val, sum(val))
	p[0] = rollhistory(sum(val), p[3].history + p[1].history + [tmp])

def p_expr_onedie(p):
	'''expr : ROLL expr'''
	val = rollDie(p[2].val)
	tmp = "Rolling 1d{0}: {1}".format(p[2].val, val)
	p[0] = rollhistory(val, p[2].history + [tmp])

def p_expr_comparison(p):
	'''expr : expr COMPARISON expr'''
	x = p[1]
	comparison = p[2]
	y = p[3]
	if comparison(x,y):
		tmp = "{0} beats {1}".format(x,y)
		p[0] = rollhistory(1, p[1].history + p[3].history + [tmp])
	else:
		tmp = "{0} was beat by {1}".format(x,y)
		p[1] = rollhistory(0, p[1].history + p[3].history + [tmp])

def p_expr_paren(p):
	'''expr : LPAREN expr RPAREN'''
	p[0] = p[2]

def p_expr_fact(p):
	'''expr : expr '!' '''
	p[0] = p[1].factorial()

def p_expr_minus(p):
	'''expr : '-' expr %prec UMINUS'''
	p[0] = -p[2]

def p_error(p):
	'''expr : error'''
	raise Exception("Error in parsing")

parser = yacc.yacc()

def parse(x):
	return parser.parse(x)

if __name__ == '__main__':
	while True:
		s = input()
		if s == '#': break
		print(parse(s))