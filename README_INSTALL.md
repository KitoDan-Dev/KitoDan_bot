# KitoDan Windows Installation

## After install
1. Launch **KitoDan** from Desktop or Start Menu.
2. If Ollama is not running, open terminal and run:
   - `ollama serve`
   - `ollama pull llama3.1:8b`
3. Open `http://localhost:4891` in browser.

## Config files
- `%APPDATA%\KitoDan\server.env`
- `%APPDATA%\KitoDan\data\kitodan.db`
- `%APPDATA%\KitoDan\logs\server.log`

## Troubleshooting
- **Port already in use**: change `PORT` in `%APPDATA%\KitoDan\server.env`.
- **Ollama offline**: run `ollama serve`.
- **Model missing**: run `ollama pull llama3.1:8b`.
- **Firewall prompt**: allow KitoDan on private networks.
