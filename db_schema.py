from typing import List, Optional
from pydantic import BaseModel

class SelectedFrames(BaseModel):
    id: List[str]
    path: List[str]

class Thumbnails(BaseModel):
    id: List[str]
    path: List[str]

class ClipCapCaption(BaseModel):
    id: List[str]
    ClipCapCaption: List[str]

class Video(BaseModel):
    camera_model: str
    created_time: str
    duration: str
    ext: str
    filename: str
    fps: str
    height: str
    width: str
    captions: List[ClipCapCaption]
    selected_frames: List[SelectedFrames]
    thumbnails: List[Thumbnails]

# {
#     "camera_model": "Canon PowerShot G12",
#     "captions": [
#         {
#             "ClipCapCaption": [
#                 "a diver swims over a coral reef.",
#                 "coral reef outside the island.",
#                 "coral reef outside the island.",
#                 "coral reef outside the island.",
#                 "coral reef outside the island.",
#                 "a diver swims over a coral reef.",
#                 "coral reef outside the island.",
#                 "coral reef outside the island.",
#                 "a clownfish on a coral reef.",
#                 "a diver swims over a coral reef."
#             ],
#             "id": [
#                 "00001",
#                 "00002",
#                 "00003",
#                 "00004",
#                 "00005",
#                 "00006",
#                 "00007",
#                 "00008",
#                 "00009",
#                 "00010"
#             ]
#         }
#     ],
#     "created_time": "2012:04:04 03:08:10",
#     "duration": "10.47 s",
#     "ext": "mp4",
#     "filename": "0001.mp4",
#     "fps": "23.976",
#     "height": "720",
#     "selected_frames": [
#         {
#             "id": [
#                 "00001",
#                 "00002",
#                 "00003",
#                 "00004",
#                 "00005",
#                 "00006",
#                 "00007",
#                 "00008",
#                 "00009",
#                 "00010"
#             ],
#             "path": [
#                 "information/selected_frames/Ambon_Apr2012/0001_00001.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00002.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00003.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00004.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00005.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00006.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00007.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00008.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00009.jpg",
#                 "information/selected_frames/Ambon_Apr2012/0001_00010.jpg"
#             ]
#         }
#     ],
#     "thumbnails": [
#         {
#             "id": [
#                 "00001",
#                 "00002",
#                 "00003",
#                 "00004",
#                 "00005",
#                 "00006",
#                 "00007",
#                 "00008",
#                 "00009",
#                 "00010"
#             ],
#             "path": [
#                 "information/thumbnails/Ambon_Apr2012/0001_00001.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00002.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00003.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00004.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00005.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00006.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00007.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00008.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00009.jpg",
#                 "information/thumbnails/Ambon_Apr2012/0001_00010.jpg"
#             ]
#         }
#     ],
#     "width": "1280"
# }
