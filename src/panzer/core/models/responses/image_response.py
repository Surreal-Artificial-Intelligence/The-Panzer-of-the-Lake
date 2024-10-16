from dataclasses import dataclass


@dataclass
class ImageResponse:
    image_url: str | None
    '''URL of the image being returned'''
    metadata = None
    '''Metadata about the image being returned'''
