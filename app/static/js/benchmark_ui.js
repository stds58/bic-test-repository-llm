document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('benchmarkForm');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData();
        const fileInput = document.getElementById('prompt_file');
        const modelInput = document.getElementById('model');
        const runsInput = document.getElementById('runs');
        const visualizeCheckbox = document.getElementById('visualize');
        const downloadBtn = document.getElementById('downloadCsvBtn');
        downloadBtn.style.display = 'none';

        if (fileInput.files.length > 0) {
            formData.append('prompt_file', fileInput.files[0]);
        }
        formData.append('model', modelInput.value);
        formData.append('runs', runsInput.value);
        formData.append('visualize', visualizeCheckbox.checked ? "true" : "false");

        const button = form.querySelector('button');
        const resultsDiv = document.getElementById('results');
        button.disabled = true;
        resultsDiv.innerHTML = '<p>Запускаем бенчмарк... Это может занять несколько минут.</p>';

        try {
            const response = await fetch('/api/benchmark', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const responseData = await response.json();
            const data = responseData.results;
            const csvFilename = responseData.csv_filename;

            // Генерируем таблицу на фронтенде
            if (visualizeCheckbox.checked) {
                let tableHtml = `
                    <h2>Результаты бенчмарка</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Промпт</th>
                                <th>Runs</th>
                                <th>Avg Latency</th>
                                <th>Min Latency</th>
                                <th>Max Latency</th>
                                <th>Std Dev</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.forEach((item, index) => {
                    tableHtml += `
                        <tr>
                            <td>${index + 1}</td>
                            <td title="${escapeHtml(item.prompt)}">${escapeHtml(truncate(item.prompt, 50))}</td>
                            <td>${item.runs}</td>
                            <td>${item.avg.toFixed(3)}s</td>
                            <td>${item.min.toFixed(3)}s</td>
                            <td>${item.max.toFixed(3)}s</td>
                            <td>${item.std_dev.toFixed(3)}s</td>
                        </tr>
                    `;
                });

                tableHtml += `
                        </tbody>
                    </table>
                `;

                resultsDiv.innerHTML = tableHtml;
                downloadBtn.style.display = 'block';
                downloadBtn.onclick = async function() {
                    try {
                        const downloadUrl = `/api/download_csv?filename=${csvFilename}`;
                        const response = await fetch(downloadUrl);
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }

                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = csvFilename;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                    } catch (err) {
                        alert('Не удалось скачать файл: ' + err.message);
                        console.error(err);
                    }
                };
            } else {
                resultsDiv.innerHTML = `
                    <h2>Результаты (JSON)</h2>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            }

        } catch (err) {
            console.error("Ошибка:", err);
            resultsDiv.innerHTML = `<p style="color: red;">Ошибка: ${err.message}</p>`;
        } finally {
            button.disabled = false;
        }
    });
});

// Вспомогательные функции
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
}