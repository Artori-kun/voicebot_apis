import importlib
import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.io import wavfile

from core.ResNetSE34V2 import MainModel
import core.constant as c
from core.loss.softmaxproto import LossFunction

def loadWAV(filename, max_frames, evalmode=True, num_eval=10):
    # Maximum audio length
    max_audio = max_frames * 160 + 240

    # Read wav file and convert to torch tensor
    sample_rate, audio = wavfile.read(filename)

    audiosize = audio.shape[0]
    
    if audiosize <= max_audio:
        shortage = max_audio - audiosize + 1
        audio = np.pad(audio, (0, shortage), 'wrap')
        audiosize = audio.shape[0]

    if evalmode:
        startframe = np.linspace(0, audiosize - max_audio, num=num_eval)
    else:
        startframe = np.array(
            [np.int64(random.random() * (audiosize - max_audio))])

    feats = []
    if evalmode and max_frames == 0:
        feats.append(audio)
    else:
        for asf in startframe:
            feats.append(audio[int(asf):int(asf) + max_audio])
    feat = np.stack(feats, axis=0).astype(np.float)

    return feat


class SpeakerNet(nn.Module):
    def __init__(self, **kwargs):
        super(SpeakerNet, self).__init__()

        # self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device('cpu')
        self.device = torch.device('cpu')

        # SpeakerNetModel = importlib.import_module(
        #     "ResNetSE34V2").__getattribute__('MainModel')
        SpeakerNetModel = MainModel
        self.__S__ = SpeakerNetModel(**kwargs).to(self.device)

        # LossFunction = importlib.import_module(
        #     'loss.' + "softmaxproto").__getattribute__('LossFunction')
        self.__L__ = LossFunction(**kwargs).to(self.device)

    def loadParameters(self, path):
        self_state = self.state_dict()
        loaded_state = torch.load(path,map_location=torch.device('cpu'))
        for name, param in loaded_state.items():
            origname = name
            if name not in self_state:
                name = name.replace("module.", "")

                if name not in self_state:
                    print("%s is not in the model." % origname)
                    continue

            if self_state[name].size() != loaded_state[origname].size():
                print("Wrong parameter length: %s, model: %s, loaded: %s" %
                      (origname, self_state[name].size(),
                       loaded_state[origname].size()))
                continue

            self_state[name].copy_(param)

    def feature(self, file_name_1):
        inp1 = torch.FloatTensor(
            loadWAV(file_name_1, c.EVAL_FRAMES, evalmode=c.EVAL_MODE,
                    num_eval=c.NUM_EVAL)).to(self.device)
        with torch.no_grad():
            ref_feat = self.__S__.forward(inp1).detach().cpu().to(self.device)
            ref_feat = F.normalize(ref_feat, p=2, dim=1)
        return ref_feat
    def check(self,file):
        try:
            inp1 = torch.FloatTensor(
                loadWAV(file, c.EVAL_FRAMES, evalmode=c.EVAL_MODE,
                        num_eval=c.NUM_EVAL)).to(self.device)
            print(inp1.shape)
            with torch.no_grad():
                ref_feat = self.__S__.forward(inp1).detach().cpu().to(self.device)
                ref_feat = F.normalize(ref_feat, p=2, dim=1)
            return True
        except:
            return False

    def compare(self, file1, file2):
        inp1 = torch.FloatTensor(
            loadWAV(file1, c.EVAL_FRAMES, evalmode=c.EVAL_MODE,
                    num_eval=c.NUM_EVAL)).to(self.device)
        with torch.no_grad():
            ref_feat_1 = self.__S__.forward(inp1).detach().cpu().to(self.device)
            ref_feat_1 = F.normalize(ref_feat_1, p=2, dim=1)
        inp2 = torch.FloatTensor(
            loadWAV(file2, c.EVAL_FRAMES, evalmode=c.EVAL_MODE,
                    num_eval=c.NUM_EVAL)).to(self.device)
        with torch.no_grad():
            ref_feat_2 = self.__S__.forward(inp2).detach().cpu().to(self.device)
            ref_feat_2 = F.normalize(ref_feat_2, p=2, dim=1)
        score = F.cosine_similarity(ref_feat_1, ref_feat_2, eps=1e-08)
        score = score.cpu().numpy()
        score = np.mean(score)
        # print(score)
        return float(score)
        # print(score)
        # if score > c.THRES:
        #     return True
        # else:
        #     return False
    def compare2(self, feature1, feature2):
        score = F.cosine_similarity(feature1, feature2, eps=1e-08)
        score = score.cpu().numpy()
        score = np.mean(score)
        return float(score)

# if __name__ == "__main__":
#     print()
