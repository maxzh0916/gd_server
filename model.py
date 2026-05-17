from pydantic import BaseModel
from pydantic.functional_serializers import model_serializer
from typing import Any, Optional


class Response(BaseModel):
    success: bool
    data: Optional[Any] = None
    msg: Optional[Any] = None

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        result = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.msg is not None:
            result["msg"] = self.msg
        return result
