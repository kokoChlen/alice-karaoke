import argparse
import os

import librosa
import numpy as np
import soundfile as sf
import torch
from tqdm import tqdm

from lib import dataset
from lib import nets
from lib import spec_utils
from lib import utils

class Separator(object):

    def __init__(self, model, device, batchsize, cropsize, postprocess=False):
        self.model = model
        self.offset = model.offset
        self.device = device
        self.batchsize = batchsize
        self.cropsize = cropsize
        self.postprocess = postprocess

    def _separate(self, X_mag_pad, roi_size):
        X_dataset = []
        patches = (X_mag_pad.shape[2] - 2 * self.offset) // roi_size
        for i in range(patches):
            start = i * roi_size
            X_mag_crop = X_mag_pad[:, :, start:start + self.cropsize]
            X_dataset.append(X_mag_crop)

        X_dataset = np.asarray(X_dataset)

        self.model.eval()
        with torch.no_grad():
            mask = []
            # To reduce the overhead, dataloader is not used.
            for i in tqdm(range(0, patches, self.batchsize)):
                X_batch = X_dataset[i: i + self.batchsize]
                X_batch = torch.from_numpy(X_batch).to(self.device)

                pred = self.model.predict_mask(X_batch)

                pred = pred.detach().cpu().numpy()
                pred = np.concatenate(pred, axis=2)
                mask.append(pred)

            mask = np.concatenate(mask, axis=2)

        return mask

    def _preprocess(self, X_spec):
        X_mag = np.abs(X_spec)
        X_phase = np.angle(X_spec)

        return X_mag, X_phase

    def _postprocess(self, mask, X_mag, X_phase):
        if self.postprocess:
            mask = spec_utils.merge_artifacts(mask)

        y_spec = mask * X_mag * np.exp(1.j * X_phase)
        v_spec = (1 - mask) * X_mag * np.exp(1.j * X_phase)

        return y_spec, v_spec

    def separate(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = dataset.make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)
        mask = mask[:, :, :n_frame]

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec

    def separate_tta(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = dataset.make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)

        pad_l += roi_size // 2
        pad_r += roi_size // 2
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask_tta = self._separate(X_mag_pad, roi_size)
        mask_tta = mask_tta[:, :, roi_size // 2:]
        mask = (mask[:, :, :n_frame] + mask_tta[:, :, :n_frame]) * 0.5

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec


def separate_audio(input_file, output_dir="", output_image=False, tta=False):

    pretrained_model = 'models/baseline.pth'
    sr = 44100
    n_fft = 2048
    hop_length = 1024
    batchsize = 4
    cropsize = 256
    postprocess = True  # or False based on your preference
    gpu = -1  # Set to the GPU index you want to use, or -1 for CPU

    #print('loading model...', end=' ')
    device = torch.device('cpu')
    model = nets.CascadedNet(n_fft, 32, 128)
    model.load_state_dict(torch.load(pretrained_model, map_location=device))
    if gpu >= 0:
        if torch.cuda.is_available():
            device = torch.device('cuda:{}'.format(gpu))
            model.to(device)
    #print('done')

    #print('loading wave source...', end=' ')
    X, _ = librosa.load(input_file, sr=sr, mono=False, dtype=np.float32, res_type='kaiser_fast')
    #print('done')

    if X.ndim == 1:
        # mono to stereo
        X = np.asarray([X, X])

    #print('stft of wave source...', end=' ')
    X_spec = spec_utils.wave_to_spectrogram(X, hop_length, n_fft)
    #print('done')

    sp = Separator(model, device, batchsize, cropsize, postprocess)
    if tta:
        y_spec, v_spec = sp.separate_tta(X_spec)
    else:
        y_spec, v_spec = sp.separate(X_spec)

    #print('validating output directory...', end=' ')
    output_dir = output_dir.rstrip('/') + '/'
    os.makedirs(output_dir, exist_ok=True)
    #print('done')

    #print('inverse stft of instruments...', end=' ')
    wave = spec_utils.spectrogram_to_wave(y_spec, hop_length=hop_length)
    #print('done')
    sf.write('{}{}_Instruments.wav'.format(output_dir, os.path.basename(input_file)), wave.T, sr)

    #print('inverse stft of vocals...', end=' ')
    wave = spec_utils.spectrogram_to_wave(v_spec, hop_length=hop_length)
    #print('done')
    sf.write('{}{}_Vocals.wav'.format(output_dir, os.path.basename(input_file)), wave.T, sr)
def use(song):
    input_audio = f'C:\\proect\\songs_data\\{song}\\{song}.mp3'
    output_directory = f'C:\\proect\\songs_data\\{song}\\'
    separate_audio(input_audio, output_dir=output_directory, output_image=False, tta=False)
