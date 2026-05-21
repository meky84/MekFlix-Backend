# -*- coding: utf-8 -*-
import http.server
import socketserver
import urllib.parse
import json
import re
import os
import requests

PORT = int(os.environ.get("PORT", 8000))
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

class MekFlixHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        # Header CORS per permettere alla TV di comunicare liberamente con il server
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_GET(self):
        # Intercettiamo le rotte delle nostre API interne
        parsed_url = urllib.parse.urlparse(self.path)
        
        if parsed_url.path == '/api/proxy':
            self.handle_proxy(parsed_url.query)
        elif parsed_url.path == '/api/resolve':
            self.handle_resolver(parsed_url.query)
        else:
            # Se è una normale risorsa statica, deleghiamo al SimpleHTTPRequestHandler nativo
            super().do_GET()

    def handle_proxy(self, query_string):
        """
        Fa da proxy per evitare errori CORS quando la TV richiede dati a StreamingCommunity
        """
        params = urllib.parse.parse_qs(query_string)
        url = params.get('url', [None])[0]
        
        if not url:
            self.send_error_json("URL parametro mancante")
            return

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://streamingcommunityz.associates/'
        }

        try:
            # Risoluzione della richiesta lato server Python (nessun blocco CORS)
            response = requests.get(url, headers=headers, timeout=10)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.content)
        except Exception as e:
            self.send_error_json(str(e))

    def handle_resolver(self, query_string):
        """
        Interroga ed estrae l'URL finale .m3u8 cifrato dal video di StreamingCommunity
        utilizzando un sistema proxy lato server superando i token dinamici.
        """
        params = urllib.parse.parse_qs(query_string)
        movie_id = params.get('id', [None])[0]
        
        if not movie_id:
            self.send_error_json("ID filmato mancante")
            return

        # URL del player di streamingcommunity per ottenere l'iframe / sorgente video
        embed_url = f"https://streamingcommunityz.associates/iframe/{movie_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://streamingcommunityz.associates/'
        }

        try:
            # 1. Recuperiamo la pagina del player
            res = requests.get(embed_url, headers=headers, timeout=10)
            html = res.text

            # 2. Estraiamo la configurazione JSON contenente i flussi video (m3u8)
            # Questo pattern simula l'estrazione operata dal plugin di Kodi
            match = re.search(r'window\.masterPlaylist\s*=\s*(.*?);', html)
            if not match:
                # Proviamo con un pattern alternativo usato dai player video moderni
                match = re.search(r'const\s+playlist\s*=\s*(.*?);', html)

            if match:
                playlist_data = match.group(1).strip()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(playlist_data.encode('utf-8'))
            else:
                # Se non troviamo un JSON strutturato, proviamo a cercare link .m3u8 diretti nella pagina
                urls = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
                if urls:
                    data = {"url": urls[0]}
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode('utf-8'))
                else:
                    self.send_error_json("Impossibile trovare sorgenti multimediali compatibili")
        except Exception as e:
            self.send_error_json(str(e))

    def send_error_json(self, message):
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {"status": "error", "message": message}
        self.wfile.write(json.dumps(error_response).encode('utf-8'))

# Avvio del server
if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), MekFlixHandler) as httpd:
        print(f"Server MekFlix avviato sulla porta {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass