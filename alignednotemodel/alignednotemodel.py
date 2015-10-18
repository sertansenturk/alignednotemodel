import numpy as np
import PitchDistribution

def getModels(pitch, alignednotes, kernel_width=2.5):
	dummyFreq = 440.0
	noteNames = set(an['Symbol'] for an in alignednotes)
	noteModels = dict((nn, {'notes':[], 'distribution':[], 'stablepitch':[], 
		'numsamples':[]}) for nn in noteNames)

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

		noteModels[key]['numsamples'] = len(tempPitchVals)

		tempCentVals = PitchDistribution.hz_to_cent(tempPitchVals, dummyFreq)
		noteModels[key]['distribution'] = PitchDistribution.generate_pd(
			tempCentVals, ref_freq=dummyFreq, kernel_width=kernel_width, 
			step_size=7.5)
		noteModels[key]['distribution'].bins = PitchDistribution.cent_to_hz(
			noteModels[key]['distribution'].bins, dummyFreq)

	# scale according to relative usage of each note
	totalNumSamples = sum(nm['numsamples'] for nm in noteModels.values())
	for key in noteModels.keys():
		noteModels[key]['distribution'].vals = (noteModels[key]['distribution'].vals 
			* noteModels[key]['numsamples'] / totalNumSamples)

	# get the stable pitch

	return noteModels

