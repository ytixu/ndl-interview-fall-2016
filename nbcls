# String parsing helper functions

def char_filter(strr):
	return strr.replace(", ", " ").replace("'s ", " s ")

def tokenize(strr):
	return char_filter(strr.lower()).split()

def question_analyse(strr):
	return tokenize(strr.strip("'"))

def answer_analyse(strr):
	return tokenize(strr)

WITHOUT_ANSWER = 0
WITH_ANSWER = 1
WITH_ANSWER_SEPERATED = 2

class NaiveBayesClassifier:

	def __init__(self, training_path, validating_path, mode=WITHOUT_ANSWER):
		self.classes = {}
		self.classes_count = 0
		self.question_terms = {}
		self.question_terms_count = {}
		self.answer_terms = {}
		self.answer_terms_count = {}

		self.train(training_path, mode)

		self.result = {}

		# self.validate(validating_path, mode)

	def _count(self, tokens, prop_name, class_name = None):
		count_prop_name = prop_name+'_count'

		prop = self.__dict__[prop_name]
		prop_count = self.__dict__[count_prop_name]

		if class_name:
			if not class_name in self.__dict__[prop_name]:
				self.__dict__[prop_name][class_name] = {}
				self.__dict__[count_prop_name][class_name] = 0

			prop = self.__dict__[prop_name][class_name]
			prop_count = self.__dict__[count_prop_name][class_name]

		for token in tokens:
			if token in prop:
				prop[token] += 1
			else:
				prop[token] = 1

			prop_count += 1

		if class_name:
			self.__dict__[prop_name][class_name] = prop
			self.__dict__[count_prop_name][class_name] = prop_count
		else:
			self.__dict__[prop_name] = prop
			self.__dict__[count_prop_name] = prop_count


	def _get_tokens(self, data, mode):
		question_tokens = question_analyse(data["question"])
		answer_tokens = None

		if (mode == WITH_ANSWER):
			question_tokens += answer_analyse(data["answer"])

		if (mode == WITH_ANSWER_SEPERATED):
			answer_tokens = answer_analyse(data["answer"])

		return (question_tokens, answer_tokens)

	def _get_term_prob(self, terms, prop_name, class_name):
		count_prop_name = prop_name+'_count'
		p = 1

		for term in terms:
			if term in self.__dict__[prop_name][class_name]:
				p *= self.__dict__[prop_name][class_name][term] / self.__dict__[count_prop_name][class_name][term]

		if p == 1: # term not in training set
			return 0

		return p

	def train(self, training_path, mode):
		data = [{"category": "HISTORY",
			"air_date": "2004-12-31",
			"question": "'For the last 8 years of his life, Galileo was under house arrest for espousing this man's theory'",
			"value": "$200",
			"answer": "Copernicus",
			"round": "Jeopardy!",
			"show_number": "4680"},{"category": "ESPN's TOP 10 ALL-TIME ATHLETES",
			"air_date": "2004-12-31",
			"question": "'No. 2: 1912 Olympian; football star at Carlisle Indian School; 6 MLB seasons with the Reds, Giants & Braves'",
			"value": "$200",
			"answer": "Jim Thorpe",
			"round": "Jeopardy!",
			"show_number": "4680"}]

		for question in data:
			# get counts for the classes
			self._count([question["category"]], 'classes')

			# get counts for the terms
			(question_tokens, answer_tokens) = self._get_tokens(question, mode)
			self._count(question_tokens, 'question_terms', question["category"])
			if (answer_tokens):
				self._count(answer_tokens, 'answer_terms', question["category"])

		print self.__dict__

	def validate(self, validating_path, mode):
		data = [{"category": "HISTORY",
			"air_date": "2004-12-31",
			"question": "'For the last 8 years of his life, Galileo was under house arrest for espousing this man's theory'",
			"value": "$200",
			"answer": "Copernicus",
			"round": "Jeopardy!",
			"show_number": "4680"},{"category": "ESPN's TOP 10 ALL-TIME ATHLETES",
			"air_date": "2004-12-31",
			"question": "'No. 2: 1912 Olympian; football star at Carlisle Indian School; 6 MLB seasons with the Reds, Giants & Braves'",
			"value": "$200",
			"answer": "Jim Thorpe",
			"round": "Jeopardy!",
			"show_number": "4680"}]

		# argmax( p(class) * p(term1 | class) * p(term2 | class) * ...)

		for question in data:
			class_prob = {}
			for class_name, count in self.classes.iteritems():

				# p(class)
				class_prob[class_name] = count / self.classes_count

				# p(term1 | class) * p(term2 | class) * ...
				(question_tokens, answer_tokens) = self._get_tokens(question, mode)
				class_prob[class_name] *= self._get_term_prob(question_tokens, 'question_terms', class_name)

				if (answer_tokens):
					class_prob[class_name] *= self._get_term_prob(answer_tokens, 'question_terms', class_name)

				print sorted(class_prob, key=class_prob.get)


def main():
	NaiveBayesClassifier("", "")

if __name__ == "__main__": main()

