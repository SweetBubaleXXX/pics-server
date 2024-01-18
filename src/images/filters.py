from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter

from .models import Image


class ImageFilter(Filter):
    order_by: list[str] | None = None
    owner_id: int | None = None
    created_at__gte: datetime | None = None
    created_at__lte: datetime | None = None

    class Constants(Filter.Constants):
        model = Image
        search_model_fields = ["title", "description"]
