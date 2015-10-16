import pdb
import numpy as np

def getModels(pitch, alignednotes):
	noteNames = set(an['Symbol'] for an in alignednotes)
	inimodel = {'notes':[], 'distribution':[], 'stablepitch':[]}
	noteModels = dict((nn, inimodel) for nn in noteNames)

	# compute note trajectories and add to each model
	for an in alignednotes:
		if not an['Interval'][0] == an['Interval'][1]:  # not aligned
			an['pitch'] = np.vstack(p for p in pitch 
				if an['Interval'][0] <= p[0] <= an['Interval'][1])

			noteModels[an['Symbol']]['notes'].append(an)

	# compute the histogram for each model
	for key in noteModels.keys():
		pdb.set_trace()
		tempPitchVals = np.hstack(nn['pitch'][:,1] 
			for nn in noteModels[key]['notes'])
		
		