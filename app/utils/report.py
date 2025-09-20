from pathlib import Path
import pandas as pd

current_dir = Path(__file__).parent
csv_path = current_dir.parent / "exports" / "benchmark_results.csv"

df = pd.read_csv(csv_path)


# Сгруппировать по модели, усреднить avg и std_dev
summary = df.groupby('model')[['avg', 'std_dev']].mean().round(3)
summary.columns = ['Средняя задержка (сек)', 'Среднее Std Dev (сек)']
summary = summary.sort_values('Средняя задержка (сек)')

print(summary.to_markdown(tablefmt="github", floatfmt=".3f"))
