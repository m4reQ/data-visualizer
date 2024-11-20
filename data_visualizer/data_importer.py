import dataclasses
import enum

DEFAULT_CSV_SEPARATOR = ','

class ImporterType(enum.Enum):
    CSV = enum.auto()

@dataclasses.dataclass
class CSVImporterConfig:
    auto_detect: bool
    index_column: int
    separator: str = DEFAULT_CSV_SEPARATOR
    datetime_format: str | None = None
    column_settings: list[tuple[str, type]] | None = None

@dataclasses.dataclass
class ImporterSettings:
    importer_type: ImporterType
    filepath: str
    config: CSVImporterConfig
