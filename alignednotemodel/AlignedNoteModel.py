import numpy as np
from modetonicestimation.PitchDistribution import PitchDistribution
from modetonicestimation.Converter import Converter
import matplotlib.pyplot as plt
from copy import deepcopy


class AlignedNoteModel(object):
    def __init__(self, kernel_width=7.5, step_size=7.5):
        self.kernel_width = kernel_width
        self.step_size = step_size

    def get_models(self, pitch, alignednotes, tonic_symbol):
        pitch = np.array(pitch)
        alignednotes_ext = deepcopy(alignednotes)

        note_names = set(an['Symbol'] for an in alignednotes_ext)
        note_models = dict((nn, {'notes': [], 'distribution': [],
                                 'stable_pitch': [], 'interval': []})
                           for nn in note_names)

        # compute note trajectories and add to each model
        for an in alignednotes_ext:
            if not an['Interval'][0] == an['Interval'][1]:  # not aligned
                trajectory = np.vstack(
                    p for p in pitch
                    if an['Interval'][0] <= p[0] <= an['Interval'][1])
                notetemp = dict(an)
                notetemp['PitchTrajectory'] = trajectory

                note_models[an['Symbol']]['notes'].append(notetemp)

        # remove models without any aligned note
        for key in note_models.keys():
            if not note_models[key]['notes']:
                note_models.pop(key, None)

        # update the tonic frequency temporarily
        # NOTE: extremely unlikely but this value might shift to the next bin
        # in the note model computation. Hence we don't assign it to the
        # final tonic value.
        tonic_trajectories = [nn['PitchTrajectory'][:, 1]
                              for nn in note_models[tonic_symbol]['notes']]
        temp_tonic_freq = self._get_stablepitch_distribution(
            tonic_trajectories)[0]

        # compute the histogram for each model
        for nm in note_models.values():
            note_trajectories = [nn['PitchTrajectory'][:, 1]
                                 for nn in nm['notes']]
            peak_freq, distribution = self._get_stablepitch_distribution(
                note_trajectories, ref_freq=temp_tonic_freq)

            nm['stable_pitch'] = {'Value': peak_freq, 'Unit': 'Hz'}
            nm['distribution'] = distribution

        # update the new tonic frequency
        newtonic = {'alignment': {
            'Value': note_models[tonic_symbol]['stable_pitch'], 'Unit': 'Hz',
            'Symbol': tonic_symbol, 'Method': 'alignedNoteModel',
            'OctaveWrapped': False, 'Citation': 'SenturkPhDThesis'}}

        # get the distances wrt tonic
        for nm in note_models.values():
            interval = Converter.hz_to_cent(nm['stable_pitch']['Value'],
                                            temp_tonic_freq)
            nm['interval'] = {'Value': interval, 'Unit': 'cent'}

        # compute the complete histogram without normalization
        recording_distribution = PitchDistribution.from_hz_pitch(
            pitch, ref_freq=temp_tonic_freq, smooth_factor=self.kernel_width,
            step_size=self.step_size, norm_type=None)
        recording_distribution.cent_to_hz()

        # normalize all the distributions
        recording_distribution, note_models = self._normalize_distributions(
            recording_distribution, note_models)

        # type conversions for json serialization
        note_models = self._serialize_for_json(note_models)

        return note_models, recording_distribution, newtonic

    def _get_stablepitch_distribution(self, note_trajectories, ref_freq=None):
        temp_pitch_vals = np.hstack(nn for nn in note_trajectories)

        # useful to keep the bins coinciding with a desired value,
        # e.g. tonic frequency
        if ref_freq is None:
            ref_freq = self._get_median_pitch(temp_pitch_vals)

        distribution = PitchDistribution.from_hz_pitch(
            temp_pitch_vals, ref_freq=ref_freq,
            smooth_factor=self.kernel_width, step_size=self.step_size,
            norm_type=None)
        distribution.cent_to_hz()

        # get the stable pitch as the highest peaks among the peaks close to
        # the theoretical pitch TODO
        peaks = distribution.detect_peaks()
        peak_id = peaks[0][np.argmax(peaks[1])]
        peak_freq = distribution.bins[peak_id]

        return peak_freq, distribution

    @staticmethod
    def _get_median_pitch(pitch):
        if pitch.ndim > 1:
            pitch = pitch[:, 1]

        # filter the nan, inf and inaudible
        pitch = pitch[~np.isnan(pitch)]
        pitch = pitch[~np.isinf(pitch)]
        pitch = pitch[pitch >= 20.0]

        return np.median(pitch)

    @staticmethod
    def _normalize_distributions(recording_distribution, note_models):
        dist_norm = deepcopy(recording_distribution)

        # area normalization on the audio recording
        dist_norm.normalize(norm_type='area')

        # compute the normalization factor
        ini_max_val = max(recording_distribution.vals)
        fin_max_val = max(dist_norm.vals)
        norm_factor = fin_max_val / ini_max_val

        for nm in note_models.values():
            nm['distribution'].vals *= norm_factor

        return dist_norm, note_models

    @staticmethod
    def _serialize_for_json(note_models):
        # conversions for json serialization
        note_models_ser = deepcopy(note_models)
        for nm in note_models_ser.values():
            # convert the distribution object to dict
            nm['distribution'] = nm['distribution'].to_dict()

            # convert the pitchtrajectories to lists from numpy arrays
            for nn in nm['notes']:
                nn['PitchTrajectory'] = nn['PitchTrajectory'].tolist()
        return note_models_ser

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
                 color='#000000', alpha=0.9)
        for key in note_models.keys():
            ax2.plot(note_models[key]['distribution']['vals'],
                     note_models[key]['distribution']['bins'], label=key)

        ax2.set_yticks(
            [nm['stable_pitch']['Value'] for nm in note_models.values()])
        ax2.set_yticklabels(
            [key + ', ' + "%.1f" % val['stable_pitch']['Value'] +
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
