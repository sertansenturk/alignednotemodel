import numpy as np
import PitchDistribution

def getModels(pitch, alignednotes, tonic, kernel_width=2.5):
	noteNames = set(an['Symbol'] for an in alignednotes)
	noteModels = dict((nn, {'notes':[], 'distribution':[], 
		'stablepitch':[]}) for nn in noteNames)

	# get the complete histogram
	noteModels['all'] = {'distribution':getModelDistribution(pitch[:,1]), 
						'notes':None, 'stablepitch': None}

	# compute note trajectories and add to each model
	for an in alignednotes:
		if not an['Interval'][0] == an['Interval'][1]:  # not aligned
			
			an['trajectory'] = np.vstack(p for p in pitch 
				if an['Interval'][0] <= p[0] <= an['Interval'][1])

			noteModels[an['Symbol']]['notes'].append(an)

	# compute the histogram for each model
	for key in noteModels.keys():
		if not key == 'all':
			tempPitchVals = np.hstack(nn['trajectory'][:,1] 
				for nn in noteModels[key]['notes'])

			noteModels[key]['distribution']=getModelDistribution(tempPitchVals)

			# get the stable pitch
			theoreticalpeak = noteModels[key]['notes'][0]['Pitch']['Value']
			peakCandIdx = noteModels[key]['distribution'].detect_peaks()[0]
			peakCandFreqs = [noteModels[key]['distribution'].bins[i] for i in peakCandIdx]

			peakCandCents = PitchDistribution.hz_to_cent(peakCandFreqs, tonic)
			minId = abs(peakCandCents - theoreticalpeak).argmin()
			noteModels[key]['stablepitch'] = peakCandFreqs[minId]

			# scale according to relative usage of each note
			stablepitchVal = noteModels[key]['distribution'].vals[peakCandIdx[minId]]
			allhistbin_id = abs(PitchDistribution.hz_to_cent(
				noteModels['all']['distribution'].bins,peakCandFreqs[minId])).argmin()
			allhistval = noteModels['all']['distribution'].vals[allhistbin_id]
			noteModels[key]['distribution'].vals = (noteModels[key]['distribution'].vals
				* allhistval / stablepitchVal)

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
