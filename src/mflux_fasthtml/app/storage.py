from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fasthtml.common import database


@dataclass
class Generation:
    uid: str
    model: str
    prompt: str
    height: int
    width: int
    guidance: float
    quantize: int
    steps: int
    seed: int
    output_dir: str
    lora_paths_csv: Optional[str] = None
    lora_scales_csv: Optional[str] = None
    init_image_path: Optional[str] = None
    init_image_strength: Optional[str] = None
    completed_at: Optional[int] = None

    @property
    def metadata(self):
        # data is stored in the database
        return False

    @property
    def output_path(self):
        return (Path(self.output_dir) / self.uid).with_suffix(".png")

    @property
    def output(self):
        return self.output_path.as_posix()

    @property
    def is_completed(self):
        return self.output_path.exists()

    @property
    def stepwise_image_output_dir(self):
        return (Path(self.output_dir) / "stepwise").as_posix()

    @property
    def lora_paths(self):
        if self.lora_paths_csv:
            return self.lora_paths_csv.split(",")
        else:
            return None

    @property
    def lora_scales(self):
        if self.lora_scales_csv:
            return [float(_) for _ in self.lora_scales_csv.split(",")]
        else:
            return None


# gens database for storing generated image details
tables = database("data/gens.db")

gens = tables.create(
    cls=Generation,
    if_not_exists=True,
    replace=True,
    pk="uid",
)
