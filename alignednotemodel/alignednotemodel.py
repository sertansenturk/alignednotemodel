import numpy as np
import PitchDistribution

def getModels(pitch, alignednotes, tonic, tuning, kernel_width=2.5):
	noteNames = set(an['Symbol'] for an in alignednotes)
	noteModels = dict((nn, {'notes':[], 'distribution':[], 
		'stablepitch':[], 'interval': []}) for nn in noteNames)

	# get the complete histogram
	recordingDistribution = getModelDistribution(pitch[:,1])

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
		theoreticalpeak = noteModels[key]['notes'][0]['Pitch']['Value']
		peakCandIdx = noteModels[key]['distribution'].detect_peaks()[0]
		peakCandFreqs = [noteModels[key]['distribution'].bins[i] for i in peakCandIdx]

		peakCandCents = PitchDistribution.hz_to_cent(peakCandFreqs, tonic['Value'])
		minId = abs(peakCandCents - theoreticalpeak).argmin()
		noteModels[key]['stablepitch'] = {'Value': peakCandFreqs[minId], 
			'Unit': 'cent'}

		# scale according to relative usage of each note
		stablepitchVal = noteModels[key]['distribution'].vals[peakCandIdx[minId]]
		allhistbin_id = abs(PitchDistribution.hz_to_cent(
			recordingDistribution.bins,peakCandFreqs[minId])).argmin()
		allhistval = recordingDistribution.vals[allhistbin_id]
		noteModels[key]['distribution'].vals = (noteModels[key]['distribution'].vals
			* allhistval / stablepitchVal)

	# the tonic might be updated

	tonicFreq = noteModels[tuning['tonicSymbol']]['stablepitch']['Value']
	newtonic = {'alignment': {'Value': tonicFreq, 'Unit': 'Hz', 
				'Method': 'alignedNoteModel', 'OctaveWrapped': False, 
				'Citation': 'SenturkPhDThesis'}}

	# get the distances wrt tonic
	for nm in noteModels.values():
		interval = PitchDistribution.cent_to_hz(nm['stablepitch']['Value'],
			tonic['Value'])
		nm['interval'] = {'Value': interval, 'Unit': 'cent'}

	return noteModels, recordingDistribution, newtonic

def getModelDistribution(pitchVals, kernel_width=2.5):
	dummyFreq = 440.0
	step_size = 7.5
	tempCentVals = PitchDistribution.hz_to_cent(pitchVals, dummyFreq)
	distribution = PitchDistribution.generate_pd(tempCentVals, 
		ref_freq=dummyFreq, kernel_width=kernel_width, step_size=step_size)
	distribution.bins = PitchDistribution.cent_to_hz(distribution.bins, 
		dummyFreq)

	return distribution
