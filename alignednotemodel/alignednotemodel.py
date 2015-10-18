import numpy as np
import PitchDistribution

def getModels(pitch, alignednotes, kernel_width=2.5):
	noteNames = set(an['Symbol'] for an in alignednotes)
	noteModels = dict((nn, {'notes':[], 'distribution':[], 
		'stablepitch':[]}) for nn in noteNames)

	# compute note trajectories and add to each model
	for an in alignednotes:
		if not an['Interval'][0] == an['Interval'][1]:  # not aligned
			
			an['trajectory'] = np.vstack(p for p in pitch 
				if an['Interval'][0] <= p[0] <= an['Interval'][1])

			noteModels[an['Symbol']]['notes'].append(an)

	# compute the histogram for each model
	for key in noteModels.keys():
		tempPitchVals = np.hstack(nn['trajectory'][:,1] 
			for nn in noteModels[key]['notes'])

		noteModels[key]['distribution']=getModelDistribution(tempPitchVals)

	# get the stable pitch

	# get the complete histogram
	noteModels['all'] = {'distribution':getModelDistribution(pitch[:,1]), 
						'notes':None, 'stablepitch': None}

	# scale according to relative usage of each note
	#for key in noteModels.keys():
	#	noteModels[key]['distribution'].vals = (noteModels[key]['distribution'].vals 
	#		* noteModels[key]['numsamples'] / totalNumSamples)

	return noteModels

def getModelDistribution(pitchVals, kernel_width=2.5):
	dummyFreq = 440.0
	step_size = 7.5
	tempCentVals = PitchDistribution.hz_to_cent(pitchVals, dummyFreq)
	distribution = PitchDistribution.generate_pd(tempCentVals, 
		ref_freq=dummyFreq, kernel_width=kernel_width, step_size=step_size)
	distribution.bins = PitchDistribution.cent_to_hz(distribution.bins, 
		dummyFreq)

	return distribution
