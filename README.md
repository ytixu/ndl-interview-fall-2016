###Naive Bayes Classifier for Jeopardy!

This packages contains

```
nbcls.py
report.html
test/
	|_ training_result/
		|_training_result_classes.txt
		|_training_result01.txt
		|_...
		|_training_result29.txt
	|_30-a0.txt
	|_30-a1.txt
	|_30-a2.txt
	|_overall.txt
	|_temp.training.json
	|_temp.validation.json
makefile
```


####DESCRIPTION OF THE FILES

'report.html' is the small write up.

'nbcls.py' is the classifier.

`test/temp.training.json` and `test/temp.validation.json` are the files that I used to do the experiment.

In `test/training_result/`, I dump the data from the training set after the classifer trained itself. 'training_result_classes.txt' contains counts for each class. The other files contains counts for each terms (as the original file was big, I split it into smaller files).

'test/30-a0.txt' is the result for Variation 0 with 30% validation set.

'test/30-a1.txt' is the result for Variation 1 with 30% validation set.

'test/30-a2.txt' is the result for Variation 2 with 30% validation set.

'test/overall.txt' stores the convergence for all the variations.


####Manual Run
The make runs the command
```
$ python nbcls.py -t "../JEOPARDY_QUESTIONS.json" -p 70 -a 2
```
Which assumes to split the data in file JEOPARDY_QUESTIONS.json into 30% validation and 70% training, and it uses variation 2.

You can change this setting by referring to the information listed under the help command.
```
$ python nbcls.py -h

nbcls.py -t <training file> -v <validation file> -a <variation mode>
OR
nbcls.py -t <data file> -p <portion for training set (%)> -a <variation mode>

Variation mode:
0 - Without answer (default)
1 - With answer mixed with question
2 - With answer as seperate parameter

```
