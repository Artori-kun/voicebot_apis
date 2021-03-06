import argparse

from core.models import SpeakerNet

parser = argparse.ArgumentParser(description="SpeakerNet")
# Training details
parser.add_argument(
    '--nClasses',
    type=int,
    default=1211,
    help='Number of speakers in the softmax layer, only for softmax-based losses')
parser.add_argument('--n_mels',
                    type=int,
                    default=64,
                    help='Number of mel filterbanks')
parser.add_argument('--encoder_type',
                    type=str,
                    default="ASP",
                    help='Type of encoder')
parser.add_argument('--nOut',
                    type=int,
                    default=512,
                    help='Embedding size in the last FC layer')
# args = parser.parse_args()
args, _ = parser.parse_known_args()
# load model
model = SpeakerNet(**vars(args))

model.loadParameters("core/model000000440.model")
model.eval()


def extra_feature(audio):
    result = model.feature(file_name_1=audio)
    return result

def compare_similarity(feat1, feat2):
    result = model.compare(feat1, feat2)
    return result

def compare_feautures(f1, f2):
    result = model.compare2(f1,f2)
    return  result

def check(file):
    result = model.check(file)
    return result

if __name__ == "__main__":
    # print(extra_feature("data/00001.wav"))
    # print(compare_similarity("data/00001.wav","data/00002.wav"))
    print(check("data/recording1.wav"))
    print(compare_similarity("data/negative/00001.wav","data/negative/00003.wav"))
