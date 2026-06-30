import httpx
import logging
from typing import List, Optional
from datetime import datetime

from app.core.api_config import copernicus_config
from app.services.copernicus_auth_service import copernicus_auth_service
from app.services.config_service import config_service
from app.satellite.schemas import SentinelScene, SceneCollection

logger = logging.getLogger(__name__)


class SatelliteServiceError(Exception):
    """Raised when there is an error interacting with the satellite data service."""
    pass


class SatelliteService:
    """Service to retrieve Sentinel satellite metadata from Copernicus."""

    def __init__(self):
        self._catalog_url = copernicus_config.catalog_url
        
    def _get_aoi_wkt(self) -> str:
        """Converts the configured AOI polygon from GeoJSON to WKT format."""
        boundary = config_service.get_boundary()
        # Assumes a single Polygon ring for the MVP
        coordinates = boundary.get("coordinates", [])[0]
        wkt_coords = ", ".join([f"{lon} {lat}" for lon, lat in coordinates])
        return f"POLYGON(({wkt_coords}))"

    def _get_season_date_range(self) -> tuple[str, str]:
        """Returns the start and end dates for the active season in the current year."""
        # For the hackathon MVP, hardcode to 2025 as used in the dataset examples
        # Real implementation would use current year or pass specific years
        # Kharif is June to October
        return "2025-06-01T00:00:00.000Z", "2025-10-31T23:59:59.999Z"

    async def _fetch_scenes(self, collection_name: str, max_results: int = 10) -> SceneCollection:
        """
        Generic method to search the Copernicus OData catalogue for scenes.
        """
        token = await copernicus_auth_service.get_valid_token()
        
        aoi_wkt = self._get_aoi_wkt()
        start_date, end_date = self._get_season_date_range()
        
        # OData filter query
        filter_query = (
            f"Collection/Name eq '{collection_name}' and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{aoi_wkt}') and "
            f"ContentDate/Start ge {start_date} and ContentDate/Start le {end_date}"
        )
        
        url = f"{self._catalog_url}/Products"
        params = {
            "$filter": filter_query,
            "$top": max_results,
            "$orderby": "ContentDate/Start desc",
            "$expand": "Attributes"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                
            if response.status_code != 200:
                logger.error(f"Copernicus catalogue search failed: {response.status_code}")
                raise SatelliteServiceError(f"Catalogue search failed. Status: {response.status_code}")

            data = response.json()
            products = data.get("value", [])
            
            scenes = []
            for item in products:
                # Extract cloud cover and processing level from attributes if available
                cloud_cover = None
                processing_level = "Unknown"
                
                attributes = item.get("Attributes", [])
                for attr in attributes:
                    if attr.get("Name") == "cloudCover":
                        cloud_cover = attr.get("Value")
                    elif attr.get("Name") == "productType":
                        processing_level = attr.get("Value")
                
                scenes.append(SentinelScene(
                    scene_id=item.get("Id", "unknown"),
                    satellite=collection_name,
                    acquisition_date=item.get("ContentDate", {}).get("Start", ""),
                    cloud_cover=float(cloud_cover) if cloud_cover is not None else None,
                    processing_level=processing_level,
                    footprint=item.get("GeoFootprint", {}),
                    download_url=f"{copernicus_config.download_url}/{item.get('Id')}/$value"
                ))
                
            return SceneCollection(scenes=scenes, total_results=len(scenes))
            
        except httpx.RequestError as exc:
            logger.error(f"Network error during scene search: {exc}")
            raise SatelliteServiceError(f"Failed to connect to Copernicus catalogue: {exc}")

    async def search_sentinel2(self) -> SceneCollection:
        """Search for Sentinel-2 optical scenes."""
        return await self._fetch_scenes(copernicus_config.collection_s2)

    async def search_sentinel1(self) -> SceneCollection:
        """Search for Sentinel-1 SAR scenes."""
        return await self._fetch_scenes(copernicus_config.collection_s1)

    async def get_latest_scene(self) -> Optional[SentinelScene]:
        """Returns the most recent available scene (S1 or S2)."""
        # Fetch 1 latest from both and compare
        s1_results = await self._fetch_scenes(copernicus_config.collection_s1, max_results=1)
        s2_results = await self._fetch_scenes(copernicus_config.collection_s2, max_results=1)
        
        latest_s1 = s1_results.scenes[0] if s1_results.scenes else None
        latest_s2 = s2_results.scenes[0] if s2_results.scenes else None
        
        if latest_s1 and latest_s2:
            dt_s1 = datetime.fromisoformat(latest_s1.acquisition_date.replace("Z", "+00:00"))
            dt_s2 = datetime.fromisoformat(latest_s2.acquisition_date.replace("Z", "+00:00"))
            return latest_s1 if dt_s1 > dt_s2 else latest_s2
            
        return latest_s1 or latest_s2

    async def list_available_dates(self) -> List[str]:
        """Returns a list of unique acquisition dates for all scenes."""
        s1_results = await self.search_sentinel1()
        s2_results = await self.search_sentinel2()
        
        dates = set()
        for scene in s1_results.scenes + s2_results.scenes:
            if scene.acquisition_date:
                # Extract just the YYYY-MM-DD part
                date_str = scene.acquisition_date.split("T")[0]
                dates.add(date_str)
                
        return sorted(list(dates), reverse=True)


satellite_service = SatelliteService()
