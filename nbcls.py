import operator
import json

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

	def __init__(self, training_filepath, validating_filepath, mode=WITHOUT_ANSWER):
		self.classes = {}
		self.classes_count = 0
		self.question_terms = {}
		self.question_terms_count = {}
		self.answer_terms = {}
		self.answer_terms_count = {}

		self.train(training_filepath, mode)

		self.result = {}

		self.validate(validating_filepath, mode)

	def _count(self, tokens, prop_name, class_name = None):
		count_prop_name = prop_name+"_count"

		prop = self.__dict__[prop_name]

		if class_name:
			if not class_name in self.__dict__[prop_name]:
				self.__dict__[prop_name][class_name] = {}
				self.__dict__[count_prop_name][class_name] = 0

			prop = self.__dict__[prop_name][class_name]
			self.__dict__[count_prop_name][class_name] += len(tokens)
		else:
			self.__dict__[count_prop_name] += 1

		for token in tokens:
			if token in prop:
				prop[token] += 1
			else:
				prop[token] = 1

		if class_name:
			self.__dict__[prop_name][class_name] = prop
		else:
			self.__dict__[prop_name] = prop


	def _get_tokens(self, data, mode):
		question_tokens = question_analyse(data["question"])
		answer_tokens = None

		if (mode == WITH_ANSWER):
			question_tokens += answer_analyse(data["answer"])

		if (mode == WITH_ANSWER_SEPERATED):
			answer_tokens = answer_analyse(data["answer"])

		return (question_tokens, answer_tokens)

	def _get_term_prob(self, terms, prop_name, class_name):
		if not class_name in self.__dict__[prop_name]:
			return 0

		count_prop_name = prop_name+"_count"
		p = 1

		for term in terms:
			if term in self.__dict__[prop_name][class_name]:
				p *= self.__dict__[prop_name][class_name][term] * 1.0 / self.__dict__[count_prop_name][class_name]
			else :
				p *= 1.0 / (self.__dict__[count_prop_name][class_name] + 1)

		return p


	def train(self, training_filepath, mode):
		with open(training_filepath) as data_file:
			rawData = json.load(data_file)

			for i, question in enumerate(rawData):
				# get counts for the classes
				self._count([question["category"]], "classes")

				# get counts for the terms
				(question_tokens, answer_tokens) = self._get_tokens(question, mode)
				self._count(question_tokens, "question_terms", question["category"])
				if (answer_tokens):
					self._count(answer_tokens, "answer_terms", question["category"])

				# if i % 100000 == 0:
				# 	print i

			# print self.classes

	def validate(self, validating_filepath, mode):
		with open(validating_filepath) as data_file:
			rawData = json.load(data_file)

			# argmax( p(class) * p(term1 | class) * p(term2 | class) * ...)
			for i, question in enumerate(rawData):
				print("Q-%d" % (i))

				class_prob = {}
				for class_name, count in self.classes.iteritems():
					# p(class)
					class_prob[class_name] = count * 1.0 / self.classes_count

					# p(term1 | class) * p(term2 | class) * ...
					(question_tokens, answer_tokens) = self._get_tokens(question, mode)
					class_prob[class_name] *= self._get_term_prob(question_tokens, "question_terms", class_name)

					if (answer_tokens):
						class_prob[class_name] *= self._get_term_prob(answer_tokens, "question_terms", class_name)

				sorted_cls_prob = sorted(class_prob.items(), key=operator.itemgetter(1), reverse=True)
				# print sorted_cls_prob

				if sorted_cls_prob[0][0] == question["category"]:
					print("Found correct class: %s, p = %e" % (sorted_cls_prob[0][0], sorted_cls_prob[0][1]))
				# else:
					# if not question["category"] in class_prob:
					# 	print("Correct class: %s not in training set" % (question["category"]))
					# else :
					# 	print("Correct class: %s, p = %e" % (question["category"], class_prob[question["category"]]))
					# print("Best class: %s, p = %e" % (sorted_cls_prob[0][0], sorted_cls_prob[0][1]))


def main():
	NaiveBayesClassifier("./JEOPARDY_QUESTIONS.json", "./JEOPARDY_QUESTIONS.json")

if __name__ == "__main__": main()

