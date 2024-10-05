from dataclasses import dataclass


@dataclass
class ImageResponse:
    message: dict[str, str]
    '''Message content in the OpenAI format for the model response. '''
    usage: dict[str, int]
    '''The token usage stats for the specific response'''
