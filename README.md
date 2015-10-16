# aligned-note-models

Introduction
------------
Python package to compute note models from note-level audio-score alignment.

Currently the algorithm computes the stable pitch and a histogram for each aligned note.

Usage
=======

```python
from alignedpitchfilter import alignedpitchfilter

pitch_corrected, synth_pitch, notes = alignedpitchfilter.correctOctaveErrors(pitch, notes, tonic)
```

The inputs are:
```python
# pitch 		  :	an n-by-2 matrix, where the values in the first column are 
#					the timestamps and the values in the second column are frequency 
#					values
# notes			  :	list of note structure. This is read from the alignedNotes.json 
#					output from [fragmentLinker](https://github.com/sertansenturk/fragmentLinker) repository 
# tonic			  : The tonic frequency value
```

The outputs are:
```python
# pitch_corrected :	The octave corrected pitch track. The size is equal to the size of pitch
# synth_pitch	  :	Synthetic pitch track from the notes input that is used for octave correction
# notes			  : Updated list of notes with the pitch height converted to Hz from the theoretical
#					pitch height wrt the tonic
```

Installation
============

If you want to install alignednotemodels, it is recommended to install the package and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install compmusic like this instead

    pip install -e .

Now you can install the rest of the dependencies:

    pip install -r requirements

Authors
-------
Sertan Senturk
contact@sertansenturk.com

Reference
-------
Thesis