#!/usr/bin/env python
from combine import *
import chunker
import mlpy
import check_answers
from packer import pack
from sequence_length import       seq_length  
from punctuation_location import  punc_loc            
from apposition import question_apposition, rewrite_apposition  
from pos import                   pos_test
from bag_of_words import   vector_bag,  bag_of_words        
from novelty_factor import novelty_bool, novelty_count       
import cache_chunkers
from math import floor

def cache_file(q_id):
	base=int(10*floor(q_id/10))
	low=base+1
	high=base+10
	name='chunks/'+str(low)+'-'+str(high)+'.txt'
	return name

def question_candidates(q_id):
	'''Select some useful subset of the candidates for a particular question.
	Return them in a list.
	'''
	foo=cache_file(q_id)
	return cache_chunkers.uncache_chunks(open(foo))[q_id]

def question_learning_data(evaluators,first,last):
	x=[]
	y=[]
	for q_id in range(first,last+1):
		cand=question_candidates(q_id)
		x=x+run_evaluators(cand,evaluators)
		y=y+map(lambda a:check_answers.check_answer(q_id,a),cand)
	return y,x

def question_prediction_data(q_id,candidate,evaluators):
	x=run_evaluators([candidate],evaluators)
	return x[0],candidate

def run_question_predictions(evaluators,trained_model,first,last):
	answers=[]
	for q_id in range(first,last+1):
		y_hat=[]
		for candidate in question_candidates(q_id):
			x_test,candidate= question_prediction_data(q_id,candidate,evaluators)
			y_hat.append( ( test(trained_model,x_test) , candidate ) )
		y_hat = sorted(y_hat, key=lambda (s,_): s,reverse=True)
		y_hat = map(lambda a:(a[0],a[1][0]),y_hat)
		for i in range(0,5):
			answers.append((q_id,pack(y_hat, 50)[0]))
	return answers

def answerLine(answer):
        return str(answer[0])+' OVER9000 '+answer[1]

def answerFile(answers):
        return "\n".join(map(answerLine,answers))

def writeAnswers(stuff,filename='tmp-answers.txt'):
        answersHandle=open(filename,'w')
        answersHandle.write(stuff)
        answersHandle.close()

def main():
	trainIDs=[332,335]
	validationIDs=[336,337]
	testIDs=[338,339]
	evaluator_combinations=[
#	[seq_length],
#	[punc_loc],
	[pos_test]
#	[seq_length,punc_loc,question_apposition,rewrite_apposition,pos_test,vector_bag,bag_of_words,novelty_bool] #,novelty_count]
#	[novelty_count]
	]
	for evaluators in evaluator_combinations:
		y_train,x_train = question_learning_data(evaluators,trainIDs[0],trainIDs[1])
		print y_train
		trained=train(mlpy.Svm,y_train,x_train)
		results=run_question_predictions(evaluators,trained,validationIDs[0],validationIDs[1])
		writeAnswers(answerFile(results),'results/'+str(evaluators))
	
if __name__ == '__main__':
	main()
#	print cache_file(243)
