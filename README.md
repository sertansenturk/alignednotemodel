# alignednotemodels

Python package to compute note models from note-level audio-score alignment.

Currently the algorithm computes the stable pitch and a pitchdistribution of each aligned note.

Usage
=======

```python
from alignednotemodel import alignednotemodel

noteModels, pitchDistibution, newTonic = alignednotemodel.getModels(pitch, alignednotes, 
    tonicsymbol, kernel_width=7.5, step_size = 7.5)
```

The inputs are:
```python
# pitch 		  :	an n-by-2 matrix, where the values in the first column are 
#					the timestamps and the values in the second column are frequency 
#					values
# alignednotes	  :	the list of aligned notes. This is read from the alignedNotes.json 
#					output from the fragmentLinker (https://github.com/sertansenturk/fragmentLinker) 
#                   repository 
# tonicsymbol	  : The tonic symbol in the symbTr format (e.g. B4b1)
# kernel_width    : The width of the Gaussian kernel used to compute the pitch distribution 
#                   (default: 7.5 cent ~ 1/3 Hc)
# step_size       : The step size between each bin of the pitch distribution (default: 7.5 cent 
#                   ~ 1/3 Hc)
```

The outputs are:
```python
# noteModels        : The model for each note symbol
# pitchDistribution	: The pitch distribution computed from the pitch input
# newtonic		    : The updated tonic according to the note model of the tonic
```

Installation
============

If you want to install the repository, it is recommended to install the package and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install the repository like this instead

    pip install -e .

The algorithm uses several modules in Essentia. Follow the [instructions](essentia.upf.edu/documentation/installing.html) to install the library.

Now you can install the rest of the dependencies:

    pip install -r requirements

Authors
-------
Sertan Şentürk
contact@sertansenturk.com

Reference
-------
Thesis
