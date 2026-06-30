from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class SentinelScene(BaseModel):
    """Metadata for a single Sentinel scene."""
    scene_id: str
    satellite: str
    acquisition_date: str
    cloud_cover: Optional[float] = None
    processing_level: str
    footprint: Dict[str, Any]
    download_url: Optional[str] = None


class SceneCollection(BaseModel):
    """A collection of Sentinel scenes."""
    scenes: List[SentinelScene]
    total_results: int
