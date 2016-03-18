import numpy as np
from modetonicestimation.PitchDistribution import PitchDistribution
from modetonicestimation.Converter import Converter
import matplotlib.pyplot as plt
import copy


class AlignedNoteModel(object):
    def __init__(self, kernel_width=7.5, step_size=7.5):
        self.kernel_width = kernel_width
        self.step_size = step_size

    def get_models(self, pitch, alignednotes, tonic_symbol):
        pitch = np.array(pitch)
        median_pitch = self._get_median_pitch(pitch)
        alignednotes_ext = copy.deepcopy(alignednotes)

        note_names = set(an['Symbol'] for an in alignednotes_ext)
        note_models = dict((nn, {'notes': [], 'distribution': [],
                                 'stablepitch': [], 'interval': []})
                           for nn in note_names)

        # get the complete histogram
        recording_distribution = PitchDistribution.from_hz_pitch(
            pitch, ref_freq=median_pitch, smooth_factor=self.kernel_width,
            step_size=self.step_size)
        recording_distribution.cent_to_hz()

        # compute note trajectories and add to each model
        for an in alignednotes_ext:
            if not an['Interval'][0] == an['Interval'][1]:  # not aligned
                trajectory = np.vstack(
                    p for p in pitch
                    if an['Interval'][0] <= p[0] <= an['Interval'][1])
                notetemp = dict(an)
                notetemp['trajectory'] = trajectory

                note_models[an['Symbol']]['notes'].append(notetemp)

        # remove models without any alinged note
        for key in note_models.keys():
            if not note_models[key]['notes']:
                note_models.pop(key, None)

        # compute the histogram for each model
        for key in note_models.keys():
            temp_pitch_vals = np.hstack(nn['trajectory'][:, 1]
                                        for nn in note_models[key]['notes'])

            temp_median_pitch = self._get_median_pitch(temp_pitch_vals)
            distribution = PitchDistribution.from_hz_pitch(
                temp_pitch_vals, ref_freq=temp_median_pitch,
                smooth_factor=self.kernel_width, step_size=self.step_size)

            distribution.cent_to_hz()

            # get the stable pitch
            peaks = distribution.detect_peaks()
            peak_id = peaks[0][np.argmax(peaks[1])]
            peak_freq = distribution.bins[peak_id]

            note_models[key]['stablepitch'] = {'Value': peak_freq,
                                               'Unit': 'Hz'}

            # scale according to relative usage of each note; don't use
            # peaks[1] because detect_peaks outputs different values than
            # the distribution values
            stablepitch_val = distribution.vals[peak_id]
            allhistbin_id = abs(Converter.hz_to_cent(
                recording_distribution.bins, peak_freq)).argmin()
            allhistval = recording_distribution.vals[allhistbin_id]
            distribution.vals = (distribution.vals * allhistval /
                                 stablepitch_val)

            # convert the object to dict for json serialization
            note_models[key]['distribution'] = distribution.to_dict()

            # convert numpy arrays to lists for json serialization
            for nn in note_models[key]['notes']:
                nn['trajectory'] = nn['trajectory'].tolist()

        # the tonic might be updated
        newtonicfreq = note_models[tonic_symbol]['stablepitch']['Value']
        newtonic = {'alignment': {
            'Value': newtonicfreq, 'Unit': 'Hz', 'Symbol': tonic_symbol,
            'Method': 'alignedNoteModel', 'OctaveWrapped': False,
            'Citation': 'SenturkPhDThesis'}}

        # get the distances wrt tonic
        for nm in note_models.values():
            interval = Converter.hz_to_cent(nm['stablepitch']['Value'],
                                            newtonicfreq)

            nm['interval'] = {'Value': interval, 'Unit': 'cent'}

        return note_models, recording_distribution, newtonic

    @staticmethod
    def _get_median_pitch(pitch):
        if pitch.ndim > 1:
            pitch = pitch[:,1]

        # filter the nan, inf and inaudible
        pitch = pitch[~np.isnan(pitch)]
        pitch = pitch[~np.isinf(pitch)]
        pitch = pitch[pitch >= 20.0]

        return np.median(pitch)

    @staticmethod
    def plot(note_models, pitch_distribution, alignednotes, pitch):
        pitch = np.array(pitch)

        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
        ax1.plot(pitch[:, 0], pitch[:, 1], 'g', label='Pitch', alpha=0.7)
        fig.subplots_adjust(wspace=0)
        ax1.set_xlabel('Time (sec)')
        ax1.yaxis.grid(True)

        for note in alignednotes:
            ax1.plot(
                note['Interval'], [note['PerformedPitch']['Value'],
                                   note['PerformedPitch']['Value']],
                'r', alpha=0.4, linewidth=4)

        ax2.plot(pitch_distribution.vals, pitch_distribution.bins, '-.',
                 color='#606060')
        for key in note_models.keys():
            ax2.plot(note_models[key]['distribution']['vals'],
                     note_models[key]['distribution']['bins'], label=key)

        ax2.set_yticks(
            [nm['stablepitch']['Value'] for nm in note_models.values()])
        ax2.set_yticklabels(
            [key + ', ' + "%.1f" % val['stablepitch']['Value'] +
             ' Hz, ' + "%.1f" % val['interval']['Value'] + ' cents'
             for key, val in note_models.iteritems()])
        ax2.axis('off')
        ax2.set_ylim([np.min(pitch_distribution.bins),
                      np.max(pitch_distribution.bins)])
        ax2.yaxis.grid(True)

        ax2.set_xticklabels([])
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        return fig, (ax1, ax2)
