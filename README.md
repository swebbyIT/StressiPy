# StressiPy

StressiPy è uno strumento open-source per eseguire test di carico su URL specifici utilizzando richieste HTTP asincrone con `aiohttp`. Questo script consente di simulare diverse strategie di carico per valutare le prestazioni di siti web e API, generando un report HTML con i risultati dettagliati.

## Funzionalità
- Test di carico con tre modalità:
  - `clienti_per_secondo`: Simula un numero fisso di richieste al secondo.
  - `clienti_per_test`: Distribuisce un numero totale di richieste su un periodo definito.
  - `clienti_distribuiti`: Mantiene un numero fisso di client concorrenti per un periodo definito.
- Report HTML con statistiche dettagliate, inclusi:
  - Tempi di risposta (medio, minimo, massimo)
  - Percentuale di errori
  - Distribuzione dei codici di stato HTTP
- Utilizzo asincrono per massimizzare l'efficienza e ridurre i tempi di test.

## Installazione

Prima di iniziare, assicurati di avere **Python 3.7+** installato sul tuo sistema.

### 1. Clona il repository
```bash
git clone https://github.com/tuo-username/StressiPy.git
cd stressipy
```

### 2. Installa le dipendenze
```bash
pip install -r requirements.txt
```

## Utilizzo

Puoi eseguire lo script fornendo gli URL da testare e i parametri desiderati.

### Esempi di utilizzo

#### 1. Test con un numero fisso di richieste al secondo
```bash
python stressipy.py --test-type clienti_per_secondo --clients 10 --duration 30 https://example.com
```
Questo comando invierà 10 richieste al secondo all'URL specificato per 30 secondi.

#### 2. Test con un numero totale di richieste distribuite nel tempo
```bash
python stressipy.py --test-type clienti_per_test --clients 100 --duration 30 https://example.com
```
Questo comando eseguirà 100 richieste totali distribuite in 30 secondi.

#### 3. Test mantenendo un numero fisso di client concorrenti
```bash
python stressipy.py --test-type clienti_distribuiti --clients 20 --duration 60 https://example.com
```
Questo comando manterrà 20 client concorrenti inviando richieste in parallelo per 60 secondi.

#### 4. Testare più domini contemporaneamente per i vari test
StressiPy consente di testare più URL contemporaneamente. Basta elencare gli URL separati da uno spazio.

### Generazione del report
Alla fine del test, viene generato un file HTML con i risultati, che si aprirà automaticamente nel browser. Puoi specificare un nome personalizzato per il file di output con l'opzione `--output-file`:
```bash
python stressipy.py --test-type clients_per_second --clients 10 --duration 30 --output-file my_report.html https://example.com
```
### Dati del report
Il report generato fornisce una panoramica dettagliata delle prestazioni dei siti testati, includendo:
	•	Tempo medio di risposta (ms) – Il tempo medio impiegato per ottenere una risposta dal server.
	•	Tempo minimo e massimo di risposta (ms) – Il valore più basso e più alto registrato durante il test.
	•	Numero totale di richieste – Quante richieste sono state inviate all’URL.
	•	Numero di richieste fallite – Quante richieste non hanno ricevuto una risposta valida.
	•	Tasso di errore (%) – Percentuale di richieste che hanno fallito rispetto al totale.
	•	Distribuzione dei codici di stato HTTP – Il numero di risposte ricevute suddivise per codice di stato (200, 404, 500, ecc.).

Questi dati permettono di analizzare le prestazioni del server e identificare eventuali colli di bottiglia o problemi di stabilità.

## Contributi
Se vuoi contribuire al progetto, sentiti libero di aprire una **Issue** o un **Pull Request**!

## Licenza
Questo progetto è distribuito sotto licenza **MIT**.

---

Se hai suggerimenti o feedback, non esitare a contattarmi! 🚀

