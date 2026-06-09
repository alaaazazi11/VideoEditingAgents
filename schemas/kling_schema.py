from typing import Optional
from pydantic import Field
from schemas.base_schema import BaseSchema


class KlingElementInput(BaseSchema):
    image_url: str = Field(
        ...,
        description="URL of the element image. Resolved from @Element1, @Element2 placeholders.",
    )


class KlingParams(BaseSchema):
    prompt: str = Field(
        ...,
        description="""Text prompt describing the video edit — in plain English only.
        
        CRITICAL RULES for the prompt:
        - NEVER include image URLs or @placeholder references in the prompt text
        - NEVER write things like 'swap with https://...' or 'use @Image1'
        - Images and elements are passed separately via 'elements' and 'image_urls' fields
        - The prompt should only describe WHAT to do, not reference the files
        
        Good examples:
        - 'Swap the dog with a cat'
        - 'Transform the video into anime style'
        - 'Outpaint the canvas from the top with more sky and clouds'
        - 'Swap the dog with the cat, then outpaint the top with sky and clouds'
        
        Bad examples (NEVER do this):
        - 'Swap dog with cat from https://cloudinary.com/cat.jpg'
        - 'Use @Image1 as style reference'
        - 'Apply https://... to the person'
        """,
    )

    video_url: str = Field(
        ...,
        description="URL of the reference video. Resolved automatically from @Video1.",
    )

    image_urls: Optional[list[str]] = Field(
        default=None,
        description="""List of reference image URLs for style or appearance guidance.
        Resolved from @Image1, @Image2 placeholders.
        Use this when the user references images as STYLE references (not character swaps).
        Maximum 4 total (image_urls + elements combined).
        
        Example: 'make it look like @Image1' → image_urls=["resolved_url"]
        Only extract if user explicitly references @Image1, @Image2 etc.""",
    )

    keep_audio: bool = Field(
        default=True,
        description="""Whether to keep the original audio:
        - true: preserves original audio (default)
        - false: removes audio
        If user doesn't mention audio → default true.""",
    )

    elements: Optional[list[KlingElementInput]] = Field(
        default=None,
        description="""List of character or object elements to SWAP or REPLACE in the video.
        Use this when user wants to swap/replace a person, animal, or object with an image.
        Resolved from @Image1, @Image2, @Element1, @Element2 placeholders.
        
        Example: 'swap the dog with the cat from @Image1' → elements=[{"image_url": "resolved_url"}]
        Example: 'replace the person with @Image1' → elements=[{"image_url": "resolved_url"}]
        
        IMPORTANT: put the image URL here, NOT in the prompt text.""",
    )

    shot_type: str = Field(
        default="customize",
        description="Shot type for generation. Default: 'customize'. Only change if user explicitly mentions it.",
    )