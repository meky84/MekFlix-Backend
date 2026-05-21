<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>MekFlix Redirector</title>
    <style>
        body {
            background-color: #000000;
            color: #ffffff;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .loader {
            text-align: center;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border-left-color: #e50914;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loader">
        <div class="spinner"></div>
        <h2>Avvio di MekFlix in corso...</h2>
        <p>Connessione al server cloud Render...</p>
    </div>

    <script type="text/javascript">
        // JavaScript compatibile con Tizen 4.0 legacy (Chromium 56)
        window.onload = function() {
            var targetURL = "https://mekflix-backend.onrender.com";
            
            // Ritardo di sicurezza per l'inizializzazione dei servizi di rete della TV
            setTimeout(function() {
                window.location.href = targetURL;
            }, 1000);
        };
    </script>
</body>
</html>