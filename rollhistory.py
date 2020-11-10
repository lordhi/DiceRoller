def fact(n):
	val = 1
	for i in range(1,n+1):
		val *= i
	return val

class rollhistory:
	def __init__(self,val,history):
		self.val = val
		self.history = history

	def __add__(self,c):
		newval = self.val + c.val
		historyEntry = "{0}+{1}={2}".format(self.val, c.val, newval)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __sub__(self,c):
		newval = self.val - c.val
		historyEntry = "{0}-{1}={2}".format(self.val, c.val, newval)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __mul__(self, c):
		newval = self.val * c.val
		historyEntry = "{0}*{1}={2}".format(self.val, c.val, newval)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __floordiv__(self, c):
		newval = self.val // c.val
		historyEntry = "{0}/{1}={2}".format(self.val, c.val, newval)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __pow__(self, c):
		newval = int(self.val**c.val)
		historyEntry = "{0}^{1}={2}".format(self.val,c.val, newval)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __neg__(self):
		return rollhistory(-self.val, self.history)

	def __eq__(self, c):
		newval = 1 if self.val == c.val else 0
		if newval:
			historyEntry = "{0} is equal to {1}".format(self.val, c.val)
		else:
			historyEntry = "{0} is not equal to {1}".format(self.val, c.val)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __ne__(self, c):
		newval = 1 if self.val != c.val else 0
		if newval:
			historyEntry = "{0} is not equal to {1}".format(self.val, c.val)
		else:
			historyEntry = "{0} is equal to {1}".format(self.val, c.val)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __lt__(self, c):
		newval = 1 if self.val < c.val else 0
		if newval:
			historyEntry = "{0} is less than {1}".format(self.val, c.val)
		else:
			historyEntry = "{0} is not less than {1}".format(self.val, c.val)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __le__(self, c):
		newval = 1 if self.val <= c.val else 0
		if newval:
			historyEntry = "{0} is less than or equal to {1}".format(self.val, c.val)
		else:
			historyEntry = "{0} is not less than nor equal to {1}".format(self.val, c.val)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __gt__(self, c):
		newval = 1 if self.val > c.val else 0
		if newval:
			historyEntry = "{0} is greater than {1}".format(self.val, c.val)
		else:
			historyEntry = "{0} is not greater than {1}".format(self.val, c.val)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def __ge__(self, c):
		newval = 1 if self.val >= c.val else 0
		if newval:
			historyEntry = "{0} is greater than or equal to {1}".format(self.val, c.val)
		else:
			historyEntry = "{0} is not greater than nor equal to {1}".format(self.val, c.val)
		return rollhistory(newval, self.history + c.history + [historyEntry])

	def factorial(self):
		newval = fact(self.val)
		return rollhistory(newval, self.history + ["{0}!={1}".format(self.val, newval)])

	def __str__(self):
		msg = self.str_not_end()
		if len(self.history) > 1:
			msg += "Total: {0}\r\n".format(self.val)
		return msg + "--------------------\r\n"

	def str_not_end(self):
		msg = ""
		if len(self.history) > 0:
			for i in self.history:
				msg += i + "\r\n"
		return msg