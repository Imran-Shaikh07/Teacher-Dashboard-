$env:PORT = 5000
waitress-serve --port=$env:PORT --host=0.0.0.0 app:app
