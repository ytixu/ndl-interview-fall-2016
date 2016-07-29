#!/usr/bin/env python

import json
import operator
import sys, getopt

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
				p *= 1.0 / (self.__dict__[count_prop_name][class_name] + self.classes_count)

		return p


	def train(self, training_filepath, mode):
		with open(training_filepath) as data_file:
			raw_data = json.load(data_file)

			for i, question in enumerate(raw_data):
				# get counts for the classes
				self._count([question["category"]], "classes")

				# get counts for the terms
				(question_tokens, answer_tokens) = self._get_tokens(question, mode)
				self._count(question_tokens, "question_terms", question["category"])
				if (answer_tokens):
					self._count(answer_tokens, "answer_terms", question["category"])

				# if i % 100000 == 0:
				# 	print i

		# print self.__dict__
		print sorted(self.classes.items(), key=operator.itemgetter(1), reverse=True)

	def validate(self, validating_filepath, mode):
		total_entries = 0
		correct_entries = 0

		with open(validating_filepath) as data_file:
			raw_data = json.load(data_file)

			# argmax( p(class) * p(term1 | class) * p(term2 | class) * ...)
			for i, question in enumerate(raw_data):
				total_entries = i
				print("Q-%d" % (i))

				class_prob = {}
				for class_name, count in self.classes.iteritems():
					# p(class)
					class_prob[class_name] = count * 1.0 # / self.classes_count

					# p(term1 | class) * p(term2 | class) * ...
					(question_tokens, answer_tokens) = self._get_tokens(question, mode)
					class_prob[class_name] *= self._get_term_prob(question_tokens, "question_terms", class_name)

					if (answer_tokens):
						class_prob[class_name] *= self._get_term_prob(answer_tokens, "question_terms", class_name)

				sorted_cls_prob = sorted(class_prob.items(), key=operator.itemgetter(1), reverse=True)
				# print sorted_cls_prob

				if sorted_cls_prob[0][0] == question["category"]:
					print("\033[92m Found correct class: %s, p = %e \033[0m" % (sorted_cls_prob[0][0], sorted_cls_prob[0][1]))
					correct_entries += 1
				else:
					if not question["category"] in class_prob:
						print("Correct class: %s not in training set" % (question["category"]))
					else :
						print("Correct class: %s, p = %e" % (question["category"], class_prob[question["category"]]))
					print("Best class: %s, p = %e" % (sorted_cls_prob[0][0], sorted_cls_prob[0][1]))

		print("\033[92m Validation set: %d \033[0m" % (total_entries))
		print("\033[92m Total Matched Entries: %d \033[0m" % (correct_entries))
		print("\033[92m Convergence %f \033[0m" % (correct_entries*1.0/total_entries))



def split_file(filePath, p):
	from random import shuffle, random
	training_file = "./temp.training.json"
	validation_file = "./temp.validation.json"

	with open(filePath) as data_file:
		raw_data = json.load(data_file)
		shuffle(raw_data, random)
		n = len(raw_data) * int(p) / 100
		if n < 10:
			print "WARNING: training set less than 10 entries!"

		training, validation = raw_data[:n], raw_data[n:]

		with open(training_file, "w") as outfile:
			json.dump(training, outfile)

		with open(validation_file, "w") as outfile:
			json.dump(validation, outfile)

		print("Created training and validation files (%s, %s)" %  (training_file, validation_file))

	return (training_file, validation_file)


def show_help_and_exit(message):
	print message
	print "nbcls.py -t <training file> -v <validation file> -a <answer mode>"
	print "OR"
	print "nbcls.py -t <data file> -p <portion for training set (%)> -a <answer mode>"
	print ""
	print "Answer mode:"
	print "0 - Without answer (default)"
	print "1 - With answer mixed with question"
	print "2 - With answer as seperate parameter"
	sys.exit(0)


def main(argv):

	training_file = None
	validation_file = None
	percent = 0
	a_mode = WITHOUT_ANSWER

	try:
		opts, args = getopt.getopt(argv,"ht:s:p:a:",["tfile=","sfile=","ptraining=","amode="])
	except getopt.GetoptError:
		show_help_and_exit('Invalid input.')

	for opt, arg in opts:
		if opt == "-h":
			show_help_and_exit('')

		elif opt in ("-t", "--tfile"):
			training_file = arg

		elif opt in ("-s", "--sfile"):
			validation_file = arg

		elif opt in ("-p", "--ptraining"):
			percent = arg

		elif opt in ("-a", "--amode"):
			a_mode = arg

	if not validation_file:
		if not training_file or not percent:
			show_help_and_exit('Need at lest one file input and/or the percentage of training set.')

		training_file, validation_file = split_file(training_file, percent)

	elif not training_file:
		show_help_and_exit('No training file found.')


	NaiveBayesClassifier(training_file, validation_file, int(a_mode))


if __name__ == "__main__": main(sys.argv[1:])

