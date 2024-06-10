"""
Author: Carolyn Jane Anderson
Date: 6/6/2023

This script takes tokenized prompts, counts token occurences of interest, and produces a tsv file of feature counts. 
tokenized_features.tsv shows an example output file.
"""

import csv

# Strings to be counted as full-word occurences 
wordlist = ["*param*","*functionname*"]
# Strings to be counted as within-word occurences (easy stemming)
containlist = ["*return*","list","dict","input","print",'[','{',"array","variable","element","example","key","number","output","consecutive","represent"]
# Strings to be counted as beginning-of-word occurences
beginlist = ["int","index"]

def make_wc_feature(w,prompt):
	return len([i for i in prompt if i==w])

def make_contain_feature(w,prompt):
	return len([i for i in prompt if i in w])

def make_begin_feature(w,prompt):
	return len([i for i in prompt if i[:len(w)] == w])

def make_features(data,wordlist,containlist):
	new_data = []
	for prompt in data:
		features = []
		for w in wordlist:
			features.append(make_wc_feature(w,prompt))
		for w in containlist:
			features.append(make_contain_feature(w,prompt))
		for w in beginlist:
			features.append(make_begin_feature(w,prompt))
		means = [f/len(prompt) for f in features]
		presence = [int(f > 0) for f in features]
		features.append(len(prompt))
		features += means
		features += presence
		new_data.append(features)
	return new_data

def export_features(prompts,data,featureNames):
	with open("tokenized_features.tsv",'w') as of:
		writer = csv.writer(of,delimiter="\t")
		writer.writerow(featureNames)
		for i,d in enumerate(data):
			writer.writerow([prompts[i]]+d)

def main():
	with open("../topic_models_tf_idf/tokenized_prompts_tuesday_with_return.tsv",'r') as of:
		reader = csv.DictReader(of,delimiter="\t")
		lines = [row for row in reader]
	tok_data = [[w.strip("'") for w in i['tokenized'].strip().strip(']').strip('[').split(', ')] for i in lines]
	prompts = [i["id"] for i in lines]
	features = make_features(tok_data,wordlist,containlist)
	for i,f in enumerate(features):
		print(tok_data[i],f)
	featureNames = ["prompt"]+wordlist+containlist+beginlist+["length"]+[n+"Mean" for n in wordlist+containlist+beginlist]+[n+"Ind" for n in wordlist+containlist+beginlist]
	featureNames = [f.replace('*','').replace('[','squareBrace').replace('{','curlyBrace') for f in featureNames]
	export_features(prompts,features,featureNames)

main()