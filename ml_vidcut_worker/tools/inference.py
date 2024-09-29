import clip
import decord
import nncore
import torch
import numpy as np
import torchvision.transforms.functional as F
from decord import VideoReader
from nncore.engine import load_checkpoint
from nncore.nn import build_model
from tabulate import tabulate

CONFIG = 'configs/qvhighlights/r2_tuning_qvhighlights.py'
WEIGHT = 'configs/r2models/r2_tuning_qvhighlights-ed516355.pth'


def load_video(video_path, cfg, device):
    decord.bridge.set_bridge('torch')

    vr = VideoReader(video_path)
    stride = vr.get_avg_fps() / cfg.data.val.fps
    fm_idx = [min(round(i), len(vr) - 1) for i in np.arange(0, len(vr), stride).tolist()]
    video = vr.get_batch(fm_idx).permute(0, 3, 1, 2).float() / 255

    size = 336 if '336px' in cfg.model.arch else 224
    h, w = video.size(-2), video.size(-1)
    s = min(h, w)
    x, y = round((h - s) / 2), round((w - s) / 2)
    video = video[..., x:x + s, y:y + s]
    video = F.resize(video, size=(size, size))
    video = F.normalize(video, (0.481, 0.459, 0.408), (0.269, 0.261, 0.276))

    video = video.reshape(video.size(0), -1).unsqueeze(0).to(device)

    return video


def run_inference(video_path, query_text, config_path=CONFIG, checkpoint_path=WEIGHT):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    cfg = nncore.Config.from_file(config_path)
    cfg.model.init = True

    if checkpoint_path.startswith('http'):
        checkpoint_path = nncore.download(checkpoint_path, out_dir='checkpoints')

    print(f'Building model from {config_path}')
    model = build_model(cfg.model, dist=False).eval()

    print(f'Loading checkpoint from {checkpoint_path}')
    model = load_checkpoint(model, checkpoint_path, warning=False)
    model = model.to(device)  

    print(f'Loading video from {video_path}')
    video = load_video(video_path, cfg, device)

    print(f'Query: {query_text}')
    query = clip.tokenize(query_text, truncate=True).to(device)

    data = dict(video=video, query=query, fps=[cfg.data.val.fps])

    with torch.inference_mode():
        pred = model(data)

    print('Prediction:')
    tab = [('Start time', 'End time', 'Score')]
    for b in pred['_out']['boundary'][:30].tolist():
        b[:2] = [min(max(0, n), video.size(1) / cfg.data.val.fps) for n in b[:2]]
        tab.append([round(n, 2) for n in b])
    print(tabulate(tab))

    return tab


# if __name__ == '__main__':
#     main()