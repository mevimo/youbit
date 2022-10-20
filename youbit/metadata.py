from __future__ import annotations
import base64
import pickle
from dataclasses import dataclass
from importlib.metadata import version
from typing import Optional, Any

from youbit.settings import Settings


@dataclass
class Metadata:
    def __init__(self,
        filename: Optional[str] = None,
        md5_hash: Optional[str] = None,
        settings: Optional[Settings] = None
    ) -> None:
        self.filename = filename
        self.md5_hash = md5_hash
        self.settings = settings
        self.youbit_version = version("youbit")

    @staticmethod
    def create_from_base64(b64: str) -> Metadata:
        return pickle.loads(
            base64.b64decode(
                bytes(b64, encoding="utf8")
            )
        )

    def export_as_base64(self) -> str:
        base64_string = base64.b64encode(
            pickle.dumps(
                self
                )
            ).decode("utf8")
        return base64_string

    @property
    def settings(self) -> Settings:
        return self._settings

    @settings.setter
    def settings(self, value: Optional[Settings]) -> None:
        if not isinstance(value, Settings) and value is not None:
            raise ValueError("Value must be a Settings object.")
        self._settings = value

    def __eq__(self, other: Any) -> bool:
        if (
            isinstance(other, type(self)) and
            other.filename == self.filename and
            other.md5_hash == self.md5_hash and
            other.settings == self.settings and
            other.youbit_version == self.youbit_version
        ):
            return True
        return False
