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

        if (fileInput.files.length > 0) {
            formData.append('prompt_file', fileInput.files[0]);
        }
        formData.append('model', modelInput.value);
        formData.append('runs', runsInput.value);
        formData.append('visualize', visualizeCheckbox.checked ? "true" : "false");

        const button = form.querySelector('button');
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

            const data = await response.json();

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
            } else {
                // Показываем JSON
                resultsDiv.innerHTML = `
                    <h2>📄 Результаты (JSON)</h2>
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