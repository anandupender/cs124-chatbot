import csv
import collections

emotionDictionary = collections.defaultdict(lambda:0)
myFile = open("emotionsParsed.txt","w")

emotions_to_skip = [1,5,6,8,9]

reader = csv.reader(file('emotions.txt'), delimiter='\t')
word_emotions = []
extraCounter = 0
for counter, line in enumerate(reader):
	if counter % 10 not in emotions_to_skip: #anticipation 5689
		word_emotions.append(line[2])

	if counter % 10 == 9:	# last emotion word
		contains_emotion_trigger = False
		for emotion in word_emotions:
			if emotion != "0":
				contains_emotion_trigger = True
		if contains_emotion_trigger:		# has some emotion!
			print line[0]
			emotionDictionary[line[0]] = word_emotions
			extraCounter = extraCounter + 1
			myFile.write(line[0])
			for emotion in word_emotions:
				myFile.write(",")
				myFile.write(emotion)
			myFile.write("\n")
		word_emotions = []	# reset array 
print extraCounter

myFile.close()

# KEEP THESE: anger, disgust, fear, joy, sadness