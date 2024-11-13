import dataclasses
import enum


class ImporterType(enum.Enum):
    CSV = enum.auto()

@dataclasses.dataclass
class CSVImporterConfig:
    auto_detect: bool
    separator: str = ''
    column_settings: list[tuple[str, type]] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class ImporterSettings:
    importer_type: ImporterType
    filepath: str
    config: CSVImporterConfig | None = None
