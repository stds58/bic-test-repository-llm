import csv
from app.core.config import settings
from app.exceptions.base import CSVExportException


EXPORT_DIR = settings.BENCHMARK_EXPORT_DIR


def export_benchmark_to_csv(benchmark_results: list):
    filename = "benchmark_results.csv"
    fieldnames = ["model", "prompt", "runs", "avg", "min", "max", "std_dev"]
    filepath = EXPORT_DIR / filename
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in benchmark_results:
                writer.writerow(row)
        return filename
    except PermissionError as e:
        raise CSVExportException(f"Нет прав на запись файла: {filename}") from e
    except OSError as e:
        raise CSVExportException(f"Ошибка файловой системы при создании {filename}: {e}") from e
    except Exception as e:
        raise CSVExportException(f"Неизвестная ошибка при экспорте в CSV: {e}") from e
