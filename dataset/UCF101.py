import cv2
import numpy as np
import random
import torch
from torch.utils.data import Dataset, DataLoader

class VideoDataset(Dataset):
    def __init__(self, file_paths, targets, n_frames=10, transform=None):
        self.file_paths = file_paths
        self.targets = targets
        self.transform = transform
        self.n_frames = n_frames

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        video_frames = frames_from_video_file(self.file_paths[idx], n_frames=self.n_frames)
        label = self.targets[idx]
        
        video_frames = torch.FloatTensor(video_frames)  # Shape: (num_frames, channels, height, width)
        
        if self.transform:
            video_frames = self.transform(video_frames)
        
        return video_frames, torch.tensor(label, dtype=torch.long)

def format_frames(frame, output_size):
    """Format frames to tensor with specified size"""
    frame = cv2.resize(frame, output_size)
    frame = frame / 255.0
    return frame

def frames_from_video_file(video_path, n_frames, output_size=(224, 224), frame_step=15):
    """Extract frames from video file"""
    result = []
    src = cv2.VideoCapture(str(video_path))
    
    video_length = src.get(cv2.CAP_PROP_FRAME_COUNT)
    need_length = 1 + (n_frames - 1) * frame_step

    if need_length > video_length:
        start = 0
    else:
        max_start = int(video_length) - need_length
        start = random.randint(0, max_start + 1)

    src.set(cv2.CAP_PROP_POS_FRAMES, start)
    ret, frame = src.read()
    result.append(format_frames(frame, output_size))

    for _ in range(n_frames - 1):
        for _ in range(frame_step):
            ret, frame = src.read()
        if ret:
            frame = format_frames(frame, output_size)
            result.append(frame)
        else:
            result.append(np.zeros_like(result[0]))

    src.release()
    result = np.array(result)
    result = np.transpose(result, (0, 3, 1, 2))  # (T, C, H, W) format
    return result