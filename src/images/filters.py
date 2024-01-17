from fastapi_filter.contrib.sqlalchemy import Filter

from .models import Image


class ImageFilter(Filter):
    order_by: list[str] | None = None
    created_at: str | None = None

    class Constants(Filter.Constants):
        model = Image
        search_model_fields = ["title", "description"]
