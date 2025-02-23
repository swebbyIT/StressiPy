import aiohttp
import asyncio
import time
import logging
import argparse
import webbrowser
import json
from collections import defaultdict
from jinja2 import Template

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Variabili globali per statistiche
stats = defaultdict(lambda: {'success': 0, 'error': 0, 'total_time': 0.0, 'failed_requests': 0, 'response_times': []})
response_code_data = defaultdict(lambda: defaultdict(int))  # Memorizza i codici di risposta HTTP

# Funzione per inviare richieste asincrone senza SSL
async def fetch_url(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.93 Safari/537.36",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    start_time = time.time()
    try:
        async with session.get(url, headers=headers, ssl=False, timeout=10) as response:
            elapsed = time.time() - start_time
            stats[url]['success'] += 1
            stats[url]['total_time'] += elapsed
            stats[url]['response_times'].append(elapsed * 1000)  # Memorizza il tempo di risposta in ms
            response_code_data[url][response.status] += 1
    except asyncio.TimeoutError:
        stats[url]['error'] += 1
        stats[url]['failed_requests'] += 1
        response_code_data[url]['timeout'] += 1
    except Exception:
        stats[url]['error'] += 1
        stats[url]['failed_requests'] += 1
        response_code_data[url]['unknown_error'] += 1

# Funzione per eseguire il test con le diverse modalità di Loader.io
async def run_tests(urls, test_type, clients, duration):
    start_time = time.time()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        if test_type == "clienti_per_secondo":
            second = 0
            while second < duration:
                progress = min(int((second / duration) * 100), 100)
                print(f"\rTest in corso... {progress}%", end="", flush=True)
                for url in urls:
                    tasks = [fetch_url(session, url) for _ in range(clients)]
                    await asyncio.gather(*tasks)
                second += 1
                sleep_time = max(0, start_time + second - time.time())
                await asyncio.sleep(sleep_time)
        
        elif test_type == "clienti_per_test":
            total_requests = clients
            requests_per_second = max(1, total_requests // duration)
            for second in range(duration):
                progress = min(int(((time.time()-start_time) / duration) * 100), 100)
                print(f"\rTest in corso... {progress}%", end="", flush=True)
                for url in urls:
                    tasks = [fetch_url(session, url) for _ in range(requests_per_second)]
                    await asyncio.gather(*tasks)
                await asyncio.sleep(1)
        
        elif test_type == "clienti_distribuiti":
            tasks = set()
            for _ in range(clients):
                for url in urls:
                    tasks.add(asyncio.create_task(fetch_url(session, url)))
            elapsed_time = 0
            while elapsed_time < duration:
                elapsed_time = time.time() - start_time
                print(f"\rTest in corso... {min(int((elapsed_time/duration)*100), 100)}%", end="", flush=True)
                await asyncio.sleep(1)
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    print("\rTest completato! Generazione del report...")

# Funzione per generare il report HTML
def generate_report(output_html, test_type, duration):
    # Calcola il tempo minimo e massimo di risposta per ogni URL in millisecondi
    for url, data in stats.items():
        if data['response_times']:
            data['min_response_time'] = min(data['response_times'])
            data['max_response_time'] = max(data['response_times'])
        else:
            data['min_response_time'] = 0
            data['max_response_time'] = 0
        if data['success'] > 0:
            data['avg_response_time'] = (data['total_time'] / data['success']) * 1000
        else:
            data['avg_response_time'] = 0

    template = Template("""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Report di Carico</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1, h2 { text-align: center; }
            .summary-container { width: 80%; margin: auto; padding: 20px; border: 1px solid #ddd; background: #f9f9f9; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px; border: 1px solid #ddd; text-align: center; }
            th { background: #f4f4f4; }
        </style>
    </head>
    <body>
        <h1>Report di Carico</h1>
        <div class="summary-container">
            <h2>Riepilogo</h2>
            <p>Tipo di test: {{ test_type }} (Durata: {{ duration }} secondi)</p>
            <table>
                <tr>
                    <th>URL</th>
                    <th>Tempo medio di risposta (ms)</th>
                    <th>Tempo min/max di risposta (ms)</th>
                    <th>Richieste totali</th>
                    <th>Richieste fallite</th>
                    <th>Tasso di errore (%)</th>
                    <th>Risposte HTTP</th>
                </tr>
                {% for url, data in stats.items() %}
                <tr>
                    <td>{{ url }}</td>
                    <td>{{ "%.2f"|format(data['avg_response_time']) }}</td>
                    <td>{{ "%.2f"|format(data['min_response_time']) }} / {{ "%.2f"|format(data['max_response_time']) }}</td>
                    <td>{{ data['success'] + data['error'] }}</td>
                    <td>{{ data['failed_requests'] }}</td>
                    <td>{{ "%.2f"|format((data['error'] / (data['success'] + data['error']) * 100) if (data['success'] + data['error']) > 0 else 0) }}</td>
                    <td>
                        {% for code, count in response_code_data[url].items() %}
                        {{ code }}: {{ count }}<br>
                        {% endfor %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """)

    with open(output_html, 'w') as f:
        f.write(template.render(stats=stats, response_code_data=response_code_data, test_type=test_type, duration=duration))

    webbrowser.open(output_html)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-type', type=str, choices=["clienti_per_secondo", "clienti_per_test", "clienti_distribuiti"], required=True)
    parser.add_argument('--clients', type=int, required=True)
    parser.add_argument('--duration', type=int, required=True)
    parser.add_argument('--output-file', type=str, default='report.html')
    parser.add_argument('urls', nargs='+')
    args = parser.parse_args()

    asyncio.run(run_tests(args.urls, args.test_type, args.clients, args.duration))
    generate_report(args.output_file, args.test_type, args.duration)
