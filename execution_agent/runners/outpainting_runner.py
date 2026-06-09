from execution_agent.runners.base_runner import BaseRunner


class OutpaintingRunner(BaseRunner):

    def __init__(self):
        super().__init__(
            feature_name="outpainting",
            endpoint="fal-ai/wan-vace-14b/outpainting"
        )

    def build_input(self, params: dict) -> dict:
        return {
            "prompt": params.get("prompt"),
            "video_url": params.get("video_url"),
            "negative_prompt": params.get("negative_prompt"),
            "expand_left": params.get("expand_left", False),
            "expand_right": params.get("expand_right", False),
            "expand_top": params.get("expand_top", False),
            "expand_bottom": params.get("expand_bottom", False),
            "expand_ratio": params.get("expand_ratio", 0.25),
            "resolution": params.get("resolution", "auto"),
            "aspect_ratio": params.get("aspect_ratio", "auto"),
            "num_frames": params.get("num_frames", 81),
            "frames_per_second": params.get("frames_per_second", 16),
            "num_inference_steps": params.get("num_inference_steps", 30),
            "guidance_scale": params.get("guidance_scale", 5.0),
            "sampler": params.get("sampler", "unipc"),
            "shift": params.get("shift", 5.0),
            "seed": params.get("seed"),
            "acceleration": params.get("acceleration", "regular"),
            "video_quality": params.get("video_quality", "high"),
            "video_write_mode": params.get("video_write_mode", "balanced"),
            "interpolator_model": params.get("interpolator_model", "film"),
            "num_interpolated_frames": params.get("num_interpolated_frames", 0),
            "temporal_downsample_factor": params.get("temporal_downsample_factor", 0),
            "enable_auto_downsample": params.get("enable_auto_downsample"),
            "auto_downsample_min_fps": params.get("auto_downsample_min_fps", 15.0),
            "transparency_mode": params.get("transparency_mode", "content_aware"),
            "ref_image_urls": params.get("ref_image_urls"),
            "first_frame_url": params.get("first_frame_url"),
            "last_frame_url": params.get("last_frame_url"),
            "enable_safety_checker": params.get("enable_safety_checker"),
            "enable_prompt_expansion": params.get("enable_prompt_expansion"),
            "sync_mode": params.get("sync_mode"),
            "return_frames_zip": params.get("return_frames_zip"),
        }