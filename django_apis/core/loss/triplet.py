import torch
import torch.nn as nn
import torch.nn.functional as F
import time, pdb, numpy
# from tuneThreshold import tuneThresholdfromScore
import random

from sklearn import metrics
def tuneThresholdfromScore(scores, labels, target_fa, target_fr=None):
    fpr, tpr, thresholds = metrics.roc_curve(labels, scores, pos_label=1)
    fnr = 1 - tpr

    tunedThreshold = [];
    if target_fr:
        for tfr in target_fr:
            idx = numpy.nanargmin(numpy.absolute((tfr - fnr)))
            tunedThreshold.append([thresholds[idx], fpr[idx], fnr[idx]]);

    for tfa in target_fa:
        idx = numpy.nanargmin(numpy.absolute((tfa - fpr)))  # numpy.where(fpr<=tfa)[0][-1]
        tunedThreshold.append([thresholds[idx], fpr[idx], fnr[idx]]);

    idxE = numpy.nanargmin(numpy.absolute((fnr - fpr)))
    eer = max(fpr[idxE], fnr[idxE]) * 100

    return (tunedThreshold, eer, fpr, fnr);

class LossFunction(nn.Module):

    def __init__(self, hard_rank=0, hard_prob=0, margin=0, **kwargs):
        super(LossFunction, self).__init__()

        self.test_normalize = True
        
        self.hard_rank  = hard_rank
        self.hard_prob  = hard_prob
        self.margin     = margin

        print('Initialised Triplet Loss')

    def forward(self, x, label=None):

        assert x.size()[1] == 2
        
        out_anchor      = F.normalize(x[:,0,:], p=2, dim=1)
        out_positive    = F.normalize(x[:,1,:], p=2, dim=1)
        stepsize        = out_anchor.size()[0]

        output      = -1 * (F.pairwise_distance(out_anchor.unsqueeze(-1),out_positive.unsqueeze(-1).transpose(0,2))**2)

        negidx      = self.mineHardNegative(output.detach())

        out_negative = out_positive[negidx,:]

        labelnp     = numpy.array([1]*len(out_positive)+[0]*len(out_negative))

        ## calculate distances
        pos_dist    = F.pairwise_distance(out_anchor,out_positive)
        neg_dist    = F.pairwise_distance(out_anchor,out_negative)

        ## loss function
        nloss   = torch.mean(F.relu(torch.pow(pos_dist, 2) - torch.pow(neg_dist, 2) + self.margin))

        scores = -1 * torch.cat([pos_dist,neg_dist],dim=0).detach().cpu().numpy()

        errors = tuneThresholdfromScore(scores, labelnp, []);

        return nloss, errors[1]

    ## ===== ===== ===== ===== ===== ===== ===== =====
    ## Hard negative mining
    ## ===== ===== ===== ===== ===== ===== ===== =====

    def mineHardNegative(self, output):

        negidx = []

        for idx, similarity in enumerate(output):

            simval, simidx = torch.sort(similarity,descending=True)

            if self.hard_rank < 0:

                ## Semi hard negative mining

                semihardidx = simidx[(similarity[idx] - self.margin < simval) &  (simval < similarity[idx])]

                if len(semihardidx) == 0:
                    negidx.append(random.choice(simidx))
                else:
                    negidx.append(random.choice(semihardidx))

            else:

                ## Rank based negative mining
                
                simidx = simidx[simidx!=idx]

                if random.random() < self.hard_prob:
                    negidx.append(simidx[random.randint(0, self.hard_rank)])
                else:
                    negidx.append(random.choice(simidx))

        return negidx
