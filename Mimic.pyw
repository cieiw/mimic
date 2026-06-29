"""
Mimic - Gerenciador de Modelos e Frames
Desenvolvido para automação de fluxo de trabalho com Google Flow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import subprocess
import threading
import concurrent.futures
import sys
import time
import random
import base64
import queue
import re
import uuid
import hashlib
import ctypes
from urllib.parse import urljoin
import urllib.request
import urllib.error
from pathlib import Path

# Verifica dependências
try:
    from PIL import Image, ImageTk, ImageOps, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import pyautogui
    import pyperclip
    SCREEN_AUTOMATION_AVAILABLE = True
except ImportError:
    SCREEN_AUTOMATION_AVAILABLE = False

try:
    import win32con
    import win32gui
    WINDOWS_DIALOG_AUTOMATION_AVAILABLE = True
except ImportError:
    WINDOWS_DIALOG_AUTOMATION_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    import asyncio
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

APP_NAME = "Mimic"
SWAP_ICON_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAABChUlEQVR4nO2dd7wU1fn/32dmZ/veyq1UqQJSxIYV"
    "UCyg2LAroiBfjdiNftWfX2P7msRvjDExiZpmS4wxRk2MvYLdiA1EihQB6eW2rTNzfn/Mzt5LuQW5e3f27rx9rcDe"
    "uTuzM+d8znOe85znARcXFxcXF5fCQ5RFhshcX4SLi0tuUHJ9AS4uLrnDFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLG"
    "FQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLG"
    "FQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLG"
    "FQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGFQAXlwLGk+sLyDeEABAt/p3+uwDR4v2uQ+bgnM5CZv4HUsrMu9K9Ne3i"
    "CkA7CCEyL9M00y8j/afENE2kKZFYf7cx2+iYgs4Ti4wAFTBCCBRFQQiBqirpvyuZv0spMy+X7XEFYAfsDmX/qes6"
    "yUSSpK4TDPgJBPwEg0HKykvo2bOGyqoelJQUEYmEKC8vQ/NqqKpKpCjc2glIxhNEo7E9vFAwDZP6ugYK2QoQQtDY"
    "FGXTxi2sX7eR1avXsnHDJmKxOI2NUeLxBB5VwefzoWpqWngt68AVBFcAMggBiqJiGAbJZArTMJFIqqsrGDxkAIP3"
    "HsiIkUMZPKQ/A/v3o7yH3dldN4pTME2TVEqnbls9S5cuZ/6XX7Pwq8UsWbycrxcuYd3aDUgJQhH4fF5UVcEwJYU8"
    "VxBlkSEF++1t015KSSqlE4vFCIdD9O3Xm0MPO4AJRx7KPiP2pmevWsLhYKufY5mXIKW53XttnJnOstzdKYCForQu"
    "xPF4glXffseC+V/z5hvv8u7cD1m5cg11dfUEg0E8HjXTDgrNKihYAbDnhrFoDKEIBg7ciwlHHca4CQdzxLiDKSsr"
    "QUrZYipgIESzaOyI2xFzy44dt2VnVlU1854Qgvq6BubO+YDXX53Lq6/OYcXybzFNid/vR1HEdr6c7k7BCYCiKkhT"
    "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"
    "4fE4y+nmmFD1DtAlAmAF/aTYq39fLrtiZov3O+fz7WoxAwf1Z9Yl53XtA5AghEo8uY54cmP29wRIazPQ5g06WzZ1"
    "9XTHWXy1YDGNmfm/czqd35f7op8dpWsEQBHEYnHOO/80Bgzqlw7j7dyWa3/eudOmMnyfISSTXWMFWNuBvUSTa4km"
    "1yCEllUBkhI0r2DdGp2N6/TMe4WE/X0//uhzYrG44/aEBEP5U64t6wKgKArxWJwx+41g2gWnA9nxjAohMA2THj3K"
    "OP+CMzr/BK0iUYRKMrWNxtjy7J9NgqpC/VaTFUusEFiHtf+sYjkAFZLJFJ/O+9JxGaIgvwQ56wIgkZim5MqrZ9G7"
    "d21WyzjZocTnTTuNgw4akwkRzTrSygy8rWkhhhlHZPm2SqyAoM8+bMA00slR8qjR7Qm2qb9w4WK+/nopXq/XUeZ/"
    "vpHVlmqH/I4bfzCTjz8KyG7RBLt+fKQozJVXzyIYCGRlurEjMl0bYFvjFyRTW9LOzez6ARRVsGIRrF/XaL9VENh9"
    "fd5/vmTN6rVomscVgD0gawJg79QKBoNcdsXMLiviaI/4Rx87jiPGjyUeT3SJiagIlYS+hbroIgSerHZIKUHTFNav"
    "jfHJB5vS73X/TmCb/1JKXn3l7fQGoO7/vbNJ1gTAzvQzafIEJh1/JNA1JZNsX4DP72P6BWcQCgW7oHy0RAgV3Whi"
    "a+OXINpOatIZCCHRUz6++rQJXY8VxG44+/t9880KPv7oM8eVBMtHsiIAdqafktJiLr50emYbb1c5a2xfwAknHcMJ"
    "Jx6d9gVk2d0hQaCyueET4okNCJHdNOGmaRII+vjy4ybWrrar0XZvBZDSEvKXX3yTDes3onlc839PyZoAxOMJZl50"
    "NocedkB6918XRue1EJzLLr+Q6prKrFcVkpgoio/G+HK2Rb9CiGwnCRWoqknd5iLef2dl5r3uih3+G4vFefXltx1a"
    "JSr/6PReaZX3StKnT09mXHROZ398h7GDg8bsP4oTpkwklcp+XICVHCTJhm3vIM1UF3RHE1UJ8u6rURKJqJUbv5sO"
    "iPZIP++TL/nww0/x+33u6N8JZGVYNgyDmbPOYcDAfpgy+1749pg561xqaqqyXlpMpusEbm74hIbYcpQsBwWZpsQf"
    "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"
    "PyNHDeOMM0/kyImHM3hI/+1KN1mOw2bT0BWE/MMWdXs3qf0MUymdrxcu4Yk/P8vTf/8X365cg6Z58Pt9mGbbST+7"
    "CwUnAC1RVRXDMIjHExiGQU1NFQcctC9HH3MEE448jN59avD5fNv9zq6zwRauczDbgtiRTmgdsvNxu7LidF1n44bN"
    "vPXGezz/r1eYO/cj1q/biM/nxefzArLVTFPdkYIWABtrVIBkMkU8lkBVFSoqezBy1DD2P2A0o8fsw9Chg9irf+92"
    "CzsWUuORO4VFdjI7WFxC7J7g2JZbfX0jX37xFZ/Nm88HH3zKRx9+wprVazEMq7S35tWQBTLi74grAC0QQqTTjpvo"
    "KYN4IkHKSFEUitCjooya2mqGDRvEgEH92HvoIHr1qqGoKEIwFCASCRMI+F0nYhaxnXaGYZBKpaxXMkUimSIRSxCN"
    "xWhqilFf38C3K1ezYvkqFixYxKqVa1i7dj0bNm5GUQQBvx+Px4OiiIIx9VvDFYBWsMTAGoF03Wpwekq3DE0pMaUk"
    "EglTUVFOcXGEsvIyIpEwwZC/IPwEVqJWL4FA9vLeJZNJEokkkK4YnUiSiCfRdZ14IkEykSAeTxKLxmhqitLQ0Ehd"
    "XQO6bljWQjqaU1EEXq8XTfMgoe3kMQWGKwAdoLUVAdM00XU9nWzUwDBNTAqncUkkZhYXxgUCpUU8tbD/EwJFKIi0"
    "QCuKgqIIVFVFVXddrqu9Sj6FiltBswO0XDraEU3T8Hq9VgCQvX+gqy8wp2T72zbf8+1vv2zx7+a/d9f1+mzhCsAe"
    "4o4sLvmM67FycSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlg"
    "XAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlgXAFwcSlg"
    "XAFwcSlgXAFwcSlgXAFwcSlgXAFwcXFxcXFxcXFxcXFxcSkM/j/SXSYI0bee8gAAAABJRU5ErkJggg=="
)


FLOW_FIRST_UPLOAD_IMG_SEL = (
    "#__next > div.sc-c7ee1759-1.jhwuTJ "
    "> div.sc-682f0b3f-0.iPxPxr "
    "> div.sc-e4f4e472-0.iUuqJB "
    "> div > div > div > div.sc-888a6226-2.iyGxUz "
    "> div > div > div:nth-child(1) > div > div > span > div > div > div > div > span > div > a > img"
)

# Botão que abre o painel de Uploads na barra lateral do Google Flow.
# Deve ser clicado APÓS o envio das imagens.
FLOW_UPLOADS_BTN_SEL = (
    "#__next > div[class*=\"sc-c7ee1759\"] "
    "> div[class*=\"sc-682f0b3f\"] "
    "> div[class*=\"sc-265fb5e0\"] "
    "> div:nth-child(5) > button"
)

# Container raiz do painel de Uploads do Google Flow.
# O input[type="file"] de envio fica dentro desse elemento.
FLOW_UPLOAD_CONTAINER_SEL = (
    "#__next > div.sc-c7ee1759-1.jhwuTJ "
    "> div.sc-682f0b3f-0.iPxPxr "
    "> div.sc-e4f4e472-0.iUuqJB "
    "> div > div"
)

# Versão genérica (sem :nth-child fixo) — casa com o <img> de CADA item do
# painel de Uploads. Usado com .first / .last para seleção por intervalo.
FLOW_ALL_UPLOAD_IMGS_SEL = (
    "#__next > div.sc-c7ee1759-1.jhwuTJ "
    "> div.sc-682f0b3f-0.iPxPxr "
    "> div.sc-e4f4e472-0.iUuqJB "
    "> div > div > div > div.sc-888a6226-2.iyGxUz "
    "> div > div > div > div > div > span > div > div > div > div > span > div > a > img"
)

# ─── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
BASE_DIR   = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
ASSETS_DIR = BASE_DIR / "assets"
MIMIC_LOGO_FILE = ASSETS_DIR / "logo.png"
MIMIC_ICON_FILE = ASSETS_DIR / "logo.ico"
CONFIG_FILE = ASSETS_DIR / "config.json"
MODELS_FILE = ASSETS_DIR / "modelos.json"
PROMPTS_FILE = ASSETS_DIR / "prompts.json"
VIDEOS_DIR  = BASE_DIR / "• VídeosOg"
PHOTOS_DIR  = ASSETS_DIR / "fotos_modelos"
WORK_DIR    = ASSETS_DIR / "work"          # pastas geradas ficam aqui
READY_DIR   = BASE_DIR / "• Pronto"
MOTION_DIR  = ASSETS_DIR / "• Motion"
VIDEO_FILTER_4K = (
    "scale=2160:3840:force_original_aspect_ratio=decrease:"
    "force_divisible_by=2:out_range=tv,"
    "pad=2160:3840:(ow-iw)/2:(oh-ih)/2:black,"
    "setsar=1,format=yuv420p"
)
FLOW_URL    = "https://labs.google/fx/pt/tools/flow/project/190ffcfc-7547-4288-9507-e6f47628c33f"
CHROME_SESSION = r"C:\Temp\chrome_motionhub"   # perfil isolado do Chrome para debugging do Mimic
CHROME_SESSION_COPY = r"C:\Temp\chrome_motionhub_perfil"  # copia de um perfil real para debug
CHROME_SESSION_NOVO = r"C:\Temp\chrome_motionhub_novo"  # perfil novo e persistente p/ login manual
MOTION_SESSION_BASE = r"C:\Temp\chrome_motion"  # base para sessoes isoladas dos perfis Motion
CHROME_USER_DATA = Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data"
MOTION_URL = (
    "https://www.runninghub.ai/workflow/"
    "2067029951899066369?source=workspace"
)
MOTION_LOGIN_URL = "https://www.runninghub.ai/workflow/2066958157439651841"
MOTION_RUN_SELECTOR = (
    "#appVue > div.app-wrap.is-new-version > div > div.comfyUI-header "
    "> div.right-btn-wrap > div.execute-btn-wrap > div > button"
)
MOTION_OUTPUT_VIDEO_SELECTOR = (
    "#graph-canvas-container > div.isolate > div:nth-child(21) > div > div > video"
)
# Painel de resultado (novo layout do RunningHub): comeca escondido e
# precisa do clique no "hide-btn" pra abrir e revelar o video gerado.
MOTION_RESULT_HIDE_BTN_SELECTOR = (
    "#appVue > div.app-wrap.is-new-version > div > "
    "div.workflow-result-wrap-en.hide.workflow-result-wrap > div.hide-btn"
)
MOTION_RESULT_PANEL_VIDEO_SELECTOR = (
    "#appVue > div.app-wrap.is-new-version > div > "
    "div.workflow-result-wrap-en.workflow-result-wrap > div.list-wrap > div > "
    "div > div > div > div > div > div:nth-child(1) > div.history-video > "
    "div.rh-video-wrap > div > video"
)
# Fallback "frouxo": qualquer video dentro do painel de resultado aberto,
# sem depender da cadeia rigida de divs (que pode variar conforme o item
# selecionado/posicao na lista).
MOTION_RESULT_PANEL_VIDEO_FALLBACK_SELECTOR = (
    ".workflow-result-wrap-en.workflow-result-wrap "
    ".history-video video, "
    ".workflow-result-wrap-en.workflow-result-wrap "
    ".rh-video-wrap video, "
    ".workflow-result-wrap-en.workflow-result-wrap video"
)
# ── Remocao de marca d'agua (tarja preta) + exportacao 4K dos videos do
# Motion, aplicada depois do download (baseado em wmRunninghub.py) ──────────
MOTION_TARJA_ALTURA_PERCENTUAL = 0.03   # 3% da altura do video, no topo
MOTION_TARJA_CRF = "23"                 # 23=padrao ffmpeg, qualidade otima em 1080p (~2-4 Mbps)
MOTION_TARJA_PRESET = "veryfast"        # veryfast=rapido, qualidade identica ao veryfast do converter_celular
MOTION_TARJA_EXPORTAR_4K = True         # True=exporta em 4K vertical/horizontal compativel com celular
MOTION_TARJA_MANTER_PROPORCAO = True    # adiciona barras pretas em vez de distorcer
# Codec de audio final. AAC garante compatibilidade com celular (iOS/
# Android/Instagram/WhatsApp); copiar o audio original pode gerar
# arquivos que nao tocam em apps de celular se o audio de origem nao
# for AAC.
MOTION_TARJA_AUDIO_CODEC = "aac"
MOTION_TARJA_AUDIO_BITRATE = "192k"

# Exportacao final para celular/redes sociais (inspirado em convertermobile).
# 4K vertical = 2160x3840; horizontal = 3840x2160.
MOBILE_EXPORT_WIDTH = 2160
MOBILE_EXPORT_HEIGHT = 3840
MOBILE_VIDEO_PROFILE = "high"
MOBILE_VIDEO_LEVEL = "5.1"
MOBILE_VIDEO_CRF = "23"
MOBILE_VIDEO_PRESET = "veryfast"
MOBILE_IMAGE_QUALITY = 95
# Workflow novo (RunningHub) — nodes identificados pelo grafo do LiteGraph
# (window.graph), nao por seletor DOM, porque o node e' desenhado no canvas.
MOTION_NODE_TYPE_IMAGEM = "LoadImage"
MOTION_NODE_TYPE_VIDEO = "VHS_LoadVideo"
MOTION_WIDGET_IMAGEM = "image"
MOTION_WIDGET_VIDEO = "video"
MOTION_UPLOAD_IMAGE_ENDPOINT = "/upload/image"
MOTION_RELOAD_YAMLS_ENDPOINT = "/sum_text_list/reload_yamls"
COMFY_IFRAME_URL = "https://www.runninghub.ai/comfyUI.html"  # iframe onde o grafo LiteGraph vive
RH_TOKEN_FILE = ASSETS_DIR / "rh_token.json"      # cache do token Rh-Comfy-Auth (valido 7 dias)
RH_TOKEN_URL_FILE = ASSETS_DIR / "rh_token_url.txt"  # usuario cola a URL aqui quando token expira


PROMPT_FLOW = """System / Reference Task:
You have three input images.
— Image 1: Full-body reference photo of the target person (the one to be inserted).
— Image 2: Close-up face reference of the same target person.
— Image 3: The original scene photo to be edited, which contains overlaid UI elements, text boxes, and cropped screenshots placed on top of a person.
Your task:
Replace the person visible in Image 3 with the person from Images 1 and 2, preserving complete visual identity fidelity: exact face features, skin tone, hair style and color, body build, posture, and all corporeal traits.
The replacement person may wear clothing similar in style, color, and fit to what the original person in Image 3 is wearing, but must retain the body, face, hair, and physical characteristics from Images 1 and 2 exactly.
Critical constraints:
— All overlaid elements in Image 3 (text layers, cropped screenshots, UI boxes, banners) must remain fully intact, in their original position, size, and visual style. Do not remove, blur, move, or alter any overlay.
— The replaced person must fit naturally behind or under the overlays, matching the same depth, lighting, and shadow as the original scene.
— Preserve the background environment of Image 3 completely.
— Do not change the pose or camera angle unless absolutely necessary for a natural composite.
— Output a single final image that looks like a seamless, original photograph."""

# ─── PERSISTÊNCIA ─────────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── TOKEN RUNNINGHUB ──────────────────────────────────────────────────────────
def rh_token_carregar():
    """Carrega o token salvo e verifica se ainda e valido."""
    try:
        if RH_TOKEN_FILE.exists():
            dados = json.loads(RH_TOKEN_FILE.read_text(encoding="utf-8"))
            qs = dados.get("qs", "")
            expire = dados.get("signExpire", 0)
            if qs and expire > time.time() * 1000:
                return qs
    except Exception:
        pass
    return None

def rh_token_salvar(qs):
    """Salva a query string do token em arquivo."""
    try:
        import urllib.parse
        params = dict(urllib.parse.parse_qsl(qs))
        auth_b64 = params.get("Rh-Comfy-Auth", "")
        expire = 0
        if auth_b64:
            padding = "=" * (-len(auth_b64) % 4)
            decoded = json.loads(
                base64.b64decode(auth_b64 + padding).decode("utf-8")
            )
            expire = decoded.get("signExpire", 0)
        dados = {
            "qs": qs,
            "signExpire": expire,
            "savedAt": int(time.time() * 1000),
        }
        RH_TOKEN_FILE.write_text(
            json.dumps(dados, ensure_ascii=False),
            encoding="utf-8"
        )
        return dados
    except Exception:
        return None

def rh_token_info():
    try:
        if RH_TOKEN_FILE.exists():
            return json.loads(RH_TOKEN_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def rh_token_expiracao_texto(expire_ms):
    try:
        expire_ms = int(expire_ms or 0)
    except (TypeError, ValueError):
        expire_ms = 0
    if expire_ms <= 0:
        return "expiracao desconhecida"
    data = time.strftime(
        "%d/%m/%Y %H:%M:%S", time.localtime(expire_ms / 1000)
    )
    restante = (expire_ms / 1000) - time.time()
    if restante <= 0:
        return f"{data} (expirado)"
    dias = int(restante // 86400)
    horas = int((restante % 86400) // 3600)
    return f"{data} (faltam {dias}d {horas}h)"

def rh_token_pedir_arquivo():
    """Le a URL do arquivo rh_token_url.txt e extrai o token."""
    if not RH_TOKEN_URL_FILE.exists():
        raise RuntimeError(
            f"Token RunningHub nao encontrado ou expirado.\n\n"
            f"Como resolver:\n"
            f"1. Abra o workflow no RunningHub\n"
            f"2. Faca um upload manual (clique em 'choose video to upload')\n"
            f"3. Abra DevTools (F12) > aba Network\n"
            f"4. Clique na requisicao /upload/image\n"
            f"5. Copie a URL completa (com Rh-Comfy-Auth=...)\n"
            f"6. Cole em um arquivo de texto: {RH_TOKEN_URL_FILE}\n"
            f"7. Tente novamente."
        )
    url = RH_TOKEN_URL_FILE.read_text(encoding="utf-8").strip()
    if "Rh-Comfy-Auth=" not in url:
        raise RuntimeError(
            f"Conteudo de {RH_TOKEN_URL_FILE} invalido.\n"
            f"Cole a URL completa do upload (com Rh-Comfy-Auth=...)."
        )
    qs = url.split("?", 1)[1] if "?" in url else ""
    if qs:
        rh_token_salvar(qs)
        try:
            RH_TOKEN_URL_FILE.unlink()
        except Exception:
            pass
    return qs

def rh_token_obter(parent=None):
    """Retorna a query string com token valido, lendo do cache ou do arquivo txt."""
    qs = rh_token_carregar()
    if qs:
        return qs
    return rh_token_pedir_arquivo()

class MotionMcpClient:
    def __init__(self, log=None):
        self.log = log or (lambda msg: None)
        self.process = None
        self.responses = queue.Queue()
        self.next_id = 1

    def start(self, porta="9222"):
        comando = [
            "cmd", "/c", "npx", "-y", "chrome-devtools-mcp@latest",
            f"--browserUrl=http://localhost:{porta}",
            "--no-usage-statistics",
            "--no-performance-crux",
            "--no-category-performance",
            "--no-category-network",
            "--no-category-emulation",
        ]
        self.process = subprocess.Popen(
            comando,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        threading.Thread(
            target=self._read_stdout, daemon=True
        ).start()
        threading.Thread(
            target=self._read_stderr, daemon=True
        ).start()
        self.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "Mimic Motion", "version": "1.1"},
            },
            timeout=30
        )
        self._write({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        })

    def _read_stdout(self):
        for linha in self.process.stdout:
            try:
                mensagem = json.loads(linha)
                if "id" in mensagem:
                    self.responses.put(mensagem)
            except Exception:
                continue

    def _read_stderr(self):
        for linha in self.process.stderr:
            texto = linha.strip()
            if texto and not texto.startswith("chrome-devtools-mcp exposes"):
                self.log(f"MCP: {texto}")

    def _write(self, mensagem):
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("A ponte do Chrome foi encerrada.")
        self.process.stdin.write(
            json.dumps(mensagem, ensure_ascii=False) + "\n"
        )
        self.process.stdin.flush()

    def request(self, metodo, params, timeout=120):
        request_id = self.next_id
        self.next_id += 1
        self._write({
            "jsonrpc": "2.0",
            "id": request_id,
            "method": metodo,
            "params": params,
        })
        limite = time.monotonic() + timeout
        pendentes = []
        try:
            while time.monotonic() < limite:
                try:
                    resposta = self.responses.get(timeout=0.25)
                except queue.Empty:
                    if self.process.poll() is not None:
                        raise RuntimeError(
                            "A ponte do Chrome fechou inesperadamente."
                        )
                    continue
                if resposta.get("id") == request_id:
                    if "error" in resposta:
                        raise RuntimeError(str(resposta["error"]))
                    return resposta.get("result", {})
                pendentes.append(resposta)
        finally:
            for resposta in pendentes:
                self.responses.put(resposta)
        raise TimeoutError(
            "Tempo esgotado aguardando autorizacao/resposta do Chrome."
        )

    def tool(self, nome, argumentos=None, timeout=120):
        resultado = self.request(
            "tools/call",
            {"name": nome, "arguments": argumentos or {}},
            timeout=timeout
        )
        textos = [
            item.get("text", "")
            for item in resultado.get("content", [])
            if item.get("type") == "text"
        ]
        texto = "\n".join(textos)
        if resultado.get("isError"):
            raise RuntimeError(texto or f"Falha na ferramenta {nome}.")
        return texto

    def close(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

# ─── APLICAÇÃO PRINCIPAL ──────────────────────────────────────────────────────
class MotionHubApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Mostra qualquer exceção de callback (botões, binds, etc.) em vez de
        # deixar o Tkinter engoli-la silenciosamente (especialmente em .pyw,
        # que não tem console para stderr).
        self.report_callback_exception = self._report_callback_exception

        BASE_DIR.mkdir(parents=True, exist_ok=True)
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        READY_DIR.mkdir(parents=True, exist_ok=True)
        MOTION_DIR.mkdir(parents=True, exist_ok=True)

        self.config  = load_json(CONFIG_FILE, {
            "window_geometry": "1100x700",
            "last_tab": 0,
        })
        self.modelos = load_json(MODELS_FILE, {})
        self.prompts  = load_json(PROMPTS_FILE, {"Padrão": PROMPT_FLOW})

        self.title(APP_NAME)
        self._aplicar_icone_app()
        self.configure(bg="#050505")
        self.geometry(self.config.get("window_geometry", "1100x700"))
        self.minsize(800, 550)
        self._aplicar_barra_titulo_escura()
        self.after(250, self._aplicar_barra_titulo_escura)

        self.bind("<Configure>", self._on_configure)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._restore_state()

    def _on_configure(self, event):
        if event.widget == self:
            self.config["window_geometry"] = self.geometry()

    def _on_close(self):
        save_json(CONFIG_FILE, self.config)
        try:
            self._video_parar_player()
        except Exception:
            pass
        self.destroy()

    def _restore_state(self):
        try:
            self.notebook.select(self.config.get("last_tab", 0))
        except Exception:
            pass

    def _aplicar_icone_app(self):
        """Aplica a logo do Mimic na janela."""
        try:
            if sys.platform == "win32":
                try:
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Mimic.App")
                except Exception:
                    pass
                if MIMIC_ICON_FILE.exists():
                    try:
                        self.iconbitmap(default=str(MIMIC_ICON_FILE))
                    except Exception:
                        pass

            if MIMIC_LOGO_FILE.exists():
                if PIL_AVAILABLE:
                    icon = Image.open(MIMIC_LOGO_FILE).convert("RGBA")
                    icon.thumbnail((64, 64), Image.LANCZOS)
                    self._app_icon_img = ImageTk.PhotoImage(icon)
                else:
                    self._app_icon_img = tk.PhotoImage(file=str(MIMIC_LOGO_FILE))
            else:
                self._app_icon_img = tk.PhotoImage(data=SWAP_ICON_PNG_B64)
            self.iconphoto(True, self._app_icon_img)
        except Exception:
            self._app_icon_img = None

    def _aplicar_barra_titulo_escura(self):
        """Força a barra de título escura no Windows quando a API DWM permite."""
        if sys.platform != "win32":
            return
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id()) or self.winfo_id()
            valor = ctypes.c_int(1)
            for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE
                try:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, attr, ctypes.byref(valor), ctypes.sizeof(valor)
                    )
                except Exception:
                    pass

            preto = ctypes.c_int(0x000000)
            texto_lilas = ctypes.c_int(0xFC84C0)  # COLORREF de #c084fc
            for attr, cor in ((35, preto), (36, texto_lilas), (38, preto)):
                try:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, attr, ctypes.byref(cor), ctypes.sizeof(cor)
                    )
                except Exception:
                    pass

            cantos_arredondados = ctypes.c_int(2)  # DWMWCP_ROUND
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 33, ctypes.byref(cantos_arredondados),
                    ctypes.sizeof(cantos_arredondados)
                )
            except Exception:
                pass
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    # UI BASE
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        BG    = "#050505"
        BG2   = "#121212"
        BG3   = "#1f1f22"
        ACC   = "#3c096c"
        ACC2  = "#5a189a"
        ACC3  = "#240046"
        ACCFG = "#c084fc"
        FG    = "#f4f4f5"
        FG2   = "#a1a1aa"
        BORDER= "#2a2a2e"
        SHADOW= "#000000"
        WARN  = "#c084fc"
        ERR   = "#ef4444"
        OK    = "#22c55e"
        INFO  = "#38bdf8"

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=0,
            bordercolor=BG, lightcolor=BG, darkcolor=BG)
        style.configure("TNotebook.Tab", background=BG2, foreground=FG2,
            padding=[20, 10], font=("Segoe UI Semibold", 10),
            borderwidth=0, focuscolor=BG, bordercolor=BG,
            lightcolor=BG, darkcolor=BG)
        style.map("TNotebook.Tab",
            background=[("selected", ACC3), ("active", BG3)],
            foreground=[("selected", ACCFG), ("active", FG)])
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=BG2, relief="flat",
            borderwidth=1, bordercolor=BORDER, lightcolor="#1a1a1f",
            darkcolor=SHADOW)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TLabelframe", background=BG2, foreground=ACCFG,
            relief="flat", borderwidth=1, padding=16,
            bordercolor=BORDER, lightcolor=BORDER, darkcolor=SHADOW)
        style.configure("TLabelframe.Label", background=BG2, foreground=ACCFG,
            font=("Segoe UI Semibold", 10))
        style.configure("TButton", background=BG3, foreground=FG,
            relief="flat", borderwidth=1, padding=[14, 9],
            font=("Segoe UI", 10), bordercolor=BORDER, focuscolor=ACC3)
        style.map("TButton",
            background=[("active", "#2a2a30"), ("pressed", "#18181b")],
            bordercolor=[("active", ACC2)])
        style.configure("Accent.TButton", background=ACC, foreground=FG,
            relief="flat", borderwidth=1, padding=[15, 9],
            font=("Segoe UI Semibold", 10), bordercolor=ACC2, focuscolor=ACC2)
        style.map("Accent.TButton",
            background=[("active", ACC2), ("pressed", ACC3)],
            foreground=[("active", FG), ("pressed", FG)])
        style.configure("TEntry", fieldbackground=BG3, foreground=FG,
            insertbackground=ACC2, relief="flat", borderwidth=1, padding=7,
            bordercolor=BORDER, lightcolor=BORDER, darkcolor=SHADOW)
        style.configure("TCombobox", fieldbackground=BG3, background=BG3,
            foreground=FG, arrowcolor=FG2, bordercolor=BORDER,
            lightcolor=BORDER, darkcolor=SHADOW, padding=5)
        style.map("TCombobox",
            fieldbackground=[("readonly", BG3)],
            selectbackground=[("readonly", ACC3)],
            selectforeground=[("readonly", FG)])
        for scrollbar_style in ("TScrollbar", "Vertical.TScrollbar", "Horizontal.TScrollbar"):
            style.configure(scrollbar_style,
                background=ACC,
                troughcolor="#0b0b0d",
                arrowcolor="#0b0b0d",
                bordercolor="#0b0b0d",
                darkcolor="#0b0b0d",
                lightcolor="#0b0b0d",
                relief="flat",
                borderwidth=0,
                arrowsize=0,
                width=12
            )
            style.map(scrollbar_style,
                background=[("active", ACC2), ("pressed", ACC3)],
                troughcolor=[("active", "#0b0b0d")]
            )
        try:
            style.layout("Vertical.TScrollbar", [
                ("Vertical.Scrollbar.trough", {
                    "sticky": "ns",
                    "children": [
                        ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                    ]
                })
            ])
            style.layout("Horizontal.TScrollbar", [
                ("Horizontal.Scrollbar.trough", {
                    "sticky": "we",
                    "children": [
                        ("Horizontal.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                    ]
                })
            ])
        except Exception:
            pass
        style.configure("TCheckbutton", background=BG2, foreground=FG,
            font=("Segoe UI", 10), focuscolor=ACC3,
            indicatorcolor=BG3, indicatorbackground=BG3,
            indicatormargin=3)
        style.map("TCheckbutton",
            background=[("active", BG3)],
            foreground=[("active", FG)],
            indicatorcolor=[("selected", ACCFG), ("active", ACC2), ("!selected", BG3)])

        self._instalar_tema_arredondado(style, {
            "BG": BG, "BG2": BG2, "BG3": BG3, "ACC": ACC, "ACC2": ACC2,
            "ACC3": ACC3, "ACCFG": ACCFG, "FG": FG, "FG2": FG2,
            "BORDER": BORDER, "SHADOW": SHADOW
        })

        self.colors = dict(
            BG=BG, BG2=BG2, BG3=BG3, ACC=ACC, ACC2=ACC2, ACC3=ACC3, ACCFG=ACCFG,
            FG=FG, FG2=FG2, BORDER=BORDER, SHADOW=SHADOW,
            WARN=WARN, ERR=ERR, OK=OK, INFO=INFO
        )

        # Header
        header = tk.Frame(self, bg=BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        try:
            if MIMIC_LOGO_FILE.exists() and PIL_AVAILABLE:
                header_logo = Image.open(MIMIC_LOGO_FILE).convert("RGBA")
                header_logo.thumbnail((54, 54), Image.LANCZOS)
                self._header_icon_img = ImageTk.PhotoImage(header_logo)
            elif getattr(self, "_app_icon_img", None):
                self._header_icon_img = self._app_icon_img.subsample(6, 6)
            else:
                self._header_icon_img = None
            if self._header_icon_img:
                tk.Label(header, image=self._header_icon_img, bg=BG).pack(side="left", padx=(24, 10), pady=6)
        except Exception:
            pass
        tk.Label(header, text=APP_NAME, bg=BG, fg=ACCFG,
                 font=("Segoe UI Black", 20, "bold")).pack(side="left", padx=(0, 0), pady=12)
        tk.Frame(self, bg=BG, height=2).pack(fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.notebook.bind("<<NotebookTabChanged>>",
            lambda e: self.config.update({"last_tab": self.notebook.index("current")}))

        self._build_tab_video()
        self._build_tab_fotos()
        self._build_tab_revisao()
        self._build_tab_videos()
        self._build_tab_motion()
        self._build_tab_configuracao()
        self._build_tab_log()

    # ══════════════════════════════════════════════════════════════════════════
    # HELPERS DE UI / MIDIA
    # ══════════════════════════════════════════════════════════════════════════
    def _rounded_photo(self, width, height, radius, fill, outline=None, shadow=False):
        if not PIL_AVAILABLE:
            return None
        scale = 3
        w, h, r = width * scale, height * scale, radius * scale
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if shadow:
            shadow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            shadow_draw.rounded_rectangle(
                (2 * scale, 3 * scale, w - 2 * scale, h - scale),
                radius=r, fill=(0, 0, 0, 95)
            )
            img.alpha_composite(shadow_img)
        draw = ImageDraw.Draw(img)
        inset = 1 * scale
        draw.rounded_rectangle(
            (inset, inset, w - inset, h - inset),
            radius=r, fill=fill, outline=outline, width=max(1, scale)
        )
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
        img = img.resize((width, height), resample)
        return ImageTk.PhotoImage(img)

    def _check_photo(self, selected, colors):
        if not PIL_AVAILABLE:
            return None
        scale = 4
        size = 18
        img = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        box = (2 * scale, 2 * scale, (size - 2) * scale, (size - 2) * scale)
        fill = colors["ACC"] if selected else colors["BG3"]
        outline = colors["ACCFG"] if selected else colors["BORDER"]
        draw.rounded_rectangle(box, radius=5 * scale, fill=fill, outline=outline, width=2 * scale)
        if selected:
            pts = [
                (5 * scale, 9 * scale),
                (8 * scale, 12 * scale),
                (13 * scale, 6 * scale),
            ]
            draw.line(pts, fill=colors["FG"], width=2 * scale, joint="curve")
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
        img = img.resize((size, size), resample)
        return ImageTk.PhotoImage(img)

    def _instalar_tema_arredondado(self, style, colors):
        if not PIL_AVAILABLE:
            return
        try:
            self._theme_images = getattr(self, "_theme_images", {})
            imgs = self._theme_images
            specs = {
                "btn": (120, 34, 13, colors["BG3"], colors["BORDER"], True),
                "btn_hover": (120, 34, 13, "#2a2a30", colors["ACC2"], True),
                "btn_press": (120, 34, 13, "#18181b", colors["ACC"], True),
                "accent": (128, 36, 14, colors["ACC"], colors["ACC2"], True),
                "accent_hover": (128, 36, 14, colors["ACC2"], colors["ACCFG"], True),
                "accent_press": (128, 36, 14, colors["ACC3"], colors["ACC2"], True),
                "field": (120, 30, 12, colors["BG3"], colors["BORDER"], False),
                "panel": (180, 80, 18, colors["BG2"], colors["BORDER"], True),
                "notebook_client": (180, 80, 1, colors["BG"], colors["BG"], False),
                "tab": (112, 40, 14, colors["BG2"], colors["BG"], False),
                "tab_active": (112, 40, 14, "#1c1c20", colors["ACC3"], False),
                "tab_selected": (112, 40, 14, colors["ACC3"], colors["ACC2"], False),
            }
            for name, args in specs.items():
                imgs[name] = self._rounded_photo(*args)
            imgs["check_off"] = self._check_photo(False, colors)
            imgs["check_on"] = self._check_photo(True, colors)

            style.element_create(
                "RoundedButton.border", "image", imgs["btn"],
                ("pressed", imgs["btn_press"]), ("active", imgs["btn_hover"]),
                border=14, padding=8, sticky="nsew"
            )
            style.layout("TButton", [
                ("RoundedButton.border", {"sticky": "nsew", "children": [
                    ("Button.focus", {"sticky": "nsew", "children": [
                        ("Button.padding", {"sticky": "nsew", "children": [
                            ("Button.label", {"sticky": "nsew"})
                        ]})
                    ]})
                ]})
            ])

            style.element_create(
                "AccentRoundedButton.border", "image", imgs["accent"],
                ("pressed", imgs["accent_press"]), ("active", imgs["accent_hover"]),
                border=14, padding=8, sticky="nsew"
            )
            style.layout("Accent.TButton", [
                ("AccentRoundedButton.border", {"sticky": "nsew", "children": [
                    ("Button.focus", {"sticky": "nsew", "children": [
                        ("Button.padding", {"sticky": "nsew", "children": [
                            ("Button.label", {"sticky": "nsew"})
                        ]})
                    ]})
                ]})
            ])

            style.element_create("RoundedEntry.field", "image", imgs["field"], border=12, sticky="nsew")
            style.layout("TEntry", [
                ("RoundedEntry.field", {"sticky": "nsew", "children": [
                    ("Entry.padding", {"sticky": "nsew", "children": [
                        ("Entry.textarea", {"sticky": "nsew"})
                    ]})
                ]})
            ])

            style.element_create(
                "RoundedCheck.indicator", "image", imgs["check_off"],
                ("selected", imgs["check_on"]), sticky=""
            )
            style.layout("TCheckbutton", [
                ("Checkbutton.padding", {"sticky": "nswe", "children": [
                    ("RoundedCheck.indicator", {"side": "left", "sticky": ""}),
                    ("Checkbutton.focus", {"side": "left", "sticky": "w", "children": [
                        ("Checkbutton.label", {"sticky": "w"})
                    ]})
                ]})
            ])
            style.element_create("RoundedLabelframe.border", "image", imgs["panel"], border=18, padding=12, sticky="nsew")
            style.layout("TLabelframe", [
                ("RoundedLabelframe.border", {"sticky": "nsew"})
            ])

            style.element_create(
                "RoundedNotebook.tab", "image", imgs["tab"],
                ("selected", imgs["tab_selected"]), ("active", imgs["tab_active"]),
                border=14, padding=8, sticky="nsew"
            )
            style.element_create(
                "FlatNotebook.client", "image", imgs["notebook_client"],
                border=1, padding=0, sticky="nsew"
            )
            style.layout("TNotebook", [
                ("FlatNotebook.client", {"sticky": "nswe"})
            ])
            style.layout("TNotebook.Tab", [
                ("RoundedNotebook.tab", {"sticky": "nsew", "children": [
                    ("Notebook.padding", {"side": "top", "sticky": "nsew", "children": [
                        ("Notebook.label", {"side": "top", "sticky": ""})
                    ]})
                ]})
            ])
        except Exception:
            pass

    def _mousewheel_delta(self, event):
        if getattr(event, "num", None) == 4:
            return -1
        if getattr(event, "num", None) == 5:
            return 1
        delta = getattr(event, "delta", 0)
        if delta == 0:
            return 0
        return -1 if delta > 0 else 1

    def _bind_widget_mousewheel_to_canvas(self, widget, canvas):
        """Faz o scroll do mouse funcionar mesmo em cima de labels/checkboxes."""
        def _on_mousewheel(event, c=canvas):
            passo = self._mousewheel_delta(event)
            if passo:
                c.yview_scroll(passo, "units")
            return "break"
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                widget.bind(seq, _on_mousewheel, add="+")
            except Exception:
                pass

    def _bind_canvas_mousewheel(self, canvas, inner=None):
        self._bind_widget_mousewheel_to_canvas(canvas, canvas)
        if inner is not None:
            self._bind_widget_mousewheel_to_canvas(inner, canvas)

    def _bind_mousewheel_recursive(self, widget, canvas):
        skip = (tk.Text, tk.Listbox, tk.Canvas, tk.Entry, ttk.Entry, ttk.Combobox)
        if not isinstance(widget, skip):
            self._bind_widget_mousewheel_to_canvas(widget, canvas)
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child, canvas)

    def _visible_checkbutton(self, parent, variable, command=None, bg=None, text="", font=None):
        return ttk.Checkbutton(parent, text=text, variable=variable, command=command)

    def _profile_marker_text(self, ativo):
        return "☑" if ativo else "☐"

    def _profile_marker_fg(self, ativo):
        return self.colors["ACCFG"] if ativo else self.colors["FG2"]

    def _mobile_target_size(self, largura, altura):
        """Retorna 4K vertical/horizontal mantendo orientacao do arquivo."""
        try:
            largura = int(largura)
            altura = int(altura)
        except Exception:
            largura, altura = MOBILE_EXPORT_WIDTH, MOBILE_EXPORT_HEIGHT
        if largura <= altura:
            return MOBILE_EXPORT_WIDTH, MOBILE_EXPORT_HEIGHT
        return MOBILE_EXPORT_HEIGHT, MOBILE_EXPORT_WIDTH

    def _mobile_filter(self, largura, altura, tarja_preta=False):
        alvo_w, alvo_h = self._mobile_target_size(largura, altura)
        filtros = []
        if tarja_preta:
            filtros.append(
                f"drawbox=x=0:y=0:w=iw:h=ih*{MOTION_TARJA_ALTURA_PERCENTUAL}:color=black:t=fill"
            )
        filtros.extend([
            f"scale={alvo_w}:{alvo_h}:force_original_aspect_ratio=decrease",
            f"pad={alvo_w}:{alvo_h}:(ow-iw)/2:(oh-ih)/2:color=black",
            "setsar=1",
            "format=yuv420p",
        ])
        return ",".join(filtros)

    def _converter_foto_celular(self, caminho):
        """Converte imagem gerada para JPG 4K com bordas pretas, sem metadados."""
        caminho = Path(caminho)
        if not caminho.exists() or not caminho.is_file():
            return caminho
        if not PIL_AVAILABLE:
            self._log("    ⚠ PIL/Pillow indisponivel; foto mantida sem conversao 4K.")
            return caminho
        destino = caminho if caminho.suffix.lower() in {".jpg", ".jpeg"} else caminho.with_suffix(".jpg")
        temp = destino.with_name(f"{destino.stem}.__TEMP_CELULAR__.jpg")
        try:
            with Image.open(caminho) as img:
                img = ImageOps.exif_transpose(img)
                largura, altura = img.size
                alvo_w, alvo_h = self._mobile_target_size(largura, altura)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                if img.mode == "RGBA":
                    base = Image.new("RGB", img.size, (0, 0, 0))
                    base.paste(img, mask=img.getchannel("A"))
                    img = base
                else:
                    img = img.convert("RGB")
                escala = min(alvo_w / max(1, largura), alvo_h / max(1, altura))
                novo_w = max(1, int(largura * escala))
                novo_h = max(1, int(altura * escala))
                img = img.resize((novo_w, novo_h), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (alvo_w, alvo_h), (0, 0, 0))
                canvas.paste(img, ((alvo_w - novo_w) // 2, (alvo_h - novo_h) // 2))
                canvas.save(temp, "JPEG", quality=MOBILE_IMAGE_QUALITY, optimize=True, subsampling=0)
            os.replace(temp, destino)
            if destino != caminho and caminho.exists():
                try:
                    caminho.unlink()
                except Exception:
                    pass
            self._log(f"    ✓ Foto convertida para celular 4K: {destino.name}")
            return destino
        except Exception as exc:
            try:
                if temp.exists():
                    temp.unlink()
            except Exception:
                pass
            self._log(f"    ⚠ Falha ao converter foto para celular: {exc}. Original mantido.")
            return caminho

    def _converter_video_celular(self, caminho, tarja_preta=False):
        """Converte video para MP4 H.264/AAC 4K com padding preto; opcional tarja no topo."""
        caminho = Path(caminho)
        if not caminho.exists() or not caminho.is_file():
            return caminho
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if not ffmpeg or not ffprobe:
            self._log("Motion: ffmpeg/ffprobe nao encontrados; video mantido sem conversao 4K.")
            return caminho
        temp = caminho.with_name(f"{caminho.stem}.__TEMP_CELULAR__.mp4")
        try:
            largura, altura = self._motion_ffmpeg_info_video(ffprobe, caminho)
            filtro = self._mobile_filter(largura, altura, tarja_preta=tarja_preta)
            comando = [
                ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(caminho),
                "-map", "0:v:0", "-map", "0:a?",
                "-vf", filtro,
                "-c:v", "libx264",
                "-profile:v", MOBILE_VIDEO_PROFILE,
                "-level", MOBILE_VIDEO_LEVEL,
                "-preset", MOBILE_VIDEO_PRESET,
                "-crf", MOBILE_VIDEO_CRF,
                "-pix_fmt", "yuv420p",
                "-c:a", MOTION_TARJA_AUDIO_CODEC,
                "-b:a", MOTION_TARJA_AUDIO_BITRATE,
                "-movflags", "+faststart",
                "-map_metadata", "-1",
                str(temp),
            ]
            processo = subprocess.run(
                comando, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if processo.returncode != 0:
                detalhe = (processo.stderr or processo.stdout or "").strip()
                raise RuntimeError(detalhe[-1200:] or "ffmpeg retornou erro sem detalhe")
            if not self._motion_ffmpeg_validar(ffprobe, temp):
                raise RuntimeError("arquivo temporario convertido ficou invalido")
            os.replace(temp, caminho)
            self._log(
                f"Motion: video convertido para celular 4K"
                f"{' com tarja preta' if tarja_preta else ''}: {caminho}"
            )
            return caminho
        except Exception as exc:
            try:
                if temp.exists():
                    temp.unlink()
            except Exception:
                pass
            self._log(f"Motion: falha na conversao 4K ({exc}). Video original mantido.")
            return caminho

    # ══════════════════════════════════════════════════════════════════════════
    # TAB CONFIGURAÇÃO — embeds Modelos + Seletores as sub-tabs
    # (built via _build_tab_configuracao; this stub remains for compat)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_tab_modelos(self):
        """Stub — modelos agora ficam em Configuração > Modelos."""
        pass

    def _build_form_vazio(self):
        C = self.colors
        for w in self.form_frame.winfo_children(): w.destroy()
        tk.Label(self.form_frame, text="Selecione ou crie uma modelo",
                 bg=C["BG"], fg=C["FG2"], font=("Segoe UI", 13)).pack(expand=True)

    def _build_form_modelo(self, nome_key=None):
        C = self.colors
        for w in self.form_frame.winfo_children(): w.destroy()

        is_new = nome_key is None
        dados  = self.modelos.get(nome_key, {}) if not is_new else {}

        tk.Label(self.form_frame, text="Nome da Modelo",
                 bg=C["BG"], fg=C["FG2"], font=("Segoe UI", 9)).pack(anchor="w")
        nome_var = tk.StringVar(value=dados.get("nome", ""))
        nome_entry = ttk.Entry(self.form_frame, textvariable=nome_var, font=("Segoe UI", 13))
        nome_entry.pack(fill="x", pady=(2, 16))
        if is_new: nome_entry.focus()

        fotos_frame = ttk.LabelFrame(self.form_frame, text="Fotos de Referência")
        fotos_frame.pack(fill="x", pady=(0, 16))

        self._foto_vars   = {}
        self._foto_labels = {}

        for i in range(1, 3):
            row = tk.Frame(fotos_frame, bg=C["BG2"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"Foto {i}", bg=C["BG2"], fg=C["ACCFG"],
                     font=("Segoe UI Semibold", 10), width=7).pack(side="left")

            foto_path = dados.get(f"foto{i}", "")
            pvar = tk.StringVar(value=foto_path)
            self._foto_vars[i] = pvar

            ttk.Entry(row, textvariable=pvar, font=("Segoe UI", 9)
                      ).pack(side="left", fill="x", expand=True, padx=(4, 4))

            def _browse(idx=i, v=pvar):
                p = filedialog.askopenfilename(
                    title=f"Selecionar Foto {idx}",
                    filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp *.bmp"), ("Todos", "*.*")])
                if p: v.set(p)

            ttk.Button(row, text="Procurar", command=_browse).pack(side="left")

            thumb = tk.Label(row, bg=C["BG2"], width=8, height=4,
                             text="[sem foto]", fg=C["FG2"], font=("Segoe UI", 7))
            thumb.pack(side="left", padx=(6, 0))
            self._foto_labels[i] = thumb
            if foto_path and PIL_AVAILABLE:
                self._update_thumb(thumb, foto_path)
            pvar.trace_add("write", lambda *a, t=thumb, v=pvar: self._update_thumb(t, v.get()))

        def _salvar():
            nome = nome_var.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Informe o nome da modelo.")
                return
            fotos = {f"foto{i}": self._foto_vars[i].get().strip() for i in range(1, 3)}
            if not is_new and nome_key != nome:
                del self.modelos[nome_key]
            self.modelos[nome] = {"nome": nome, **fotos}
            save_json(MODELS_FILE, self.modelos)
            self._reload_lista_modelos()
            # Atualiza o checklist de modelos na aba Fotos
            if hasattr(self, "_fotos_modelos_inner"):
                self._fotos_rebuild_modelos_checklist()
            # Atualiza o checklist de modelos na aba Flow
            if hasattr(self, "_flow_modelos_inner"):
                self._flow_rebuild_modelos_checklist()
            idx = list(self.modelos.keys()).index(nome)
            self.modelo_listbox.selection_clear(0, "end")
            self.modelo_listbox.selection_set(idx)
            self.modelo_listbox.see(idx)
            messagebox.showinfo("Salvo", f"Modelo '{nome}' salva!")

        ttk.Button(self.form_frame, text="Salvar Modelo",
                   style="Accent.TButton", command=_salvar).pack(anchor="e")

    def _update_thumb(self, label, path):
        if not PIL_AVAILABLE or not path or not os.path.isfile(path):
            label.configure(image="", text="[sem foto]"); return
        try:
            img = Image.open(path); img.thumbnail((56, 56))
            photo = ImageTk.PhotoImage(img)
            label.configure(image=photo, text=""); label.image = photo
        except Exception:
            label.configure(image="", text="[erro]")

    def _reload_lista_modelos(self):
        self.modelo_listbox.delete(0, "end")
        for nome in self.modelos:
            self.modelo_listbox.insert("end", f"  {nome}")

    def _on_modelo_select(self, event):
        sel = self.modelo_listbox.curselection()
        if not sel: return
        nome = list(self.modelos.keys())[sel[0]]
        self._build_form_modelo(nome)

    def _novo_modelo(self):
        self.modelo_listbox.selection_clear(0, "end")
        self._build_form_modelo(None)

    def _excluir_modelo(self):
        sel = self.modelo_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma modelo para excluir."); return
        nome = list(self.modelos.keys())[sel[0]]
        if messagebox.askyesno("Confirmar", f"Excluir modelo '{nome}'?"):
            del self.modelos[nome]
            save_json(MODELS_FILE, self.modelos)
            self._reload_lista_modelos()
            if hasattr(self, "_fotos_modelos_inner"):
                self._fotos_rebuild_modelos_checklist()
            if hasattr(self, "_flow_modelos_inner"):
                self._flow_rebuild_modelos_checklist()
            self._build_form_vazio()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB — VÍDEO  (Frames + Flow unificados)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_tab_automacao(self):
        """Stub — conteúdo migrado para _build_tab_video."""
        pass

    def _build_tab_flow(self):
        """Stub — conteúdo migrado para _build_tab_video."""
        pass

    def _build_tab_video(self):
        C = self.colors
        frame = tk.Frame(self.notebook, bg=C["BG"])
        self._tab_video_frame = frame
        self.notebook.add(frame, text="  Vídeo  ")

        # ── Variáveis e stubs de compatibilidade ──────────────────────────────
        # Inicializar ANTES de qualquer widget para evitar AttributeError no Python 3.14+
        self._frames_modelos_vars   = {}
        self._frames_modelos_canvas = None  # será substituído abaixo
        self._frames_modelos_inner  = None
        self._flow_modelos_vars     = {}

        self.prompts = load_json(PROMPTS_FILE, {"Padrão": PROMPT_FLOW})
        self.auto_modo_var       = tk.StringVar(value="modelo")
        self.config["auto_modo"] = "modelo"
        self.auto_pasta_refs_var = tk.StringVar(value=self.config.get("auto_pasta_refs", ""))
        self.opt_copiar_video    = tk.BooleanVar(value=True)
        self.opt_chrome_port     = tk.StringVar(value=self.config.get("chrome_port", "9222"))
        self.opt_chrome_port.trace_add("write",
            lambda *a: self.config.update({"chrome_port": self.opt_chrome_port.get()}))

        video_canvas = tk.Canvas(frame, bg=C["BG"], highlightthickness=0, borderwidth=0)
        video_scrollbar = ttk.Scrollbar(frame, orient="vertical", style="Vertical.TScrollbar", command=video_canvas.yview)
        video_canvas.configure(yscrollcommand=video_scrollbar.set)
        video_canvas.pack(side="left", fill="both", expand=True)
        video_scrollbar.pack(side="right", fill="y")

        video_inner = tk.Frame(video_canvas, bg=C["BG"])
        video_inner_window = video_canvas.create_window((0, 0), window=video_inner, anchor="nw")

        def _video_inner_configure(_event=None):
            video_canvas.configure(scrollregion=video_canvas.bbox("all"))

        def _video_canvas_configure(event):
            video_canvas.itemconfigure(video_inner_window, width=event.width)

        video_inner.bind("<Configure>", _video_inner_configure)
        video_canvas.bind("<Configure>", _video_canvas_configure)
        self._bind_canvas_mousewheel(video_canvas, video_inner)
        self._video_tab_canvas = video_canvas

        # ── Layout: blocos verticais — Criar frames + Enviar para Flow ──
        body = tk.Frame(video_inner, bg=C["BG"])
        body.pack(fill="both", expand=True, padx=14, pady=(10, 20))

        # Bloco superior — Modelos + vídeos + botão Criar Frames
        col_a = ttk.LabelFrame(body, text="Criar frames")
        col_a.pack(fill="x", pady=(0, 22))
        col_a.columnconfigure(0, weight=1, uniform="frames_top")
        col_a.columnconfigure(1, weight=1, uniform="frames_top")
        col_a.rowconfigure(0, weight=1)

        # Separação entre criação de frames e envio para Flow
        sep = tk.Frame(body, bg=C["BORDER"], height=1)
        sep.pack(fill="x", pady=(0, 18))

        bottom = ttk.LabelFrame(body, text="Enviar para Flow")
        bottom.pack(fill="both", expand=True)

        flow_top = tk.Frame(bottom, bg=C["BG2"])
        flow_top.pack(fill="x", pady=(0, 12))
        flow_top.columnconfigure(0, weight=1, uniform="flow_top")
        flow_top.columnconfigure(1, weight=1, uniform="flow_top")
        flow_top.rowconfigure(0, weight=1)

        # Coluna C — Perfis Flow + Timers (esquerda)
        col_c = tk.Frame(flow_top, bg=C["BG2"])
        col_c.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Coluna B — Pastas de trabalho do Flow (direita)
        col_b = ttk.LabelFrame(flow_top, text="Pastas em assets/work")
        col_b.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # ══ COLUNA A (topo) — Modelos à esquerda, Vídeos+botão à direita ════════

        # Lado esquerdo da col_a: Modelos
        col_a_left = tk.Frame(col_a, bg=C["BG2"])
        col_a_left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Lado direito da col_a: Vídeos + botão Criar Frames
        col_a_right = tk.Frame(col_a, bg=C["BG2"])
        col_a_right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # --- Modelos ---
        mod_hdr = tk.Frame(col_a_left, bg=C["BG2"])
        mod_hdr.pack(fill="x", pady=(0, 2))
        tk.Label(mod_hdr, text="Modelos", bg=C["BG2"], fg=C["FG2"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        mod_btns = tk.Frame(col_a_left, bg=C["BG2"])
        mod_btns.pack(fill="x", pady=(0, 6))
        ttk.Button(mod_btns, text="Todas",
                   command=self._frames_modelos_marcar_todas).pack(side="left", padx=(0, 3))
        ttk.Button(mod_btns, text="Limpar",
                   command=self._frames_modelos_desmarcar_todas).pack(side="left", padx=(0, 3))
        ttk.Button(mod_btns, text="↻",
                   command=self._frames_rebuild_modelos_checklist).pack(side="left")

        mf_wrap = tk.Frame(col_a_left, bg=C["BG2"])
        mf_wrap.pack(fill="both", expand=True)
        mf_canvas = tk.Canvas(mf_wrap, bg=C["BG2"], highlightthickness=0, height=248)
        mf_sb = ttk.Scrollbar(mf_wrap, orient="vertical", style="Vertical.TScrollbar", command=mf_canvas.yview)
        mf_canvas.configure(yscrollcommand=mf_sb.set)
        mf_sb.pack(side="right", fill="y")
        mf_canvas.pack(side="left", fill="both", expand=True)
        self._frames_modelos_inner = tk.Frame(mf_canvas, bg=C["BG2"])
        mf_win = mf_canvas.create_window((0, 0), window=self._frames_modelos_inner, anchor="nw")
        def _on_mf_c(e): mf_canvas.configure(scrollregion=mf_canvas.bbox("all"))
        def _on_mf_w(e): mf_canvas.itemconfig(mf_win, width=e.width)
        self._frames_modelos_inner.bind("<Configure>", _on_mf_c)
        mf_canvas.bind("<Configure>", _on_mf_w)
        self._bind_canvas_mousewheel(mf_canvas, self._frames_modelos_inner)
        self._frames_modelos_canvas = mf_canvas

        # Stubs de compat
        self.auto_modelo_frame = tk.Frame(col_a_left, bg=C["BG2"])
        self.auto_pasta_frame  = tk.Frame(col_a_left, bg=C["BG2"])
        self._flow_modelos_inner  = tk.Frame(col_b, bg=C["BG2"])
        self._flow_modelos_canvas = tk.Canvas(col_b, width=0, height=0, highlightthickness=0)

        # --- Vídeos ---
        vid_hdr = tk.Frame(col_a_right, bg=C["BG2"])
        vid_hdr.pack(fill="x", pady=(0, 2))
        tk.Label(vid_hdr, text="Vídeos em • VídeosOg", bg=C["BG2"], fg=C["FG2"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        vid_btns = tk.Frame(col_a_right, bg=C["BG2"])
        vid_btns.pack(fill="x", pady=(0, 6))
        ttk.Button(vid_btns, text="↻ Listar",
                   command=self._listar_videos).pack(side="left")
        vid_wrap = tk.Frame(col_a_right, bg=C["BG2"])
        vid_wrap.pack(fill="both", expand=True)
        vs = ttk.Scrollbar(vid_wrap, style="Vertical.TScrollbar"); vs.pack(side="right", fill="y")
        self.videos_listbox = tk.Listbox(vid_wrap, bg=C["BG3"], fg=C["FG"],
            selectbackground=C["ACC"], selectforeground=C["FG"],
            font=("Consolas", 9), relief="flat", borderwidth=0,
            highlightthickness=0, yscrollcommand=vs.set,
            selectmode="extended", activestyle="none", height=12)
        self.videos_listbox.pack(fill="both", expand=True)
        vs.config(command=self.videos_listbox.yview)

        # Botão criar frames fica na base da col_a_right
        ttk.Button(col_a_right, text="🎬  Criar frames", style="Accent.TButton",
                   command=self._criar_frames_thread).pack(fill="x", pady=(6, 0))

        # ══ COLUNA B ══════════════════════════════════════════════════════════

        # --- Pastas de trabalho ---
        pf_btns = tk.Frame(col_b, bg=C["BG2"])
        pf_btns.pack(fill="x", pady=(0, 6))
        ttk.Button(pf_btns, text="Limpar",
                   command=self._limpar_pastas_work).pack(side="left", padx=(0, 3))
        ttk.Button(pf_btns, text="↻",
                   command=self._atualizar_pastas_flow).pack(side="left")

        pf_wrap = tk.Frame(col_b, bg=C["BG2"])
        pf_wrap.pack(fill="both", expand=True)
        ps = ttk.Scrollbar(pf_wrap, style="Vertical.TScrollbar"); ps.pack(side="right", fill="y")
        self.pastas_listbox = tk.Listbox(pf_wrap, bg=C["BG3"], fg=C["FG"],
            selectbackground=C["ACC"], selectforeground=C["FG"],
            font=("Consolas", 9), relief="flat", borderwidth=0,
            highlightthickness=0, yscrollcommand=ps.set,
            selectmode="extended", activestyle="none")
        self.pastas_listbox.pack(fill="both", expand=True)
        ps.config(command=self.pastas_listbox.yview)
        self.pastas_listbox.bind("<Button-1>", lambda _e: "break")

        # ── Referências (info compacta) ──
        ref_info = tk.Label(col_b,
            text="ref1 + ref2 → Uploads uma vez  •  frameog = 3ª imagem",
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 7), justify="left")
        ref_info.pack(anchor="w", pady=(4, 0))

        # Botão enviar flow na base da col_b
        tk.Label(col_b,
            text="Faça login em cada sessão se necessário.",
            bg=C["BG2"], fg=C["WARN"], font=("Segoe UI", 7)).pack(anchor="w", pady=(3, 2))
        ttk.Button(col_b, text="▶  Enviar", style="Accent.TButton",
                   command=self._enviar_flow_thread).pack(fill="x")

        # ══ COLUNA C ══════════════════════════════════════════════════════════

        # --- Perfis Flow ---
        profiles = ttk.LabelFrame(col_c, text="Perfis Flow")
        profiles.pack(fill="x", pady=(0, 6))
        profiles_body = tk.Frame(profiles, bg=C["BG2"])
        profiles_body.pack(fill="x")

        self.flow_profiles_checks_frame = tk.Frame(profiles_body, bg=C["BG2"])
        self.flow_profiles_checks_frame.pack_forget()

        # Editor inline de perfil acima da lista.
        editor = tk.Frame(profiles_body, bg=C["BG2"])
        editor.pack(fill="x", pady=(0, 6))
        self.flow_profile_active_var = tk.BooleanVar(value=True)
        tk.Label(editor, text="Nome:", bg=C["BG2"], fg=C["FG"],
                 font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", padx=(0, 4), pady=(0, 3))
        self.flow_profile_name_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.flow_profile_name_var, width=12
            ).grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(0, 3))
        tk.Label(editor, text="Porta:", bg=C["BG2"], fg=C["FG"],
                 font=("Segoe UI", 8)).grid(row=0, column=2, sticky="w", padx=(0, 4), pady=(0, 3))
        self.flow_profile_port_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.flow_profile_port_var, width=7
            ).grid(row=0, column=3, sticky="w", pady=(0, 3))
        tk.Label(editor, text="Projeto:", bg=C["BG2"], fg=C["FG"],
                 font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w", padx=(0, 4))
        self.flow_profile_url_var = tk.StringVar()
        ttk.Entry(editor, textvariable=self.flow_profile_url_var
            ).grid(row=1, column=1, columnspan=3, sticky="ew")
        editor.columnconfigure(1, weight=1)

        profile_buttons = tk.Frame(profiles, bg=C["BG2"])
        profile_buttons.pack(fill="x", pady=(4, 0))
        for txt, cmd in [
            ("Novo",    self._flow_profile_novo),
            ("Salvar",  self._flow_profile_salvar),
            ("Excluir", self._flow_profile_excluir),
            ("Abrir sel.", self._abrir_chrome_debug),
            ("Abrir ativos", self._flow_abrir_perfis_ativos),
        ]:
            ttk.Button(profile_buttons, text=txt, command=cmd).pack(side="left", padx=(0, 3))

        flow_list_wrap = tk.Frame(profiles_body, bg=C["BG3"], relief="flat", bd=0)
        flow_list_wrap.pack(fill="both", expand=True)
        self._flow_profiles_list_frame = tk.Frame(flow_list_wrap, bg=C["BG3"])
        self._flow_profiles_list_frame.pack(fill="both", expand=True)

        self.flow_profiles_listbox = tk.Listbox(
            profiles_body, height=0, width=0,
            bg=C["BG3"], fg=C["FG"],
            selectbackground=C["ACC"], selectforeground=C["FG"],
            font=("Consolas", 8), relief="flat", borderwidth=0,
            highlightthickness=0, exportselection=False
        )
        self.flow_profiles_listbox.pack_forget()
        self.flow_profiles_listbox.bind("<<ListboxSelect>>", self._flow_profile_selecionado)

        # --- Timers (compacto em grid) ---
        tf = ttk.LabelFrame(col_c, text="Timers / Ciclos")
        tf.pack(fill="x", pady=(0, 6))
        timer_defs = [
            ("Perfis simultâneos:", "flow_max_parallel_profiles", "0",  "opt_max_parallel_profiles", "(0 = todos)"),
            ("Aguardar imagens (s):",     "flow_delay",            "10", "opt_delay",                 "após imagens"),
            ("Intervalo envios (s):",     "flow_send_interval",    "10", "opt_send_interval",         "entre pastas"),
            ("Intervalo ciclos (s):",     "flow_cycle_interval",   "60", "opt_cycle_interval",        "pausa/ciclo"),
            ("Abas por perfil/ciclo:",    "flow_sends_per_cycle",  "3",  "opt_sends_per_cycle",       "abas/ciclo"),
        ]
        for row_i, (lbl, key, default, attr, hint) in enumerate(timer_defs):
            tk.Label(tf, text=lbl, bg=C["BG2"], fg=C["FG"],
                     font=("Segoe UI", 8)).grid(row=row_i, column=0, sticky="w", padx=(4, 2), pady=1)
            var = tk.StringVar(value=self.config.get(key, default))
            setattr(self, attr, var)
            var.trace_add("write", lambda *a, k=key, v=var: self.config.update({k: v.get()}))
            ttk.Entry(tf, textvariable=var, width=6).grid(row=row_i, column=1, sticky="w", padx=2, pady=1)
            tk.Label(tf, text=hint, bg=C["BG2"], fg=C["FG2"],
                     font=("Segoe UI", 7)).grid(row=row_i, column=2, sticky="w", padx=(2, 4), pady=1)
        tf.columnconfigure(2, weight=1)
        self.opt_prompt_delay = self.opt_send_interval  # compat

        # --- Prompt ---
        prf = ttk.LabelFrame(bottom, text="Prompt")
        prf.pack(fill="both", expand=True)
        mgmt_row = tk.Frame(prf, bg=C["BG2"])
        mgmt_row.pack(fill="x", pady=(0, 3))
        self.prompt_sel_var = tk.StringVar(value=self.config.get("flow_prompt_edit", "Padrão"))
        self.prompt_combo = ttk.Combobox(mgmt_row, textvariable=self.prompt_sel_var,
            state="readonly", width=14, font=("Segoe UI", 8))
        self.prompt_combo.pack(side="left", padx=(0, 3))
        self.prompt_combo.bind("<<ComboboxSelected>>", lambda e: self._on_prompt_select())
        for txt, cmd in [("Novo", self._novo_prompt), ("Salvar", self._salvar_prompt), ("Excluir", self._excluir_prompt)]:
            ttk.Button(mgmt_row, text=txt, command=cmd).pack(side="left", padx=(0, 2))
        pt_frame = tk.Frame(prf, bg=C["BG2"])
        pt_frame.pack(fill="both", expand=True)
        pt_scroll = ttk.Scrollbar(pt_frame, style="Vertical.TScrollbar")
        pt_scroll.pack(side="right", fill="y")
        self.prompt_text = tk.Text(pt_frame, bg=C["BG3"], fg=C["FG"],
            insertbackground=C["ACC"], font=("Consolas", 9), relief="flat",
            borderwidth=0, wrap="word", yscrollcommand=pt_scroll.set, height=18)
        self.prompt_text.pack(fill="both", expand=True)
        pt_scroll.config(command=self.prompt_text.yview)

        sep_video = tk.Frame(body, bg=C["BORDER"], height=1)
        sep_video.pack(fill="x", pady=(18, 18))
        self._video_frame = ttk.LabelFrame(body, text="Separação")
        self._video_frame.pack(fill="both", expand=True)

        sep_motion = tk.Frame(body, bg=C["BORDER"], height=1)
        sep_motion.pack(fill="x", pady=(18, 18))
        self._motion_frame = ttk.LabelFrame(body, text="Motion")
        self._motion_frame.pack(fill="both", expand=True)

        # ── Inicialização ─────────────────────────────────────────────────────
        self._frames_rebuild_modelos_checklist()
        self._listar_videos()
        self._reload_prompt_combo()
        self._flow_rebuild_modelos_checklist()
        self._atualizar_pastas_flow()
        self._flow_profiles_carregar()
        self._bind_mousewheel_recursive(body, video_canvas)
    def _on_auto_modo_change(self):
        """Stub — modo fixo 'modelo'; mantido para compatibilidade."""
        pass

    def _frames_rebuild_modelos_checklist(self):
        """Reconstrói os checkboxes de modelos na aba Vídeo."""
        C = self.colors
        if not hasattr(self, "_frames_modelos_inner") or self._frames_modelos_inner is None:
            return
        inner = self._frames_modelos_inner
        for w in inner.winfo_children():
            w.destroy()

        anteriores = {n: v.get() for n, v in self._frames_modelos_vars.items()}
        self._frames_modelos_vars = {}

        if not self.modelos:
            lbl = tk.Label(inner, text="Nenhuma modelo cadastrada. Vá à aba Configuração > Modelos.",
                           bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8))
            lbl.pack(anchor="w", pady=4)
            if self._frames_modelos_canvas:
                self._bind_widget_mousewheel_to_canvas(lbl, self._frames_modelos_canvas)
            return

        cols = tk.Frame(inner, bg=C["BG2"])
        cols.pack(fill="x")
        if self._frames_modelos_canvas:
            self._bind_widget_mousewheel_to_canvas(cols, self._frames_modelos_canvas)
        col_frames = []
        for _ in range(2):
            cf = tk.Frame(cols, bg=C["BG2"])
            cf.pack(side="left", fill="both", expand=True, padx=2)
            if self._frames_modelos_canvas:
                self._bind_widget_mousewheel_to_canvas(cf, self._frames_modelos_canvas)
            col_frames.append(cf)

        for i, (nome, dados) in enumerate(self.modelos.items()):
            foto1 = dados.get("foto1", "")
            foto2 = dados.get("foto2", "")
            parent = col_frames[i % 2]
            row = tk.Frame(parent, bg=C["BG3"], bd=0, highlightthickness=1,
                           highlightbackground=C["BORDER"])
            row.pack(fill="x", pady=2, padx=1)
            if self._frames_modelos_canvas:
                self._bind_widget_mousewheel_to_canvas(row, self._frames_modelos_canvas)

            var = tk.BooleanVar(value=anteriores.get(nome, False))
            self._frames_modelos_vars[nome] = var

            cb = ttk.Checkbutton(row, text=nome, variable=var)
            cb.pack(side="left", padx=(4, 4), pady=3)
            if self._frames_modelos_canvas:
                self._bind_widget_mousewheel_to_canvas(cb, self._frames_modelos_canvas)

            def _toggle_modelo(_event=None, v=var):
                v.set(not v.get())
                return "break"

            row.bind("<Button-1>", _toggle_modelo)

            for fp in [foto1, foto2]:
                if fp and PIL_AVAILABLE and os.path.isfile(fp):
                    try:
                        img = Image.open(fp)
                        img.thumbnail((28, 28))
                        photo = ImageTk.PhotoImage(img)
                        lbl = tk.Label(row, image=photo, bg=C["BG3"])
                        lbl.image = photo
                        lbl.pack(side="left", padx=1, pady=2)
                        lbl.bind("<Button-1>", _toggle_modelo)
                        if self._frames_modelos_canvas:
                            self._bind_widget_mousewheel_to_canvas(lbl, self._frames_modelos_canvas)
                    except Exception:
                        pass
                elif fp:
                    lbl = tk.Label(row, text="[?]", bg=C["BG3"], fg=C["ERR"],
                                   font=("Segoe UI", 7))
                    lbl.pack(side="left", padx=1)
                    lbl.bind("<Button-1>", _toggle_modelo)
                    if self._frames_modelos_canvas:
                        self._bind_widget_mousewheel_to_canvas(lbl, self._frames_modelos_canvas)

        if self._frames_modelos_canvas:
            self._frames_modelos_canvas.update_idletasks()
            self._frames_modelos_canvas.configure(
                scrollregion=self._frames_modelos_canvas.bbox("all"))

    def _frames_modelos_marcar_todas(self):
        for v in self._frames_modelos_vars.values():
            v.set(True)

    def _frames_modelos_desmarcar_todas(self):
        for v in self._frames_modelos_vars.values():
            v.set(False)

    def _frames_modelos_selecionadas(self):
        """Retorna lista de nomes das modelos marcadas no checklist."""
        if not hasattr(self, "_frames_modelos_vars"):
            return []
        return [nome for nome, var in self._frames_modelos_vars.items() if var.get()]

    def _listar_videos(self):
        self.videos_listbox.delete(0, "end")
        exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        if VIDEOS_DIR.exists():
            for f in sorted(VIDEOS_DIR.iterdir()):
                if f.suffix.lower() in exts:
                    self.videos_listbox.insert("end", f"  {f.name}")
        else:
            self.videos_listbox.insert("end", "  [Pasta • VídeosOg não encontrada]")

    def _criar_frames_thread(self):
        threading.Thread(target=self._criar_frames, daemon=True).start()

    def _criar_frames(self):
        modo = self.auto_modo_var.get()
        if not CV2_AVAILABLE:
            messagebox.showerror("Erro", "OpenCV não instalado.\npip install opencv-python"); return

        exts_img = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        exts_vid = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

        if modo == "modelo":
            modelos_selecionadas = self._frames_modelos_selecionadas()
            if not modelos_selecionadas:
                modelos_selecionadas = sorted(self.modelos.keys())
                if not modelos_selecionadas:
                    messagebox.showerror("Erro", "Nenhuma modelo cadastrada."); return
                self._log(
                    f"Criar Frames: nenhuma modelo marcada; usando todas "
                    f"({len(modelos_selecionadas)})."
                )
            refs_externas = None
        elif modo == "pasta":
            pasta_refs_str = self.auto_pasta_refs_var.get().strip()
            if not pasta_refs_str or not os.path.isdir(pasta_refs_str):
                messagebox.showerror("Erro", "Selecione uma pasta de fotos de referência válida."); return
            pasta_refs = Path(pasta_refs_str)
            refs_externas = sorted([str(f) for f in pasta_refs.iterdir() if f.suffix.lower() in exts_img])
            if not refs_externas:
                messagebox.showerror("Erro", f"Nenhuma imagem encontrada em:\n{pasta_refs_str}"); return
            pasta_prefix = pasta_refs.name
            modelo_nome  = None
        else:
            pasta_prefix = None
            modelo_nome  = None
            refs_externas = None

        if not VIDEOS_DIR.exists():
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{VIDEOS_DIR}"); return

        videos = [f for f in sorted(VIDEOS_DIR.iterdir()) if f.suffix.lower() in exts_vid]
        if not videos:
            messagebox.showwarning("Aviso", "Nenhum vídeo encontrado."); return

        erros  = []
        criados = 0
        iteracoes = [(mn, None) for mn in modelos_selecionadas] if modo == "modelo" else [(None, refs_externas)]

        for (modelo_nome, refs_iter) in iteracoes:
            if modo == "modelo":
                pasta_prefix = modelo_nome
            for video_path in videos:
                try:
                    if modo == "detectar":
                        modelo_detectada = self._detectar_modelo_pasta(video_path.stem)
                        if not modelo_detectada:
                            cadastradas = ", ".join(self.modelos.keys())
                            raise RuntimeError(
                                f"modelo nao detectada em '{video_path.name}'. "
                                f"Cadastradas: {cadastradas or '(nenhuma)'}"
                            )
                        pasta_nome = video_path.stem[:80]
                        self._log(f"  Detectada: {video_path.name} -> {modelo_detectada}")
                    else:
                        pasta_nome = f"{pasta_prefix}_{video_path.stem[:40]}"
                    pasta = WORK_DIR / pasta_nome
                    pasta.mkdir(parents=True, exist_ok=True)
                    self._log(f"📁 {pasta_nome}")

                    if refs_iter is not None:
                        refs_dir = pasta / "_refs"
                        refs_dir.mkdir(exist_ok=True)
                        for ref_path in refs_iter:
                            dest_ref = refs_dir / Path(ref_path).name
                            if not dest_ref.exists():
                                shutil.copy2(ref_path, dest_ref)
                        self._log(f"  ✓ {len(refs_iter)} foto(s) de referência copiada(s) → _refs/")

                    # Vídeo sempre copiado
                    dest = pasta / video_path.name
                    if not dest.exists():
                        shutil.copy2(video_path, dest)
                        self._log(f"  ✓ Vídeo copiado")
                    else:
                        self._log(f"  ~ Vídeo já existe")

                    frame_path = pasta / "frameog.jpg"
                    cap = cv2.VideoCapture(str(video_path))
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        cv2.imwrite(str(frame_path), frame)
                        self._log(f"  ✓ frameog.jpg extraído")
                        criados += 1
                    else:
                        self._log(f"  ✗ Falha ao ler frame: {video_path.name}")
                        erros.append(video_path.name)
                except Exception as e:
                    self._log(f"  ✗ Erro: {e}")
                    erros.append(video_path.name)

        msg = f"Concluído! {criados} pasta(s) criada(s) em assets/work"
        if erros:
            msg += f"\n\nErros:\n" + "\n".join(erros)
        messagebox.showinfo("Concluído", msg)
        self._log("─" * 50)


    def _flow_rebuild_modelos_checklist(self):
        """Reconstrói os checkboxes de modelos no painel de filtro da aba Flow."""
        C = self.colors
        inner = self._flow_modelos_inner
        for w in inner.winfo_children():
            w.destroy()

        anteriores = {n: v.get() for n, v in self._flow_modelos_vars.items()}
        self._flow_modelos_vars = {}

        if not self.modelos:
            tk.Label(inner, text="Nenhuma modelo cadastrada. Vá à aba Configuração > Modelos.",
                     bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8)).pack(anchor="w", pady=4)
            return

        cols = tk.Frame(inner, bg=C["BG2"])
        cols.pack(fill="x")
        col_frames = []
        for _ in range(3):
            cf = tk.Frame(cols, bg=C["BG2"])
            cf.pack(side="left", fill="both", expand=True, padx=2)
            col_frames.append(cf)

        for i, nome in enumerate(self.modelos.keys()):
            var = tk.BooleanVar(value=anteriores.get(nome, False))
            self._flow_modelos_vars[nome] = var
            parent = col_frames[i % 3]

            row = tk.Frame(parent, bg=C["BG2"], cursor="hand2")
            row.pack(fill="x", pady=1, padx=2)

            cb = ttk.Checkbutton(row, variable=var, command=self._atualizar_pastas_flow)
            cb.pack(side="left")

            lbl = tk.Label(
                row, text=nome, bg=C["BG2"], fg=C["FG"],
                font=("Segoe UI", 9), anchor="w", cursor="hand2"
            )
            lbl.pack(side="left", fill="x", expand=True)

            def _toggle(e, v=var):
                v.set(not v.get())
                self._atualizar_pastas_flow()
            lbl.bind("<Button-1>", _toggle)
            row.bind("<Button-1>", _toggle)

        self._flow_modelos_canvas.update_idletasks()
        self._flow_modelos_canvas.configure(
            scrollregion=self._flow_modelos_canvas.bbox("all"))

    def _flow_modelos_marcar_todas(self):
        for v in self._flow_modelos_vars.values():
            v.set(True)
        self._atualizar_pastas_flow()

    def _flow_modelos_desmarcar_todas(self):
        for v in self._flow_modelos_vars.values():
            v.set(False)
        self._atualizar_pastas_flow()

    def _reload_prompt_combo(self):
        nomes = list(self.prompts.keys())
        self.prompt_combo["values"] = nomes
        ativo = self.prompt_sel_var.get()
        if ativo not in nomes:
            ativo = nomes[0] if nomes else ""
            self.prompt_sel_var.set(ativo)
        self._on_prompt_select()

    def _on_prompt_select(self):
        nome = self.prompt_sel_var.get()
        self.config["flow_prompt_edit"] = nome
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("end", self.prompts.get(nome, ""))

    def _salvar_prompt(self):
        nome = self.prompt_sel_var.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Selecione ou crie um prompt primeiro."); return
        texto = self.prompt_text.get("1.0", "end").rstrip()
        self.prompts[nome] = texto
        save_json(PROMPTS_FILE, self.prompts)
        self._reload_prompt_combo()
        self.prompt_sel_var.set(nome)
        self._log(f"  ✓ Prompt '{nome}' salvo.")

    def _novo_prompt(self):
        win = tk.Toplevel(self)
        win.title("Novo Prompt")
        win.configure(bg=self.colors["BG"])
        win.geometry("320x120")
        win.grab_set()
        tk.Label(win, text="Nome do novo prompt:", bg=self.colors["BG"],
                 fg=self.colors["FG"], font=("Segoe UI", 10)).pack(pady=(18, 4))
        nome_var = tk.StringVar()
        entry = ttk.Entry(win, textvariable=nome_var, font=("Segoe UI", 11), width=28)
        entry.pack(pady=(0, 12))
        entry.focus()
        def _ok():
            nome = nome_var.get().strip()
            if not nome: return
            if nome in self.prompts:
                messagebox.showerror("Erro", f"Já existe um prompt chamado '{nome}'.", parent=win)
                return
            self.prompts[nome] = ""
            save_json(PROMPTS_FILE, self.prompts)
            self._reload_prompt_combo()
            self.prompt_sel_var.set(nome)
            self._on_prompt_select()
            win.destroy()
        entry.bind("<Return>", lambda e: _ok())
        ttk.Button(win, text="Criar", style="Accent.TButton", command=_ok).pack()

    def _excluir_prompt(self):
        nome = self.prompt_sel_var.get().strip()
        if not nome: return
        if len(self.prompts) <= 1:
            messagebox.showwarning("Aviso", "Deve existir ao menos um prompt."); return
        if messagebox.askyesno("Confirmar", f"Excluir o prompt '{nome}'?"):
            del self.prompts[nome]
            save_json(PROMPTS_FILE, self.prompts)
            self._reload_prompt_combo()

    def _flow_profiles_padrao(self):
        return [{
            "id": "perfil_1",
            "name": "Perfil 1",
            "port": "9222",
            "url": FLOW_URL,
            "session": CHROME_SESSION,
            "active": True,
        }]

    def _flow_profiles_obter(self):
        perfis = self.config.get("flow_profiles")
        if not isinstance(perfis, list) or not perfis:
            perfis = self._flow_profiles_padrao()
            self.config["flow_profiles"] = perfis
        normalizados = []
        for indice, perfil in enumerate(perfis, 1):
            if not isinstance(perfil, dict):
                continue
            normalizados.append({
                "id": str(perfil.get("id") or f"perfil_{indice}"),
                "name": str(
                    perfil.get("name") or f"Perfil {indice}"
                ).strip(),
                "port": str(
                    perfil.get("port") or (9221 + indice)
                ).strip(),
                "url": str(perfil.get("url") or FLOW_URL).strip(),
                "session": str(
                    perfil.get("session")
                    or (
                        CHROME_SESSION if indice == 1
                        else f"{CHROME_SESSION}_{indice}"
                    )
                ),
                "active": bool(perfil.get("active", True)),
            })
        if not normalizados:
            normalizados = self._flow_profiles_padrao()
        self.config["flow_profiles"] = normalizados
        return normalizados

    def _flow_profiles_salvar_config(self):
        save_json(CONFIG_FILE, self.config)

    def _flow_profiles_carregar(self, selecionar=0):
        self.flow_profiles_listbox.delete(0, "end")
        if hasattr(self, "flow_profiles_checks_frame"):
            for w in self.flow_profiles_checks_frame.winfo_children():
                w.destroy()
        if hasattr(self, "_flow_profiles_list_frame"):
            for w in self._flow_profiles_list_frame.winfo_children():
                w.destroy()
        self._flow_profile_check_vars = {}
        self._flow_profile_row_frames = {}
        C = self.colors
        perfis = self._flow_profiles_obter()
        for indice, perfil in enumerate(perfis):
            var = tk.BooleanVar(value=perfil["active"])
            self._flow_profile_check_vars[indice] = var

            if hasattr(self, "_flow_profiles_list_frame"):
                row = tk.Frame(self._flow_profiles_list_frame, bg=C["BG3"], cursor="hand2")
                row.pack(fill="x", pady=0)
                self._flow_profile_row_frames[indice] = row

                def _toggle_profile(i=indice, v=var):
                    self._flow_profile_toggle_active(i, v.get())
                    self._flow_profile_selecionar_linha(i)
                cb = ttk.Checkbutton(row, variable=var, command=_toggle_profile)
                cb.pack(side="left", padx=(5, 2))

                lbl = tk.Label(
                    row,
                    text=f"{perfil['name']}  |  {perfil['port']}",
                    bg=C["BG3"], fg=C["FG"], font=("Consolas", 8),
                    anchor="w", cursor="hand2"
                )
                lbl.pack(side="left", fill="x", expand=True, padx=(2, 4), pady=3)

                def _select_row(e, i=indice):
                    self._flow_profile_selecionar_linha(i)
                for w in (row, lbl):
                    w.bind("<Button-1>", _select_row)

            self.flow_profiles_listbox.insert(
                "end",
                f"{'✓' if perfil['active'] else ' '} {perfil['name']} | porta {perfil['port']}"
            )

        if perfis:
            selecionar = max(0, min(selecionar, len(perfis) - 1))
            self.flow_profiles_listbox.selection_clear(0, "end")
            self.flow_profiles_listbox.selection_set(selecionar)
            self.flow_profiles_listbox.activate(selecionar)
            self._flow_profile_selecionar_linha(selecionar)
            self._flow_profile_carregar_editor(selecionar)

    def _flow_profile_selecionar_linha(self, indice):
        C = self.colors
        if not hasattr(self, "_flow_profile_row_frames"):
            return
        for i, row in self._flow_profile_row_frames.items():
            bg = C["ACC"] if i == indice else C["BG3"]
            fg = C["FG"] if i == indice else C["FG"]
            row.configure(bg=bg)
            for w in row.winfo_children():
                try:
                    if isinstance(w, tk.Label):
                        w.configure(bg=bg, fg=fg)
                except Exception:
                    pass
        self.flow_profiles_listbox.selection_clear(0, "end")
        self.flow_profiles_listbox.selection_set(indice)
        self.flow_profiles_listbox.activate(indice)
        self._flow_profile_carregar_editor(indice)

    def _flow_profile_toggle_active(self, indice, ativo):
        perfis = self._flow_profiles_obter()
        if indice is None or not (0 <= indice < len(perfis)):
            return
        perfis[indice]["active"] = bool(ativo)
        self.config["flow_profiles"] = perfis
        self._flow_profiles_salvar_config()
        self.flow_profiles_listbox.delete(indice)
        marcador = "✓" if ativo else " "
        perfil = perfis[indice]
        self.flow_profiles_listbox.insert(
            indice, f"[{marcador}] {perfil['name']} | porta {perfil['port']}"
        )
        self.flow_profiles_listbox.selection_clear(0, "end")
        self.flow_profiles_listbox.selection_set(indice)
        self.flow_profiles_listbox.activate(indice)
        self.flow_profile_active_var.set(bool(ativo))
        self._log(f"Perfil Flow {'ativado' if ativo else 'desativado'}: {perfil['name']}")

    def _flow_profile_indice(self):
        selecao = self.flow_profiles_listbox.curselection()
        return selecao[0] if selecao else None

    def _flow_profile_carregar_editor(self, indice):
        perfis = self._flow_profiles_obter()
        if indice is None or not (0 <= indice < len(perfis)):
            return
        perfil = perfis[indice]
        self.flow_profile_active_var.set(perfil["active"])
        self.flow_profile_name_var.set(perfil["name"])
        self.flow_profile_port_var.set(perfil["port"])
        self.flow_profile_url_var.set(perfil["url"])

    def _flow_profile_selecionado(self, _event=None):
        self._flow_profile_carregar_editor(self._flow_profile_indice())

    def _flow_profile_validar_editor(self):
        nome = self.flow_profile_name_var.get().strip()
        porta = self.flow_profile_port_var.get().strip()
        url = self.flow_profile_url_var.get().strip()
        if not nome:
            raise ValueError("Informe um nome para o perfil.")
        try:
            porta_num = int(porta)
        except ValueError as exc:
            raise ValueError("A porta precisa ser um numero.") from exc
        if not (1024 <= porta_num <= 65535):
            raise ValueError("A porta deve ficar entre 1024 e 65535.")
        if not (
                url.startswith("https://labs.google/")
                and "/flow/project/" in url):
            raise ValueError("Informe um link valido de projeto do Google Flow.")
        return nome, str(porta_num), url

    def _flow_profile_salvar(self):
        indice = self._flow_profile_indice()
        if indice is None:
            return
        try:
            nome, porta, url = self._flow_profile_validar_editor()
        except ValueError as exc:
            messagebox.showerror("Perfil Flow", str(exc))
            return
        perfis = self._flow_profiles_obter()
        for outro_indice, outro in enumerate(perfis):
            if outro_indice != indice and outro["port"] == porta:
                messagebox.showerror(
                    "Perfil Flow",
                    f"A porta {porta} ja esta sendo usada por "
                    f"'{outro['name']}'."
                )
                return
        perfis[indice].update({
            "name": nome,
            "port": porta,
            "url": url,
            "active": self.flow_profile_active_var.get(),
        })
        self.config["flow_profiles"] = perfis
        self._flow_profiles_salvar_config()
        self._flow_profiles_carregar(indice)
        self._log(
            f"Perfil Flow salvo: {nome} | porta {porta} | {url}"
        )

    def _flow_profile_novo(self):
        perfis = self._flow_profiles_obter()
        usados = {
            int(p["port"]) for p in perfis
            if str(p.get("port", "")).isdigit()
        }
        porta = 9222
        while porta in usados:
            porta += 1
        numero = 1
        ids = {p["id"] for p in perfis}
        while f"perfil_{numero}" in ids:
            numero += 1
        perfil = {
            "id": f"perfil_{numero}",
            "name": f"Perfil {numero}",
            "port": str(porta),
            "url": FLOW_URL,
            "session": (
                CHROME_SESSION if numero == 1
                else f"{CHROME_SESSION}_{numero}"
            ),
            "active": True,
        }
        perfis.append(perfil)
        self.config["flow_profiles"] = perfis
        self._flow_profiles_salvar_config()
        self._flow_profiles_carregar(len(perfis) - 1)

    def _flow_profile_excluir(self):
        indice = self._flow_profile_indice()
        perfis = self._flow_profiles_obter()
        if indice is None or len(perfis) <= 1:
            messagebox.showwarning(
                "Perfil Flow", "Deve existir pelo menos um perfil."
            )
            return
        perfil = perfis[indice]
        if not messagebox.askyesno(
                "Excluir perfil",
                f"Excluir '{perfil['name']}' da lista?\n\n"
                "O login salvo ainda sera mantido no computador."):
            return
        perfis.pop(indice)
        self.config["flow_profiles"] = perfis
        self._flow_profiles_salvar_config()
        self._flow_profiles_carregar(max(0, indice - 1))

    def _flow_profile_selecionado_dados(self):
        indice = self._flow_profile_indice()
        perfis = self._flow_profiles_obter()
        if indice is None or not (0 <= indice < len(perfis)):
            return None
        return dict(perfis[indice])

    def _flow_perfis_ativos(self):
        return [
            dict(perfil) for perfil in self._flow_profiles_obter()
            if perfil.get("active")
        ]

    def _int_config_positivo(self, var_ou_valor, padrao=0, minimo=0):
        """Converte uma StringVar/valor para inteiro, respeitando mínimo."""
        try:
            valor = var_ou_valor.get() if hasattr(var_ou_valor, "get") else var_ou_valor
            return max(minimo, int(str(valor).strip()))
        except Exception:
            return max(minimo, int(padrao))

    def _limitar_perfis_ativos(self, perfis, var_limite=None, padrao=0):
        """
        Usa somente os perfis marcados como ativos, respeitando o limite configurado.
        Limite 0 = todos os perfis ativos.
        """
        limite = self._int_config_positivo(var_limite, padrao=padrao, minimo=0)
        if limite > 0:
            return perfis[:limite], limite
        return perfis, 0

    def _imagem_dedupe_key(self, caminho):
        """Cria uma chave estável para impedir o mesmo arquivo/imagem de entrar duas vezes."""
        p = Path(caminho)
        try:
            h = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            return ("sha256", h.hexdigest())
        except Exception:
            try:
                return ("path", str(p.resolve()).lower())
            except Exception:
                return ("path", str(p).lower())

    def _deduplicar_caminhos_por_imagem(self, caminhos, imagem_resolver=None, label="imagem"):
        """
        Remove entradas repetidas antes da distribuição em perfis/abas.
        Se duas pastas/arquivos apontarem para a mesma imagem, só a primeira entra na fila.
        """
        unicos = []
        vistos = {}
        duplicados = []
        for item in caminhos:
            alvo = imagem_resolver(item) if imagem_resolver else item
            alvo = Path(alvo)
            if alvo.exists() and alvo.is_file():
                chave = self._imagem_dedupe_key(alvo)
            else:
                try:
                    chave = ("missing", str(Path(item).resolve()).lower())
                except Exception:
                    chave = ("missing", str(item).lower())
            if chave in vistos:
                duplicados.append((item, vistos[chave]))
                continue
            vistos[chave] = item
            unicos.append(item)
        if duplicados:
            self._log(
                f"  ⚠ {len(duplicados)} {label}(ns) repetida(s) ignorada(s) "
                "para não produzir imagem duplicada."
            )
            for repetido, original in duplicados[:20]:
                self._log(f"    ↳ ignorado: {Path(repetido).name} | já entrou: {Path(original).name}")
            if len(duplicados) > 20:
                self._log(f"    … +{len(duplicados) - 20} repetida(s) omitida(s) no log")
        return unicos

    def _flow_chrome_path(self):
        candidatos = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        return next((p for p in candidatos if os.path.exists(p)), None)

    def _flow_abrir_perfil(self, perfil):
        chrome = self._flow_chrome_path()
        if not chrome:
            raise RuntimeError("Chrome nao encontrado.")
        session_path = Path(perfil["session"])
        perfil_existe = session_path.exists()
        session_path.mkdir(parents=True, exist_ok=True)
        subprocess.Popen([
            chrome,
            f"--remote-debugging-port={perfil['port']}",
            f"--user-data-dir={perfil['session']}",
            "--no-first-run",
            "--no-default-browser-check",
            perfil["url"],
        ])
        self._log(
            f"Chrome Flow aberto: {perfil['name']} | "
            f"porta {perfil['port']} | {perfil['url']}"
        )
        return perfil_existe

    def _flow_porta_respondendo(self, porta, timeout=1.5):
        try:
            with urllib.request.urlopen(
                    f"http://localhost:{porta}/json/version",
                    timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _flow_aguardar_porta(self, porta, timeout=30, intervalo=0.5):
        """Aguarda o Chrome com remote debugging responder na porta informada."""
        inicio = time.time()
        while time.time() - inicio < timeout:
            if self._flow_porta_respondendo(porta, timeout=min(1.5, intervalo)):
                return True
            time.sleep(intervalo)
        return self._flow_porta_respondendo(porta, timeout=1.5)

    def _flow_garantir_perfil_aberto(self, perfil):
        porta = perfil.get("port")
        if self._flow_porta_respondendo(porta):
            return False
        self._log(
            f"[{perfil['name']}] Chrome Flow fechado na porta {porta}. "
            "Abrindo automaticamente..."
        )
        self._flow_abrir_perfil(perfil)
        espera = 30
        self._log(
            f"[{perfil['name']}] Aguardando o Chrome responder na porta "
            f"{porta} por ate {espera}s..."
        )
        if not self._flow_aguardar_porta(porta, timeout=espera):
            raise RuntimeError(
                f"Chrome aberto para '{perfil['name']}', mas a porta {porta} "
                "nao respondeu. Feche Chromes antigos desse perfil e tente novamente."
            )
        self._log(f"[{perfil['name']}] Chrome pronto na porta {porta}.")
        return True

    def _abrir_chrome_debug(self):
        perfil = self._flow_profile_selecionado_dados()
        if not perfil:
            messagebox.showwarning(
                "Perfil Flow", "Selecione um perfil para abrir."
            )
            return
        self._flow_profile_salvar()
        perfil = self._flow_profile_selecionado_dados()
        try:
            perfil_existe = self._flow_abrir_perfil(perfil)
        except Exception as exc:
            messagebox.showerror("Perfil Flow", str(exc))
            return
        if not perfil_existe:
            messagebox.showinfo(
                "Novo perfil Flow",
                f"A sessao '{perfil['name']}' foi criada.\n\n"
                "Faca login na conta Google desta sessao. O login ficara "
                "salvo para as proximas vezes."
            )

    def _flow_abrir_perfis_ativos(self):
        self._flow_profile_salvar()
        perfis = self._flow_perfis_ativos()
        if not perfis:
            messagebox.showwarning(
                "Perfis Flow", "Marque pelo menos um perfil como ativo."
            )
            return
        novos = []
        erros = []
        for perfil in perfis:
            try:
                if not self._flow_abrir_perfil(perfil):
                    novos.append(perfil["name"])
                time.sleep(0.4)
            except Exception as exc:
                erros.append(f"{perfil['name']}: {exc}")
        if novos:
            messagebox.showinfo(
                "Novas sessoes Flow",
                "Faca login nestas sessoes:\n\n" + "\n".join(novos)
            )
        if erros:
            messagebox.showerror(
                "Erro ao abrir perfis", "\n".join(erros)
            )

    def _atualizar_pastas_flow(self):
        self.pastas_listbox.delete(0, "end")
        if not WORK_DIR.exists():
            return

        # Modelos marcadas no checklist (None ou vazio = mostrar todas)
        modelos_filtro = set()
        if hasattr(self, "_flow_modelos_vars"):
            modelos_filtro = {n for n, v in self._flow_modelos_vars.items() if v.get()}

        for p in sorted(WORK_DIR.iterdir()):
            if p.is_dir():
                if modelos_filtro:
                    modelo_pasta = self._detectar_modelo_pasta(p.name)
                    if modelo_pasta not in modelos_filtro:
                        continue
                tem_frame = (p / "frameog.jpg").exists()
                tem_refs  = (p / "_refs").is_dir()
                icone_frame = "✓" if tem_frame else "⚠"
                icone_refs  = "📁" if tem_refs else "👤"
                self.pastas_listbox.insert("end", f"  {icone_frame} {icone_refs} {p.name}")

    def _limpar_pastas_work(self):
        if not WORK_DIR.exists():
            self._atualizar_pastas_flow()
            return
        pastas = [p for p in sorted(WORK_DIR.iterdir()) if p.is_dir()]
        if not pastas:
            self._atualizar_pastas_flow()
            return
        if not messagebox.askyesno(
            "Limpar work",
            f"Apagar {len(pastas)} pasta(s) em:\n{WORK_DIR}?"
        ):
            return
        base = WORK_DIR.resolve()
        apagadas = 0
        erros = []
        for pasta in pastas:
            try:
                alvo = pasta.resolve()
                if alvo.parent != base:
                    raise RuntimeError("caminho fora de assets/work")
                shutil.rmtree(alvo)
                apagadas += 1
            except Exception as exc:
                erros.append(f"{pasta.name}: {exc}")
        self._atualizar_pastas_flow()
        self._log(f"assets/work: {apagadas} pasta(s) apagada(s).")
        if erros:
            messagebox.showwarning(
                "Limpar work",
                "Algumas pastas não foram apagadas:\n" + "\n".join(erros[:8])
            )

    def _enviar_flow_thread(self):
        def _run():
            asyncio.run(self._enviar_flow_async())
        threading.Thread(target=_run, daemon=True).start()

    def _obter_abas_flow_abertas(self, context, projeto_url=None):
        abas = []
        for page in context.pages:
            try:
                if (
                    not page.is_closed()
                    and "labs.google/fx/" in page.url
                    and "/flow/" in page.url
                    and (
                        not projeto_url
                        or (
                            page.url.split("?", 1)[0].rstrip("/")
                            == projeto_url.split("?", 1)[0].rstrip("/")
                        )
                    )
                ):
                    abas.append(page)
            except Exception:
                continue
        return abas

    async def _enviar_flow_async(self, pastas_override=None):
        if not PLAYWRIGHT_AVAILABLE:
            self.after(0, lambda: messagebox.showerror("Erro",
                "Playwright não instalado.\n"
                "Execute no terminal:\n"
                "pip install playwright\n"
                "playwright install chromium"))
            return

        p_nome  = self.prompt_sel_var.get().strip()
        p_texto = self.prompt_text.get("1.0", "end").rstrip()
        if not p_texto:
            self.after(
                0, lambda: messagebox.showerror(
                    "Erro",
                    "O prompt está vazio. Escreva ou selecione um prompt "
                    "antes de enviar."
                )
            )
            return

        if pastas_override is not None:
            pastas_sel = list(pastas_override)
        else:
            if not WORK_DIR.exists():
                pastas_sel = []
            else:
                pastas_sel = [p for p in sorted(WORK_DIR.iterdir()) if p.is_dir()]
            if not pastas_sel:
                self.after(
                    0, lambda: messagebox.showwarning(
                        "Aviso",
                        "Nenhuma pasta encontrada em assets/work para enviar."
                    )
                )
                return
            self._log(f"Flow: enviando todas as pastas em assets/work ({len(pastas_sel)}).")

        pastas_sel = self._deduplicar_caminhos_por_imagem(
            pastas_sel,
            imagem_resolver=lambda pasta: Path(pasta) / "frameog.jpg",
            label="frame"
        )
        if not pastas_sel:
            self.after(
                0, lambda: messagebox.showwarning(
                    "Flow", "Nenhuma pasta única sobrou para enviar."
                )
            )
            return

        perfis_todos = self._flow_perfis_ativos()
        if not perfis_todos:
            self.after(
                0, lambda: messagebox.showwarning(
                    "Perfis Flow",
                    "Marque pelo menos um perfil Flow como ativo."
                )
            )
            return
        perfis, limite_perfis = self._limitar_perfis_ativos(
            perfis_todos,
            getattr(self, "opt_max_parallel_profiles", None),
            padrao=0
        )
        if not perfis:
            self.after(
                0, lambda: messagebox.showwarning(
                    "Perfis Flow",
                    "O limite de perfis simultaneos deixou a fila vazia."
                )
            )
            return

        try:
            delay_img = float(self.opt_delay.get())
        except ValueError:
            delay_img = 10.0
        try:
            send_interval = float(self.opt_send_interval.get())
        except ValueError:
            send_interval = 10.0
        try:
            cycle_interval = float(self.opt_cycle_interval.get())
        except ValueError:
            cycle_interval = 60.0
        try:
            sends_per_cycle = max(1, int(self.opt_sends_per_cycle.get()))
        except ValueError:
            sends_per_cycle = 3

        posicoes = {
            pasta: indice for indice, pasta in enumerate(pastas_sel, 1)
        }
        distribuicoes = []
        for indice, perfil in enumerate(perfis):
            lote = pastas_sel[indice::len(perfis)]
            if lote:
                distribuicoes.append((perfil, lote))
        distribuidas = [
            pasta for _, lote in distribuicoes for pasta in lote
        ]
        if len(set(distribuidas)) != len(distribuidas):
            self.after(
                0, lambda: messagebox.showerror(
                    "Flow",
                    "Distribuicao abortada: uma pasta caiu em mais de "
                    "um perfil/aba."
                )
            )
            return

        capacidade_simultanea = max(1, sends_per_cycle) * max(1, len(distribuicoes))
        self._log("🚀 Iniciando Flow em múltiplos perfis...")
        self._log(f"   Perfis ativos    : {len(perfis_todos)}")
        self._log(f"   Perfis em uso    : {len(distribuicoes)}" + (f" de {limite_perfis}" if limite_perfis else ""))
        self._log(f"   Abas por perfil  : {sends_per_cycle}")
        self._log(f"   Produção simult. : até {capacidade_simultanea} imagem(ns)")
        self._log(f"   Pastas totais    : {len(pastas_sel)}")
        for perfil, lote in distribuicoes:
            self._log(
                f"   {perfil['name']} (porta {perfil['port']}): "
                f"{len(lote)} pasta(s)"
            )

        resultados = await asyncio.gather(*[
            self._enviar_flow_perfil_async(
                perfil, lote, p_nome, p_texto,
                delay_img, send_interval, cycle_interval,
                sends_per_cycle, posicoes
            )
            for perfil, lote in distribuicoes
        ])

        erros = []
        itens_revisao = []
        falhas_perfil = []
        for resultado in resultados:
            erros.extend(resultado["erros"])
            itens_revisao.extend(resultado["itens_revisao"])
            if resultado.get("erro_geral"):
                falhas_perfil.append(
                    f"{resultado['perfil']}: {resultado['erro_geral']}"
                )

        total = len(pastas_sel)
        erros_pastas_set = {p for _, p in erros}
        concluidos = total - len(erros_pastas_set)
        msg = f"Envio concluído!\n{concluidos}/{total} enviado(s)."
        if erros:
            nomes_erros = list(dict.fromkeys(n for n, _ in erros))
            msg += "\n\nErros em:\n" + "\n".join(nomes_erros)
        if falhas_perfil:
            msg += "\n\nFalhas de perfil:\n" + "\n".join(falhas_perfil)
        self.after(0, lambda: messagebox.showinfo("Concluído", msg))
        self._log("─" * 50)

        # Adiciona pastas com erro à revisão (marcadas automaticamente como refazer)
        pastas_ok = {item["pasta"] for item in itens_revisao}
        pos_extra = max((item["pos"] for item in itens_revisao), default=0)
        for nome, pasta in {e[0]: e[1] for e in erros}.items():
            if pasta not in pastas_ok:
                pos_extra += 1
                itens_revisao.append({
                    "pasta": pasta,
                    "arquivo": None,
                    "pos": pos_extra,
                    "erro": True,
                })

        if itens_revisao:
            itens_revisao.sort(key=lambda item: item["pos"])
            self.after(0, lambda: self._abrir_revisao(itens_revisao))

    async def _enviar_flow_perfil_async(
            self, perfil, pastas_sel, p_nome, p_texto,
            delay_img, send_interval, cycle_interval,
            sends_per_cycle, posicoes_globais):
        porta = perfil["port"]
        projeto_url = perfil["url"]
        prefixo = f"[{perfil['name']}]"

        total_pastas = len(pastas_sel)
        total_ciclos = (total_pastas + sends_per_cycle - 1) // sends_per_cycle

        self._log(f"{prefixo} Projeto: {projeto_url}")
        self._log(f"{prefixo} Pastas: {total_pastas}")
        self._log(f"{prefixo} Ciclos: {total_ciclos}")

        erros = []  # list[(nome_str, pasta_path)]
        downloads_pendentes = []
        erro_geral = None

        try:
            try:
                self._flow_garantir_perfil_aberto(perfil)
            except Exception as exc:
                raise RuntimeError(
                    f"Nao foi possivel abrir o perfil '{perfil['name']}': "
                    f"{exc}"
                ) from exc

            async with async_playwright() as pw:
                try:
                    browser = await pw.chromium.connect_over_cdp(f"http://localhost:{porta}")
                except Exception as exc:
                    raise RuntimeError(
                        f"Não foi possível conectar à porta {porta}. "
                        f"O perfil '{perfil['name']}' foi aberto "
                        "automaticamente, mas a porta ainda nao respondeu."
                    ) from exc

                context = browser.contexts[0]

                # Reaproveita as abas do Flow que ja estao abertas no Chrome.
                # A conexao Playwright e recriada, mas as paginas persistem no
                # perfil remoto e podem ser recuperadas por context.pages.
                abas_flow = self._obter_abas_flow_abertas(
                    context, projeto_url
                )
                if abas_flow:
                    self._log(
                        f"   Abas Flow reutilizadas: {len(abas_flow)}"
                    )

                # Acumula (aba, pasta, posição_global) de todos os ciclos para download no final
                for ciclo_idx in range(total_ciclos):
                    ciclo_num    = ciclo_idx + 1
                    inicio       = ciclo_idx * sends_per_cycle
                    fim          = min(inicio + sends_per_cycle, total_pastas)
                    ciclo_pastas = pastas_sel[inicio:fim]
                    n_abas       = len(ciclo_pastas)

                    self._log(f"\n{'─'*46}")
                    self._log(f"🔄  CICLO {ciclo_num}/{total_ciclos}  —  {n_abas} aba(s)  "
                              f"(pasta {inicio+1}–{fim} de {total_pastas})")
                    self._log(f"{'─'*46}")

                    # Abre somente as abas que faltarem.
                    async def _abrir_aba(slot):
                        self._log(f"  🌐 Abrindo aba {slot}/{n_abas}...")
                        nova = await context.new_page()
                        await nova.goto(projeto_url)
                        await nova.wait_for_load_state("networkidle", timeout=30000)
                        self._log(f"  ✓ Aba {slot} pronta")
                        return nova

                    while len(abas_flow) < n_abas:
                        faltam = n_abas - len(abas_flow)
                        slots  = list(range(len(abas_flow) + 1, len(abas_flow) + faltam + 1))
                        novas  = await asyncio.gather(*[_abrir_aba(s) for s in slots])
                        abas_flow.extend(novas)

                    # FASE 1: Upload + prompt em paralelo em todas as abas.
                    self._log(
                        f"\n  📤 FASE 1 — Upload + prompt simultâneo "
                        f"nas {n_abas} aba(s)..."
                    )

                    async def _preparar_slot(tab_i, pasta):
                        aba        = abas_flow[tab_i]
                        global_num = posicoes_globais[pasta]

                        frame_path = pasta / "frameog.jpg"
                        if not frame_path.exists():
                            self._log(f"  [Aba {tab_i+1}] ⚠ frameog.jpg não encontrado em {pasta.name}")
                            erros.append((pasta.name, pasta))
                            return (aba, pasta, None, False)

                        refs_dir = pasta / "_refs"
                        exts_img = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
                        if refs_dir.is_dir():
                            modelo_nome = None
                            refs = sorted([
                                str(f) for f in refs_dir.iterdir()
                                if f.suffix.lower() in exts_img
                            ])
                            fonte_label = f"_refs/ ({len(refs)} foto(s))"
                        else:
                            modelo_nome = self._detectar_modelo_pasta(pasta.name)
                            dados = self.modelos.get(modelo_nome, {}) if modelo_nome else {}
                            refs  = []
                            for i in range(1, 3):
                                fp = dados.get(f"foto{i}", "").strip()
                                if fp and os.path.isfile(fp):
                                    refs.append(fp)
                            if modelo_nome:
                                fonte_label = f"modelo '{modelo_nome}' ({len(refs)} foto(s))"
                            else:
                                fonte_label = f"modelo não identificada ({len(refs)} foto(s))"

                        refs = refs[:2]
                        if len(refs) < 2:
                            if modelo_nome is None and not refs_dir.is_dir():
                                self._log(f"  [Aba {tab_i+1}] ⚠ Não foi possível identificar a modelo "
                                          f"a partir do nome da pasta '{pasta.name}'. "
                                          f"Modelos cadastradas: {', '.join(self.modelos.keys()) or '(nenhuma)'}")
                            else:
                                self._log(f"  [Aba {tab_i+1}] ⚠ Precisa de 2 imagens de referência para "
                                          f"'{pasta.name}' (modelo '{modelo_nome}' tem {len(refs)} foto(s) "
                                          f"cadastrada(s) e válida(s))")
                            erros.append((pasta.name, pasta))
                            return (aba, pasta, modelo_nome, False)

                        imagens = refs + [str(frame_path)]
                        self._log(f"\n  [Aba {tab_i+1}/{n_abas}] 📂 {pasta.name}"
                                  f"  →  {fonte_label}"
                                  f"  [global {global_num}]")
                        try:
                            await self._preparar_aba_flow_async(aba, imagens, p_texto)
                            return (aba, pasta, modelo_nome, True)
                        except Exception as e:
                            self._log(
                                f"  [Aba {tab_i+1}] ✗ Erro na preparação: {e}"
                            )
                            erros.append((pasta.name, pasta))
                            return (aba, pasta, modelo_nome, False)

                    abas_info = await asyncio.gather(*[
                        _preparar_slot(i, pasta)
                        for i, pasta in enumerate(ciclo_pastas)
                    ])

                    abas_ok = [
                        (aba, pasta, modelo)
                        for aba, pasta, modelo, ok in abas_info if ok
                    ]
                    if abas_ok:
                        self._log(
                            f"\n  ⏳ FASE 2 — Aguardando {delay_img}s "
                            f"para todas as {len(abas_ok)} aba(s)..."
                        )
                        await asyncio.sleep(delay_img)

                    self._log(
                        f"\n  🚀 FASE 3 — Enviando simultaneamente "
                        f"em {len(abas_ok)} aba(s)..."
                    )

                    srcs_anteriores = {}

                    async def _enviar_aba(aba, pasta, num, total):
                        try:
                            self._log(
                                f"\n  [Aba {num}/{total}] → {pasta.name}"
                            )
                            try:
                                srcs_anteriores[pasta] = (
                                    await self._obter_src_primeira_galeria_async(
                                        aba, timeout_ms=3000
                                    )
                                )
                            except Exception:
                                srcs_anteriores[pasta] = None
                            await self._selecionar_todos_uploads_para_prompt_async(
                                aba
                            )
                            await self._clicar_criar_flow_async(aba)
                            await self._deletar_ultima_imagem_uploads_flow_async(
                                aba
                            )
                            self._log(
                                f"  [Aba {num}/{total}] ✓ Criado!"
                            )
                        except Exception as e:
                            self._log(
                                f"  [Aba {num}/{total}] ✗ Erro: {e}"
                            )
                            erros.append((pasta.name, pasta))

                    await asyncio.gather(*[
                        _enviar_aba(
                            aba, pasta, indice + 1, len(abas_ok)
                        )
                        for indice, (aba, pasta, _) in enumerate(abas_ok)
                    ])

                    # ── Download imediato por ciclo ──────────────────────────────
                    # Cada aba baixa a imagem que acabou de gerar (a mais recente
                    # na galeria NESTE momento), antes que o próximo ciclo
                    # sobreponha com uma geração nova na mesma aba.
                    if abas_ok:
                        lote_pendente = [
                            (aba, pasta, posicoes_globais[pasta])
                            for aba, pasta, _ in abas_ok
                        ]
                        self._log(
                            f"\n  ⏳ Ciclo {ciclo_num}/{total_ciclos}: aguardando "
                            f"{cycle_interval:.0f}s para as imagens gerarem..."
                        )
                        await asyncio.sleep(cycle_interval)
                        self._log(
                            f"\n  📥 Baixando {len(lote_pendente)} imagem(ns) do ciclo {ciclo_num}..."
                        )

                        async def _baixar_ciclo(dl_aba, dl_pasta, pos):
                            self._log(f"  [{pos}] ↓ {dl_pasta.name}")
                            try:
                                ok_dl = await self._baixar_primeira_galeria_async(
                                    dl_aba, dl_pasta, pos,
                                    src_anterior=srcs_anteriores.get(dl_pasta)
                                )
                                if not ok_dl:
                                    erros.append((dl_pasta.name, dl_pasta))
                            except Exception as e:
                                self._log(f"  [{pos}] ⚠ Falha no download: {e}")
                                erros.append((dl_pasta.name, dl_pasta))

                        await asyncio.gather(*[
                            _baixar_ciclo(a, p, pos) for a, p, pos in lote_pendente
                        ])
                        downloads_pendentes.extend(lote_pendente)

        except Exception as e:
            erro_geral = str(e)
            self._log(f"{prefixo} ✗ Erro geral Playwright: {e}")
            existentes = {p for _, p in erros}
            for pasta in pastas_sel:
                if pasta not in existentes:
                    erros.append((pasta.name, pasta))

        itens_revisao = []
        erros_pastas = {p for _, p in erros}
        pastas_adicionadas = set()
        for _, pasta, pos in downloads_pendentes:
            if pasta in erros_pastas or pasta in pastas_adicionadas:
                continue
            arquivo = pasta / f"frameNew ({pos}).jpg"
            if arquivo.exists():
                itens_revisao.append({"pasta": pasta, "arquivo": arquivo, "pos": pos})
                pastas_adicionadas.add(pasta)
        return {
            "perfil": perfil["name"],
            "erros": erros,
            "itens_revisao": itens_revisao,
            "erro_geral": erro_geral,
        }

    def _mover_falhas_flow(self, erros):
        """
        Cria a pasta  WORK_DIR/_falhas_<timestamp>  e copia para lá
        a pasta de cada frame que não foi gerado com sucesso,
        mantendo todos os arquivos originais intactos.
        erros: list[(nome_str, pasta_path)]
        """
        if not erros:
            return

        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        falhas_dir = WORK_DIR / f"_falhas_{ts}"
        falhas_dir.mkdir(parents=True, exist_ok=True)
        self._log(f"\n  📁 Movendo {len(erros)} pasta(s) com falha → {falhas_dir.name}")

        for nome, pasta_src in erros:
            if not pasta_src or not pasta_src.exists():
                self._log(f"    ⚠ Pasta não encontrada: {nome}")
                continue
            destino = falhas_dir / pasta_src.name
            try:
                # Se já existe destino com o mesmo nome, remove antes de copiar
                if destino.exists():
                    shutil.rmtree(destino)
                shutil.copytree(str(pasta_src), str(destino))
                self._log(f"    ✓ {pasta_src.name}  →  _falhas_{ts}/")
            except Exception as e:
                self._log(f"    ✗ Erro ao copiar {nome}: {e}")

        self._log(f"  ✓ Pasta de falhas criada: {falhas_dir}")

    def _detectar_modelo_pasta(self, nome_pasta):
        """
        Identifica a qual modelo cadastrada uma pasta de trabalho pertence,
        a partir do nome da pasta (ex: '#1Aurora (4)', 'Aurora_video1',
        'aurora (5)').

        Estratégias, em ordem:
          1) Prefixo exato antes do primeiro '_' (comportamento original).
          2) Nome de modelo cadastrada que seja prefixo do nome da pasta
             (escolhendo o match mais longo, caso haja vários).
          3) Igual ao item 2, mas ignorando maiúsculas/minúsculas.
        Retorna None se nenhuma modelo cadastrada corresponder.
        """
        if not self.modelos:
            return None

        # 1) Prefixo antes do "_" (ex.: "Aurora_video1" -> "Aurora")
        prefixo = nome_pasta.split("_")[0]
        if prefixo in self.modelos:
            return prefixo

        # 2) Modelo cadastrada cujo nome é prefixo do nome da pasta
        melhor = None
        for nome in self.modelos.keys():
            if nome and nome_pasta.startswith(nome):
                if melhor is None or len(nome) > len(melhor):
                    melhor = nome
        if melhor:
            return melhor

        # 3) Mesmo teste, ignorando maiúsculas/minúsculas
        nome_pasta_lower = nome_pasta.lower()
        for nome in self.modelos.keys():
            if nome and nome_pasta_lower.startswith(nome.lower()):
                if melhor is None or len(nome) > len(melhor):
                    melhor = nome

        return melhor

    async def _preparar_aba_flow_async(self, page, imagens, prompt_texto):
        """
        FASE 1 — Envia imagens para a galeria Uploads, não diretamente no prompt.
        Ordem obrigatória no primeiro uso de cada referência:
        1) referência 1, 2) referência 2, 3) frameog da pasta.
        Sempre envia as 3 imagens (refs + frameog) — sem reutilização entre ciclos.
        """
        if len(imagens) < 3:
            raise Exception("o fluxo Mimic exige 2 referências + 1 frameog")

        refs = [str(Path(x)) for x in imagens[:-1]][:2]
        frameog = str(Path(imagens[-1]))

        self._log("    → Enviando referências para Uploads...")
        for idx, ref_path in enumerate(refs, start=1):
            self._log(f"    → [{idx}/3] referência {idx}: {Path(ref_path).name}")
            await self._upload_arquivo_para_galeria_async(page, ref_path)
            await asyncio.sleep(1.2)

        self._log(f"    → [3/3] frameog: {Path(frameog).name}")
        await self._upload_arquivo_para_galeria_async(page, frameog)
        await asyncio.sleep(1.2)

        # Tenta abrir o painel Uploads APÓS o envio das imagens, mas não
        # aborta a preparação se o Flow ainda estiver processando os uploads.
        # A seleção obrigatória acontece depois, na FASE 3, após o delay.
        try:
            await self._abrir_uploads_flow_async(page)
        except Exception as e:
            self._log(
                f"    ~ Uploads não abriu na preparação ({e}); "
                "vou tentar novamente na FASE 3 após o delay."
            )

        CAMPO = '[data-slate-editor="true"]'
        await page.wait_for_selector(CAMPO, timeout=15000)
        campo = page.locator(CAMPO).first
        self._log("    → Colando prompt...")
        await campo.click()
        await asyncio.sleep(0.5)
        await self._colar_prompt_async(page, prompt_texto)
        await asyncio.sleep(0.3)
        self._log("    ✓ Prompt pronto; imagens serão selecionadas em Uploads após o tempo configurado")

    # ── Mantém a versão síncrona como alias caso seja chamada em outro lugar ──
    def _preparar_aba_flow(self, page, imagens, prompt_texto):
        raise RuntimeError("Use _preparar_aba_flow_async via asyncio")

    # Seletor CSS exato do botão Enviar/Criar do Google Flow
    FLOW_SEND_BTN_SEL = (
        "#__next > div.sc-c7ee1759-1.jhwuTJ "
        "> div.sc-682f0b3f-1.cLCWIL "
        "> div > div > div > div "
        "> div.sc-26b30722-1.kZzgCz "
        "> div.sc-26b30722-10.eTAJIl "
        "> button.sc-e8425ea6-0.hOBPaw.sc-d3791a4f-0.sc-d3791a4f-4.sc-26b30722-5.ewGlDn.famhRe.jDvIwb"
    )

    # Seletor CSS do botão de enviar o prompt (atualizado)
    FLOW_PROMPT_SEND_BTN_SEL = (
        "#__next > div.sc-c7ee1759-1.jhwuTJ "
        "> div.sc-682f0b3f-1.cLCWIL "
        "> div > div > div > div "
        "> div.sc-26b30722-1.kZzgCz "
        "> div.sc-26b30722-10.eTAJIl "
        "> button.sc-e8425ea6-0.hOBPaw.sc-d3791a4f-0.sc-d3791a4f-4.sc-26b30722-5.ewGlDn.famhRe.jDvIwb"
    )

    async def _clicar_criar_flow_async(self, page):
        """
        FASE 3 — Clica no botão Enviar/Criar usando o seletor CSS exato
        capturado via DevTools. Fallback para a toolbar genérica caso o
        DOM mude.
        """
        self._log(f"    → Clicando em Criar...")
        try:
            btn = page.locator(self.FLOW_SEND_BTN_SEL).first
            await btn.wait_for(state="visible", timeout=8000)
            if await btn.get_attribute("aria-disabled") == "true":
                raise Exception("botão desabilitado")
            await btn.click()
            self._log(f"    ✓ Botão Criar clicado (seletor exato)")
            await asyncio.sleep(1.5)
        except Exception as e1:
            self._log(f"    ~ seletor exato falhou ({e1}), tentando toolbar genérica...")
            try:
                toolbar = page.locator("div.sc-26b30722-10").first
                btn2 = toolbar.locator("button").last
                await btn2.wait_for(state="visible", timeout=8000)
                if await btn2.get_attribute("aria-disabled") == "true":
                    raise Exception("botão desabilitado")
                await btn2.click()
                self._log(f"    ✓ Botão Criar clicado (toolbar genérica)")
                await asyncio.sleep(1.5)
            except Exception as e2:
                self._log(f"    ~ toolbar falhou ({e2}), tentando fallback JS...")
                clicado = await page.evaluate("""
                    () => {
                        const exact = document.querySelector(
                            '#__next > div.sc-c7ee1759-1.jhwuTJ'
                            + ' > div.sc-682f0b3f-1.cLCWIL'
                            + ' > div > div > div > div'
                            + ' > div.sc-26b30722-1.kZzgCz'
                            + ' > div.sc-26b30722-10.eTAJIl'
                            + ' > button.sc-e8425ea6-0.hOBPaw.sc-d3791a4f-0.sc-d3791a4f-4.sc-26b30722-5.ewGlDn.famhRe.jDvIwb'
                        );
                        if (exact && exact.getAttribute('aria-disabled') !== 'true') {
                            exact.click(); return 'ok-exact';
                        }
                        const toolbar = document.querySelector('div.sc-26b30722-10');
                        if (toolbar) {
                            const btns = [...toolbar.querySelectorAll('button')]
                                .filter(b => b.getAttribute('aria-disabled') !== 'true');
                            if (btns.length) { btns[btns.length - 1].click(); return 'ok-toolbar'; }
                        }
                        for (const b of document.querySelectorAll('button')) {
                            const txt = b.textContent.trim();
                            if ((txt === 'Criar' || txt === 'Create' || txt === 'Send') && b.getAttribute('aria-disabled') !== 'true') {
                                b.click(); return 'ok-text';
                            }
                        }
                        return 'not-found';
                    }
                """)
                if clicado == 'not-found':
                    self._log(f"    ⚠ Botão Criar não encontrado")
                else:
                    self._log(f"    ✓ Botão Criar clicado (fallback: {clicado})")
                await asyncio.sleep(1.5)

    def _clicar_criar_flow(self, page):
        raise RuntimeError("Use _clicar_criar_flow_async via asyncio")

    def _enviar_pasta_flow(self, page, imagens, prompt_texto, delay):
        """Mantido para compatibilidade — este fluxo agora é assíncrono."""
        raise RuntimeError("Use o fluxo assíncrono via _enviar_flow_async")

    async def _obter_src_primeira_galeria_async(
            self, page, timeout_ms=15000, diferente_de=None):
        """
        Faz polling no src da primeira imagem da galeria até encontrar um
        valor (e, se 'diferente_de' for passado, até que o src mude em
        relação ao valor anterior — ou seja, até a nova geração substituir
        a miniatura antiga). Mesma lógica usada para vídeos no Motion
        (_motion_obter_video_src_async), aplicada a imagens.
        """
        IMG_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-682f0b3f-0.iPxPxr "
            "> div.sc-e4f4e472-0.iUuqJB "
            "> div > div > div > div.sc-888a6226-2.iyGxUz "
            "> div > div "
            "> div:nth-child(1) > div > div > span > div > div > div > div > span > div > a > img"
        )
        img_el = page.locator(IMG_SEL).first
        limite = time.monotonic() + (timeout_ms / 1000)
        while time.monotonic() < limite:
            try:
                await img_el.wait_for(state="visible", timeout=3000)
                src = await img_el.get_attribute("src")
                if src and (not diferente_de or src != diferente_de):
                    return src
            except Exception:
                pass
            await asyncio.sleep(1)
        if diferente_de:
            raise RuntimeError(
                "A imagem gerada ainda não apareceu na galeria "
                "(src não mudou em relação à anterior)."
            )
        raise RuntimeError("Imagem da galeria não apareceu no seletor de saída.")

    async def _baixar_primeira_galeria_async(
            self, page, pasta: Path, pos: int = 1, src_anterior=None,
            timeout_ms=60000, destino=None):
        """
        Busca o src da primeira imagem gerada na galeria do Flow e faz o
        download autenticado (usando a sessão já logada do Playwright).
        Salva o arquivo como  <pasta>/frameNew (N).jpg  onde N é a posição global.

        Se 'src_anterior' for informado, aguarda (com polling, até
        'timeout_ms') o src da primeira imagem mudar antes de baixar —
        isso evita baixar a miniatura antiga enquanto a edição/geração
        ainda está em andamento no Flow.
        """
        destino = Path(destino) if destino else pasta / f"frameNew ({pos}).jpg"

        TODAS_MIDIAS_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-8d642504-0.hMSKOY "
            "> div.sc-559b4cd2-0.eEmtGh "
            "> nav.sc-559b4cd2-2.iKQMcG "
            "> button:nth-child(1)"
        )

        try:
            try:
                todas = page.locator(TODAS_MIDIAS_SEL).first
                await todas.wait_for(state="visible", timeout=5000)
                await todas.click()
                await asyncio.sleep(0.8)
                self._log(f"    → 'Todas as mídias' ativa")
            except Exception:
                pass

            if src_anterior:
                self._log(
                    "    → Aguardando a imagem gerada substituir a "
                    "anterior na galeria..."
                )
            else:
                self._log(f"    → Procurando primeira imagem da galeria...")

            try:
                src = await self._obter_src_primeira_galeria_async(
                    page, timeout_ms=timeout_ms, diferente_de=src_anterior
                )
            except RuntimeError as e:
                if src_anterior:
                    # Timeout esperando mudar: cai para o que tiver, com
                    # aviso, em vez de travar a edição indefinidamente.
                    self._log(f"    ⚠ {e} Tentando baixar o que estiver visível...")
                    return False
                else:
                    raise

            if not src:
                self._log(f"    ⚠ Imagem encontrada mas sem atributo src")
                return False

            self._log(f"    → src: {src[:80]}...")

            if src.startswith("/"):
                src = "https://labs.google" + src

            self._log(f"    → Baixando imagem autenticada...")
            response = await page.context.request.get(src)

            if response.status != 200:
                self._log(f"    ⚠ Download falhou (HTTP {response.status})")
                return False

            body = await response.body()
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(body)
            destino = self._converter_foto_celular(destino)
            self._log(f"    ✓ {destino.name} salvo em {pasta.name}  ({len(body)//1024} KB)")
            return True

        except Exception as e:
            self._log(f"    ⚠ Erro ao baixar galeria: {e}")
            return False

    def _baixar_primeira_galeria(self, page, pasta: Path):
        raise RuntimeError("Use _baixar_primeira_galeria_async via asyncio")

    def _sel(self, chave, padrao):
        """Retorna seletor salvo no config (pelo usuário) ou o padrão hardcoded."""
        return self.config.get("seletores", {}).get(chave, padrao)

    async def _abrir_uploads_flow_async(self, page):
        """
        Abre Uploads usando SOMENTE o seletor configurado em seletores.uploads_btn.
        Sem fallback por texto, aria, heurística visual ou padrão alternativo.
        Se o seletor não funcionar, o fluxo para com erro.
        """
        sel_uploads_btn = self.config.get("seletores", {}).get("uploads_btn", "").strip()
        if not sel_uploads_btn:
            raise RuntimeError("Seletor 'uploads_btn' não configurado. Capture/salve o botão Uploads na aba Seletores.")

        self._log("    → Abrindo Uploads pelo seletor configurado...")

        async def _tentar_clicar_uploads_btn():
            # 1. Tenta pelo texto/aria "Uploads" — estável independente de CSS
            for loc in [
                page.get_by_role("tab", name=re.compile(r"uploads?", re.I)),
                page.get_by_role("button", name=re.compile(r"uploads?", re.I)),
                page.locator("button, [role='tab'], [role='button']").filter(has_text=re.compile(r"^uploads?$", re.I)),
            ]:
                try:
                    el = loc.first
                    await el.wait_for(state="visible", timeout=2000)
                    await el.click(timeout=3000, force=True)
                    return "texto/aria"
                except Exception:
                    pass

            # 2. Usa o seletor salvo pelo usuário (CSS antigo ou __XYREL__)
            if sel_uploads_btn.startswith("__XYREL__"):
                coords = sel_uploads_btn[len("__XYREL__"):].split(",")
                cx_rel, cy_rel = float(coords[0]), float(coords[1])
                vp = page.viewport_size or {"width": 1280, "height": 800}
                await page.mouse.click(cx_rel * vp["width"], cy_rel * vp["height"])
                return "xyrel"
            else:
                btn = page.locator(sel_uploads_btn).first
                await btn.wait_for(state="visible", timeout=9000)
                try:
                    await btn.scroll_into_view_if_needed(timeout=1500)
                except Exception:
                    pass
                await btn.click(timeout=5000, force=True)
                return "css"

        try:
            metodo = await _tentar_clicar_uploads_btn()
            await asyncio.sleep(0.8)
            self._log(f"    ✓ Uploads clicado ({metodo})")
            return True
        except Exception as e:
            raise RuntimeError(
                "Falhou ao clicar no seletor configurado 'uploads_btn'. "
                f"Seletor usado: {sel_uploads_btn} | Erro: {str(e).splitlines()[0]}"
            ) from e

    def _abrir_uploads_flow(self, page):
        raise RuntimeError("Use _abrir_uploads_flow_async via asyncio")

    async def _obter_uploads_visiveis_por_posicao_async(self, page):
        """
        Retorna os thumbnails visíveis do painel Uploads por posição de tela,
        sem depender dos seletores CSS longos/dinâmicos do Google Flow.

        A estratégia procura um container visível cujo texto contenha
        "Uploads" e imagens grandes o suficiente para serem thumbnails,
        preservando a ordem visual da galeria.
        """
        sel_painel = self._sel("uploads_painel", "")
        rects = await page.evaluate(
            """
            (selPainel) => {
                const MIN_W = 36;
                const MIN_H = 36;

                const visible = (el) => {
                    if (!el) return false;
                    const r = el.getBoundingClientRect();
                    const st = window.getComputedStyle(el);
                    return (
                        r.width >= MIN_W &&
                        r.height >= MIN_H &&
                        r.bottom > 0 &&
                        r.right > 0 &&
                        r.top < window.innerHeight &&
                        r.left < window.innerWidth &&
                        st.visibility !== 'hidden' &&
                        st.display !== 'none' &&
                        Number(st.opacity || 1) > 0
                    );
                };

                const imgCandidates = [...document.querySelectorAll('img')]
                    .map((img, idx) => {
                        const r = img.getBoundingClientRect();
                        return {
                            el: img,
                            idx,
                            x: r.left,
                            y: r.top,
                            width: r.width,
                            height: r.height,
                            cx: r.left + r.width / 2,
                            cy: r.top + r.height / 2,
                            area: r.width * r.height,
                            src: img.currentSrc || img.src || ''
                        };
                    })
                    .filter(item => {
                        const img = item.el;
                        if (!visible(img)) return false;
                        const src = item.src.toLowerCase();
                        if (src.startsWith('data:image/svg')) return false;
                        if (item.width < MIN_W || item.height < MIN_H) return false;
                        // Evita ícones/logos muito pequenos; thumbnails reais
                        // normalmente têm área bem maior que botões/avatares.
                        if (item.area < 1800) return false;
                        return true;
                    });

                // Se o usuário salvou um seletor customizado para o painel,
                // usa diretamente sem precisar buscar por texto.
                let chosen;
                if (selPainel) {
                    try {
                        const painelEl = document.querySelector(selPainel);
                        if (painelEl) {
                            chosen = imgCandidates.filter(item => painelEl.contains(item.el));
                        }
                    } catch(e) {}
                }

                if (!chosen || chosen.length === 0) {
                    // Fallback: busca por texto "uploads" no container
                    const containers = [...document.querySelectorAll(
                        'aside, section, dialog, [role="dialog"], [role="tabpanel"], [aria-label], div'
                    )]
                        .filter(el => {
                            const r = el.getBoundingClientRect();
                            if (r.width < 120 || r.height < 120) return false;
                            const st = window.getComputedStyle(el);
                            if (st.visibility === 'hidden' || st.display === 'none') return false;
                            const txt = (el.innerText || el.textContent || el.getAttribute('aria-label') || '').toLowerCase();
                            return txt.includes('uploads') || txt.includes('upload');
                        })
                        .map(el => {
                            const r = el.getBoundingClientRect();
                            const imgs = imgCandidates.filter(item => el.contains(item.el));
                            return { el, imgs, area: r.width * r.height, x: r.left, y: r.top };
                        })
                        .filter(c => c.imgs.length > 0)
                        .sort((a, b) => {
                            if (a.imgs.length !== b.imgs.length) return b.imgs.length - a.imgs.length;
                            return a.area - b.area;
                        });
                    chosen = containers.length ? containers[0].imgs : imgCandidates;
                }

                // Remove duplicados por centro aproximado, comum quando há imagens
                // sobrepostas/preview lazy-load.
                const seen = new Set();
                chosen = chosen.filter(item => {
                    const key = `${Math.round(item.cx / 4)}:${Math.round(item.cy / 4)}`;
                    if (seen.has(key)) return false;
                    seen.add(key);
                    return true;
                });

                // Ordem visual: cima->baixo, esquerda->direita. Depois o Python
                // clica no inverso: 3ª -> 2ª -> 1ª.
                chosen.sort((a, b) => {
                    const rowA = Math.round(a.y / 12);
                    const rowB = Math.round(b.y / 12);
                    if (rowA !== rowB) return rowA - rowB;
                    return a.x - b.x;
                });

                return chosen.map(({x, y, width, height, cx, cy, idx}) => ({
                    x, y, width, height, cx, cy, idx
                }));
            }
            """,
            sel_painel
        )
        return rects or []

    async def _clicar_uploads_visualmente_em_ordem_async(
            self, page, quantidade_esperada=3):
        """
        Seleciona as 3 imagens recém-enviadas clicando sempre nas ÚLTIMAS 3
        da galeria por ordem visual (cima→baixo, esq→dir).

        Estratégia: obtém todos os thumbnails visíveis do painel de uploads,
        ordena-os visualmente e clica nos últimos 3 em ordem inversa
        (3ª→2ª→1ª do final), que correspondem às 3 imagens mais recentes.

        Isso evita o problema de UUIDs/seletores capturados em sessões
        anteriores que apontam para imagens antigas.
        """
        self._log("    → Selecionando as 3 últimas imagens enviadas (por posição visual)...")

        # Aguarda os thumbnails aparecerem na galeria após o upload
        await asyncio.sleep(1.0)

        # Obtém todos os thumbnails visíveis ordenados por posição visual
        rects = await self._obter_uploads_visiveis_por_posicao_async(page)

        if len(rects) < quantidade_esperada:
            # Tenta mais uma vez com espera extra
            await asyncio.sleep(1.5)
            rects = await self._obter_uploads_visiveis_por_posicao_async(page)

        if len(rects) < quantidade_esperada:
            raise RuntimeError(
                f"Galeria de uploads tem apenas {len(rects)} thumbnail(s) visível(is); "
                f"esperava ao menos {quantidade_esperada}. "
                "Verifique se o painel de Uploads está aberto e as imagens foram enviadas."
            )

        # Pega as primeiras `quantidade_esperada` imagens da lista ordenada visualmente
        # — o Flow exibe as mais recentes no topo/início, então índice 0..N-1 = mais novas
        ultimas = rects[:quantidade_esperada]

        # Clica em ordem inversa: última → penúltima → antepenúltima
        # (equivalente a: 3ª→2ª→1ª mais recentes)
        ordem_clique = list(reversed(ultimas))
        labels = [f"{quantidade_esperada - i}ª" for i in range(quantidade_esperada)]

        async def _clicar_por_posicao(label, rect, idx):
            """Clica no centro do thumbnail usando coordenadas de tela."""
            mods = ["Control"]
            x = rect["cx"]
            y = rect["cy"]
            self._log(f"    [debug] {label}: clicando em ({x:.0f}, {y:.0f})")
            await page.keyboard.down("Control")
            await page.mouse.click(x, y)
            await page.keyboard.up("Control")

        try:
            for idx, (label, rect) in enumerate(zip(labels, ordem_clique)):
                await _clicar_por_posicao(label, rect, idx)
                await asyncio.sleep(0.35)
                self._log(f"    ✓ Imagem {label} (mais recente) clicada")
        except Exception as e:
            raise RuntimeError(
                "Falhou ao clicar nas últimas imagens da galeria. "
                f"Erro: {str(e).splitlines()[0]}"
            ) from e

        await asyncio.sleep(0.35)
        return quantidade_esperada

    async def _upload_arquivo_para_galeria_async(self, page, arquivo):
        """
        Envia um arquivo para a galeria Uploads via input[type=file].
        O arquivo é enviado individualmente para preservar a ordem exata.

        Estratégia de busca do input (em ordem de prioridade):
        1. input[type=file] dentro do container FLOW_UPLOAD_CONTAINER_SEL
        2. Qualquer input[type=file] da página (fallback genérico, iterado de
           trás para frente)
        3. file-chooser aberto por clique em botão com palavras-chave de upload
        """
        arquivo = str(Path(arquivo))
        ultimo_erro = None

        # ── Prioridade 1: input dentro do container de uploads ────────────────
        try:
            sel_container = self._sel("upload_container", FLOW_UPLOAD_CONTAINER_SEL)
            container_input = page.locator(
                f'{sel_container} input[type="file"]'
            )
            count_container = await container_input.count()
            if count_container > 0:
                await container_input.first.set_input_files(arquivo, timeout=8000)
                await asyncio.sleep(1.0)
                self._log(
                    f"    ✓ Upload enviado via container de uploads: "
                    f"{Path(arquivo).name}"
                )
                return True
        except Exception as e:
            ultimo_erro = e
            self._log(
                f"    ~ input no container falhou ({e}), tentando fallback genérico..."
            )

        # ── Prioridade 2: qualquer input[type=file] da página ─────────────────
        inputs = page.locator('input[type="file"]')
        try:
            count = await inputs.count()
        except Exception:
            count = 0

        for idx in reversed(range(count)):
            try:
                await inputs.nth(idx).set_input_files(arquivo, timeout=8000)
                await asyncio.sleep(1.0)
                self._log(f"    ✓ Upload enviado para galeria: {Path(arquivo).name}")
                return True
            except Exception as e:
                ultimo_erro = e

        # Fallback: espera file chooser ao clicar em um botão provável de upload.
        try:
            async with page.expect_file_chooser(timeout=5000) as fc_info:
                clicked = await page.evaluate("""
                    () => {
                        const words = ['upload', 'enviar', 'arquivo', 'imagem', 'mídia', 'media'];
                        const nodes = [...document.querySelectorAll('button, [role="button"]')];
                        for (const n of nodes.reverse()) {
                            const txt = (n.innerText || n.textContent || n.getAttribute('aria-label') || '').toLowerCase();
                            if (words.some(w => txt.includes(w))) {
                                n.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                if not clicked:
                    raise Exception("botão de upload não encontrado")
            fc = await fc_info.value
            await fc.set_files(arquivo)
            await asyncio.sleep(1.0)
            self._log(f"    ✓ Upload enviado via file chooser: {Path(arquivo).name}")
            return True
        except Exception as e:
            raise Exception(f"falha ao enviar {Path(arquivo).name} para Uploads: {e or ultimo_erro}")

    def _upload_arquivo_para_galeria(self, page, arquivo):
        raise RuntimeError("Use _upload_arquivo_para_galeria_async via asyncio")

    async def _selecionar_uploads_visiveis_async(
            self, page, quantidade_esperada=None):
        """
        Seleção de uploads por posição visual automática.
        Clica sempre nas últimas `quantidade_esperada` imagens da galeria.
        Não depende de seletores configurados.
        """
        if quantidade_esperada is not None:
            return await self._clicar_uploads_visualmente_em_ordem_async(
                page, quantidade_esperada=quantidade_esperada
            )
        self._log("    · Seleção visual desativada; nenhum upload será selecionado sem seletor configurado")
        return 0

    async def _limpar_uploads_pendentes_flow_async(self, page):
        """Remove resíduos da galeria compartilhada antes da próxima pasta."""
        await self._abrir_uploads_flow_async(page)
        await asyncio.sleep(0.5)
        total = await self._selecionar_uploads_visiveis_async(page)
        if not total:
            self._log("    ✓ Galeria Uploads limpa")
            await self._voltar_galeria_principal_async(page)
            return
        self._log(f"    → Removendo {total} upload(s) pendente(s)...")
        await page.keyboard.press("Delete")
        await asyncio.sleep(0.8)
        restantes = len(await self._obter_uploads_visiveis_por_posicao_async(page))
        if restantes:
            raise RuntimeError(
                f"Nao foi possivel limpar a galeria Uploads "
                f"({restantes} item(ns) restante(s))."
            )
        self._log("    ✓ Residuos de Uploads removidos")
        await self._voltar_galeria_principal_async(page)

    async def _voltar_galeria_principal_async(self, page):
        """
        Clica no botão 'Voltar à galeria' configurado na aba Seletores.
        Fallback: navega pela URL removendo '/tools' se o seletor não estiver configurado.
        """
        sel = self.config.get("seletores", {}).get("voltar_galeria", "").strip()
        if sel:
            try:
                self._log("    → Clicando em 'Voltar à galeria'...")
                if sel.startswith("__XYREL__"):
                    coords = sel[len("__XYREL__"):].split(",")
                    vp = page.viewport_size or {"width": 1280, "height": 800}
                    x = float(coords[0]) * vp["width"]
                    y = float(coords[1]) * vp["height"]
                    await page.mouse.click(x, y)
                else:
                    btn = page.locator(sel).first
                    await btn.wait_for(state="visible", timeout=7000)
                    await btn.click(timeout=5000)
                await asyncio.sleep(0.6)
                self._log("    ✓ Voltou à galeria principal")
                return
            except Exception as e:
                self._log(f"    ⚠ Seletor 'voltar_galeria' falhou ({e}); usando fallback por URL")
        # Fallback: remove '/tools' da URL
        if page.url.rstrip("/").endswith("/tools"):
            await page.goto(page.url.rstrip("/")[:-6])
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            self._log("    ✓ Voltou à galeria via URL (fallback)")

    async def _selecionar_todos_uploads_para_prompt_async(self, page):
        """
        Depois do delay, abre Uploads e seleciona as 3 imagens na ordem
        necessária para o prompt: 3ª/última -> 2ª -> 1ª.
        Usa somente seletores configurados. Se falhar, para.
        """
        self._log("    → Selecionando uploads na ordem 3 → 2 → 1...")

        total_itens = await self._clicar_uploads_visualmente_em_ordem_async(
            page, quantidade_esperada=3
        )
        self._log(f"    → {total_itens} upload(s) clicado(s) por seletor configurado")

        self._log("    ✓ Uploads selecionados na ordem configurada")

    def _selecionar_todos_uploads_para_prompt(self, page):
        raise RuntimeError("Use _selecionar_todos_uploads_para_prompt_async via asyncio")

    async def _selecionar_upload_edicao_async(self, page):
        """
        Fluxo de edição: clica APENAS na 1ª imagem (a mais recente) segurando Shift.
        """
        self._log("    → Selecionando 1ª imagem para edição (Shift+clique)...")

        await asyncio.sleep(1.0)
        rects = await self._obter_uploads_visiveis_por_posicao_async(page)

        if not rects:
            await asyncio.sleep(1.5)
            rects = await self._obter_uploads_visiveis_por_posicao_async(page)

        if not rects:
            raise RuntimeError(
                "Nenhum thumbnail visível encontrado na galeria de uploads."
            )

        rect = rects[0]  # a mais recente
        x, y = rect["cx"], rect["cy"]
        self._log(f"    [debug] Ctrl+clique em ({x:.0f}, {y:.0f})")
        await page.keyboard.down("Control")
        await page.mouse.click(x, y)
        await page.keyboard.up("Control")
        await asyncio.sleep(0.35)
        self._log("    ✓ Imagem selecionada para edição")

    async def _deletar_ultima_imagem_uploads_flow_async(self, page):
        """
        Após o envio as imagens continuam selecionadas.
        Basta reabrir Uploads e apertar Delete.
        """
        try:
            self._log("    → Deletando uploads (já selecionados)...")
            await page.keyboard.press("Delete")
            await asyncio.sleep(0.5)
            self._log("    ✓ Uploads deletados")
            return True
        except Exception as e:
            self._log(f"    ⚠ Não foi possível deletar os uploads: {e}")
            return False

    def _deletar_ultima_imagem_uploads_flow(self, page):
        raise RuntimeError("Use _deletar_ultima_imagem_uploads_flow_async via asyncio")

    async def _limpar_uploads_flow_async(self, page):
        """Compatibilidade: no fluxo novo, limpa apenas o último frameog enviado."""
        return await self._deletar_ultima_imagem_uploads_flow_async(page)

    def _limpar_uploads_flow(self, page):
        raise RuntimeError("Use _limpar_uploads_flow_async via asyncio")

    async def _colar_prompt_async(self, page, texto):
        """
        Insere o prompt diretamente no editor sem usar o clipboard global.
        Isso permite que vários perfis Flow trabalhem simultaneamente.
        """
        await page.keyboard.insert_text(texto)
        await asyncio.sleep(0.3)
        self._log("    ✓ Prompt inserido diretamente")

    def _colar_prompt(self, page, texto):
        raise RuntimeError("Use _colar_prompt_async via asyncio")

    def _drop_image_flow(self, page, campo, img_path):
        """
        Envia a imagem para o editor do Flow usando 3 estratégias em sequência.
        Estratégia 1: Clipboard BMP via win32clipboard + Ctrl+V  (mais confiável no Flow)
        Estratégia 2: DragEvent via JS com DataTransfer
        Estratégia 3: page.set_input_files no input nativo do Flow (se encontrado)

        O cache _estrategia_ok acelera uploads subsequentes na mesma aba.
        NÃO depende de confirmação visual — prossegue após execução sem erro.
        """
        import base64

        img_path = Path(img_path)
        ext  = img_path.suffix.lower().lstrip(".")
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png",  "webp": "image/webp",
                "bmp": "image/bmp"}.get(ext, "image/jpeg")
        fname = img_path.name

        favorita = getattr(self, '_estrategia_ok', None)

        # ── Estratégia 1: Clipboard BMP + Ctrl+V ─────────────────────────────
        if favorita in (None, 1):
            try:
                import win32clipboard
                import io
                from PIL import Image as PILImage

                img_pil  = PILImage.open(img_path).convert("RGB")
                buf      = io.BytesIO()
                img_pil.save(buf, format="BMP")
                bmp_data = buf.getvalue()[14:]  # remove cabeçalho BITMAPFILEHEADER

                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, bmp_data)
                win32clipboard.CloseClipboard()
                time.sleep(0.15)

                # Garante foco no campo antes de colar
                campo.click()
                time.sleep(0.2)
                page.keyboard.press("Control+v")
                time.sleep(0.6)

                self._log(f"    ✓ Imagem enviada via clipboard (Ctrl+V)")
                self._estrategia_ok = 1
                return
            except Exception as e:
                self._log(f"    ~ Clipboard falhou ({e}), tentando DragEvent JS...")
                if favorita == 1:
                    self._estrategia_ok = None

        # ── Estratégia 2: DragEvent via JS ───────────────────────────────────
        if favorita in (None, 2):
            try:
                with open(img_path, "rb") as f:
                    raw = f.read()
                b64 = base64.b64encode(raw).decode()

                js_drop = f"""
                (function() {{
                    const b64  = "{b64}";
                    const mime = "{mime}";
                    const fname= "{fname}";

                    const byteChars = atob(b64);
                    const byteArr   = new Uint8Array(byteChars.length);
                    for (let i = 0; i < byteChars.length; i++) {{
                        byteArr[i] = byteChars.charCodeAt(i);
                    }}
                    const blob = new Blob([byteArr], {{type: mime}});
                    const file = new File([blob], fname, {{type: mime, lastModified: Date.now()}});

                    const dt = new DataTransfer();
                    dt.items.add(file);

                    const el = document.querySelector('[data-slate-editor="true"]');
                    if (!el) return 'editor not found';

                    el.focus();
                    const rect = el.getBoundingClientRect();
                    const cx   = rect.left + rect.width  / 2;
                    const cy   = rect.top  + rect.height / 2;

                    ['dragenter','dragover','drop'].forEach(evtName => {{
                        const evt = new DragEvent(evtName, {{
                            bubbles: true, cancelable: true,
                            clientX: cx, clientY: cy,
                            dataTransfer: dt
                        }});
                        el.dispatchEvent(evt);
                    }});
                    return 'ok';
                }})()
                """
                result = page.evaluate(js_drop)
                time.sleep(0.8)
                if result == 'ok':
                    self._log(f"    ✓ Imagem enviada via DragEvent JS")
                    self._estrategia_ok = 2
                    return
                else:
                    self._log(f"    ~ DragEvent JS retornou: {result}, tentando input nativo...")
                    if favorita == 2:
                        self._estrategia_ok = None
            except Exception as e:
                self._log(f"    ~ DragEvent JS falhou ({e}), tentando input nativo...")
                if favorita == 2:
                    self._estrategia_ok = None

        # ── Estratégia 3: set_input_files no input nativo do Flow ────────────
        try:
            # Busca qualquer input[type=file] já presente no DOM do Flow
            input_file = page.locator('input[type="file"]').first
            input_file.set_input_files(str(img_path), timeout=5000)
            time.sleep(0.5)
            self._log(f"    ✓ Imagem enviada via input nativo do Flow")
            self._estrategia_ok = 3
            return
        except Exception as e:
            self._log(f"    ✗ Todas as estratégias falharam: {e}")
            raise Exception(f"Não foi possível enviar a imagem '{fname}': {e}")


    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — FOTOS  (Flow com pasta única — substitui originais)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_tab_fotos(self):
        C = self.colors
        frame = tk.Frame(self.notebook, bg=C["BG"])
        self.notebook.add(frame, text="  Fotos  ")

        paned = tk.Frame(frame, bg=C["BG"])
        paned.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        left_col = tk.Frame(paned, bg=C["BG"])
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_col = tk.Frame(paned, bg=C["BG"])
        right_col.pack(side="left", fill="both", expand=True)

        # ── Pasta de fotos ────────────────────────────────────────────────────
        pf = ttk.LabelFrame(left_col, text="Pasta de fotos")
        pf.pack(fill="x", pady=(0, 8))

        pasta_row = tk.Frame(pf, bg=C["BG2"])
        pasta_row.pack(fill="x")
        self.fotos_pasta_var = tk.StringVar(value=self.config.get("fotos_pasta", ""))
        ttk.Entry(pasta_row, textvariable=self.fotos_pasta_var).pack(
            side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(pasta_row, text="Selecionar",
                   command=self._fotos_selecionar_pasta).pack(side="left")
        self.fotos_pasta_var.trace_add("write",
            lambda *a: self.config.update({"fotos_pasta": self.fotos_pasta_var.get()}))

        tk.Label(pf, text=(
            "Cada foto da pasta e enviada individualmente ao Flow.\n"
            "A imagem gerada é salva como novo arquivo (ex: foto_Modelo.jpg), sem sobrescrever o original."
        ), bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8), justify="left"
        ).pack(anchor="w", pady=(6, 2))

        opt_row = tk.Frame(pf, bg=C["BG2"])
        opt_row.pack(fill="x", pady=(4, 0))
        self.fotos_backup_var = tk.BooleanVar(value=False)  # backup desativado — arquivos novos são gerados

        # ── Checklist de modelos ──────────────────────────────────────────────
        mf = ttk.LabelFrame(left_col, text="Modelos com fotos de referência")
        mf.pack(fill="x", pady=(0, 8))

        mf_top = tk.Frame(mf, bg=C["BG2"])
        mf_top.pack(fill="x", pady=(0, 4))
        tk.Label(mf_top,
            text="Selecione as modelos cujas fotos de referência serão enviadas junto.",
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8), justify="left"
        ).pack(side="left", anchor="w")

        # botões Todas / Limpar
        mf_btns = tk.Frame(mf_top, bg=C["BG2"])
        mf_btns.pack(side="right")
        ttk.Button(mf_btns, text="Todas",
                   command=self._fotos_modelos_marcar_todas).pack(side="left", padx=(0, 4))
        ttk.Button(mf_btns, text="Limpar",
                   command=self._fotos_modelos_desmarcar_todas).pack(side="left")

        # frame com scroll para os checkboxes
        mf_scroll_wrap = tk.Frame(mf, bg=C["BG2"])
        mf_scroll_wrap.pack(fill="x")
        mf_canvas = tk.Canvas(mf_scroll_wrap, bg=C["BG2"], highlightthickness=0, height=220)
        mf_sb = ttk.Scrollbar(mf_scroll_wrap, orient="vertical", style="Vertical.TScrollbar", command=mf_canvas.yview)
        mf_canvas.configure(yscrollcommand=mf_sb.set)
        mf_sb.pack(side="right", fill="y")
        mf_canvas.pack(side="left", fill="both", expand=True)

        self._fotos_modelos_inner = tk.Frame(mf_canvas, bg=C["BG2"])
        mf_canvas_win = mf_canvas.create_window((0, 0), window=self._fotos_modelos_inner, anchor="nw")

        def _on_mf_configure(e):
            mf_canvas.configure(scrollregion=mf_canvas.bbox("all"))
        def _on_mf_width(e):
            mf_canvas.itemconfig(mf_canvas_win, width=e.width)
        self._fotos_modelos_inner.bind("<Configure>", _on_mf_configure)
        mf_canvas.bind("<Configure>", _on_mf_width)
        self._bind_canvas_mousewheel(mf_canvas, self._fotos_modelos_inner)

        self._fotos_modelos_canvas = mf_canvas
        self._fotos_modelos_vars = {}  # nome_modelo -> BooleanVar

        # ── Prompt ───────────────────────────────────────────────────────────
        prf = ttk.LabelFrame(left_col, text="Prompt")
        prf.pack(fill="both", expand=True, pady=(0, 8))

        mgmt_row = tk.Frame(prf, bg=C["BG2"])
        mgmt_row.pack(fill="x", pady=(0, 4))
        tk.Label(mgmt_row, text="Prompt:", bg=C["BG2"], fg=C["FG"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))
        self.fotos_prompt_sel_var = tk.StringVar(value=self.config.get("fotos_prompt_edit", "Padrao"))
        self.fotos_prompt_combo = ttk.Combobox(
            mgmt_row, textvariable=self.fotos_prompt_sel_var,
            state="readonly", width=18, font=("Segoe UI", 9))
        self.fotos_prompt_combo.pack(side="left", padx=(0, 4))
        self.fotos_prompt_combo.bind("<<ComboboxSelected>>",
            lambda e: self._fotos_on_prompt_select())
        ttk.Button(mgmt_row, text="Usar prompt do Flow",
                   command=self._fotos_copiar_prompt_flow).pack(side="left", padx=(0, 2))

        pt_frame = tk.Frame(prf, bg=C["BG2"])
        pt_frame.pack(fill="both", expand=True)
        pt_scroll = ttk.Scrollbar(pt_frame, style="Vertical.TScrollbar")
        pt_scroll.pack(side="right", fill="y")
        self.fotos_prompt_text = tk.Text(
            pt_frame, bg=C["BG3"], fg=C["FG"],
            insertbackground=C["ACC"], font=("Consolas", 8), relief="flat",
            borderwidth=0, wrap="word", yscrollcommand=pt_scroll.set, height=8)
        self.fotos_prompt_text.pack(fill="both", expand=True)
        pt_scroll.config(command=self.fotos_prompt_text.yview)

        # ── Lista de fotos ────────────────────────────────────────────────────
        lf = ttk.LabelFrame(right_col, text="Fotos na pasta")
        lf.pack(fill="both", expand=True)

        ls = ttk.Scrollbar(lf, style="Vertical.TScrollbar")
        ls.pack(side="right", fill="y")
        self.fotos_listbox = tk.Listbox(
            lf, bg=C["BG3"], fg=C["FG"],
            selectbackground=C["ACC"], selectforeground=C["FG"],
            font=("Consolas", 9), relief="flat", borderwidth=0,
            highlightthickness=0, yscrollcommand=ls.set,
            selectmode="extended", activestyle="none")
        self.fotos_listbox.pack(fill="both", expand=True)
        ls.config(command=self.fotos_listbox.yview)

        btn_row = tk.Frame(lf, bg=C["BG2"])
        btn_row.pack(fill="x", pady=(4, 0))
        ttk.Button(btn_row, text="\u21bb Atualizar",
                   command=self._fotos_atualizar_lista).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Todas",
                   command=lambda: self.fotos_listbox.select_set(0, "end")).pack(side="left")
        ttk.Button(btn_row, text="Limpar",
                   command=lambda: self.fotos_listbox.selection_clear(0, "end")).pack(side="left")

        # ── Timers ────────────────────────────────────────────────────────────
        tf = ttk.LabelFrame(right_col, text="Timers / Ciclos")
        tf.pack(fill="x", pady=(8, 0))

        def _timer_row(parent, label, var_attr, cfg_key, default, hint):
            row = tk.Frame(parent, bg=C["BG2"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, bg=C["BG2"], fg=C["FG"],
                     font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
            var = tk.StringVar(value=self.config.get(cfg_key, default))
            setattr(self, var_attr, var)
            ttk.Entry(row, textvariable=var, width=6).pack(side="left")
            var.trace_add("write",
                lambda *a, k=cfg_key, v=var: self.config.update({k: v.get()}))
            tk.Label(row, text=hint, bg=C["BG2"], fg=C["FG2"],
                     font=("Segoe UI", 8)).pack(side="left", padx=(6, 0))

        _timer_row(tf, "Perfis simultaneos:",
                   "fotos_max_parallel_profiles", "fotos_max_parallel_profiles", "0", "(0 = todos ativos)")
        _timer_row(tf, "Aguardar imagens carregarem (s):",
                   "fotos_delay", "fotos_delay", "10", "(apos enviar a foto)")
        _timer_row(tf, "Intervalo entre ciclos (s):",
                   "fotos_cycle_interval", "fotos_cycle_interval", "60",
                   "(pausa apos cada lote)")
        _timer_row(tf, "Abas por perfil/ciclo:",
                   "fotos_sends_per_cycle", "fotos_sends_per_cycle", "3",
                   "(quantas abas cada perfil usa ao mesmo tempo)")

        # ── Ações ─────────────────────────────────────────────────────────────
        actions = tk.Frame(frame, bg=C["BG"])
        actions.pack(fill="x", padx=20, pady=(8, 12))
        tk.Label(actions,
            text="Os perfis ativos são abertos automaticamente; faça login uma vez em cada sessão se necessário.",
            bg=C["BG"], fg=C["WARN"], font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(0, 6))
        ttk.Button(actions, text="Enviar fotos para todos os perfis ativos",
                   style="Accent.TButton",
                   command=self._fotos_enviar_thread).pack(side="left")

        self._fotos_reload_prompt_combo()
        self._fotos_atualizar_lista()
        self._fotos_rebuild_modelos_checklist()

    # Fotos helpers

    def _fotos_selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecionar pasta de fotos")
        if pasta:
            self.fotos_pasta_var.set(pasta)
            self._fotos_atualizar_lista()

    def _fotos_atualizar_lista(self):
        self.fotos_listbox.delete(0, "end")
        pasta_str = self.fotos_pasta_var.get().strip()
        if not pasta_str or not os.path.isdir(pasta_str):
            return
        exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        fotos = sorted(
            f for f in Path(pasta_str).iterdir()
            if f.is_file() and f.suffix.lower() in exts
            and not f.name.endswith(".bak")
        )
        for f in fotos:
            self.fotos_listbox.insert("end", f"  {f.name}")

    def _fotos_rebuild_modelos_checklist(self):
        """Reconstrói os checkboxes de modelos no painel de fotos em colunas compactas."""
        C = self.colors
        inner = self._fotos_modelos_inner
        for w in inner.winfo_children():
            w.destroy()

        anteriores = {n: v.get() for n, v in self._fotos_modelos_vars.items()}
        self._fotos_modelos_vars = {}

        if not self.modelos:
            lbl = tk.Label(inner, text="Nenhuma modelo cadastrada. Vá à aba Configuração > Modelos.",
                           bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8))
            lbl.pack(anchor="w", pady=4)
            self._bind_widget_mousewheel_to_canvas(lbl, self._fotos_modelos_canvas)
            return

        cols = tk.Frame(inner, bg=C["BG2"])
        cols.pack(fill="x")
        self._bind_widget_mousewheel_to_canvas(cols, self._fotos_modelos_canvas)
        col_frames = []
        for _ in range(3):
            cf = tk.Frame(cols, bg=C["BG2"])
            cf.pack(side="left", fill="both", expand=True, padx=3)
            self._bind_widget_mousewheel_to_canvas(cf, self._fotos_modelos_canvas)
            col_frames.append(cf)

        for i, (nome, dados) in enumerate(self.modelos.items()):
            foto1 = dados.get("foto1", "")
            foto2 = dados.get("foto2", "")
            tem_refs = bool(foto1 or foto2)
            parent = col_frames[i % 3]
            row = tk.Frame(parent, bg=C["BG3"], bd=0, highlightthickness=1,
                           highlightbackground=C["BORDER"])
            row.pack(fill="x", pady=2, padx=1)
            self._bind_widget_mousewheel_to_canvas(row, self._fotos_modelos_canvas)

            var = tk.BooleanVar(value=anteriores.get(nome, False))
            self._fotos_modelos_vars[nome] = var

            cb = ttk.Checkbutton(row, text=nome, variable=var)
            cb.pack(side="left", padx=(6, 6), pady=4)
            self._bind_widget_mousewheel_to_canvas(cb, self._fotos_modelos_canvas)

            def _toggle_modelo(_event=None, v=var):
                v.set(not v.get())
                return "break"

            row.bind("<Button-1>", _toggle_modelo)

            for fp in [foto1, foto2]:
                if fp and PIL_AVAILABLE and os.path.isfile(fp):
                    try:
                        img = Image.open(fp)
                        img.thumbnail((34, 34))
                        photo = ImageTk.PhotoImage(img)
                        lbl = tk.Label(row, image=photo, bg=C["BG3"])
                        lbl.image = photo
                        lbl.pack(side="left", padx=1, pady=2)
                        lbl.bind("<Button-1>", _toggle_modelo)
                        self._bind_widget_mousewheel_to_canvas(lbl, self._fotos_modelos_canvas)
                    except Exception:
                        pass
                elif fp:
                    lbl = tk.Label(row, text="[?]", bg=C["BG3"], fg=C["ERR"],
                                   font=("Segoe UI", 7))
                    lbl.pack(side="left", padx=1)
                    lbl.bind("<Button-1>", _toggle_modelo)
                    self._bind_widget_mousewheel_to_canvas(lbl, self._fotos_modelos_canvas)

            if not tem_refs:
                lbl = tk.Label(row, text="sem refs", bg=C["BG3"],
                               fg=C["WARN"], font=("Segoe UI", 7))
                lbl.pack(side="left", padx=(4, 0))
                lbl.bind("<Button-1>", _toggle_modelo)
                self._bind_widget_mousewheel_to_canvas(lbl, self._fotos_modelos_canvas)

        self._fotos_modelos_canvas.update_idletasks()
        self._fotos_modelos_canvas.configure(
            scrollregion=self._fotos_modelos_canvas.bbox("all"))

    def _fotos_modelos_marcar_todas(self):
        for v in self._fotos_modelos_vars.values():
            v.set(True)

    def _fotos_modelos_desmarcar_todas(self):
        for v in self._fotos_modelos_vars.values():
            v.set(False)

    def _fotos_modelos_selecionadas(self):
        """Retorna lista de (nome, foto1_path, foto2_path) das modelos marcadas."""
        if not hasattr(self, "_fotos_modelos_vars"):
            return []
        resultado = []
        for nome, var in self._fotos_modelos_vars.items():
            if var.get():
                dados = self.modelos.get(nome, {})
                foto1 = dados.get("foto1", "")
                foto2 = dados.get("foto2", "")
                resultado.append((nome, foto1, foto2))
        return resultado

    def _fotos_reload_prompt_combo(self):
        nomes = list(self.prompts.keys())
        self.fotos_prompt_combo["values"] = nomes
        ativo = self.fotos_prompt_sel_var.get()
        if ativo not in nomes:
            ativo = nomes[0] if nomes else ""
            self.fotos_prompt_sel_var.set(ativo)
        self._fotos_on_prompt_select()

    def _fotos_on_prompt_select(self):
        nome = self.fotos_prompt_sel_var.get()
        self.config["fotos_prompt_edit"] = nome
        self.fotos_prompt_text.delete("1.0", "end")
        self.fotos_prompt_text.insert("end", self.prompts.get(nome, ""))

    def _fotos_copiar_prompt_flow(self):
        texto = self.prompt_text.get("1.0", "end").rstrip()
        self.fotos_prompt_text.delete("1.0", "end")
        self.fotos_prompt_text.insert("end", texto)

    def _fotos_enviar_thread(self):
        def _run():
            asyncio.run(self._fotos_enviar_async())
        threading.Thread(target=_run, daemon=True).start()

    async def _fotos_enviar_async(self):
        if not PLAYWRIGHT_AVAILABLE:
            self.after(0, lambda: messagebox.showerror("Erro",
                "Playwright nao instalado.\n"
                "Execute:\npip install playwright\nplaywright install chromium"))
            return

        pasta_str = self.fotos_pasta_var.get().strip()
        if not pasta_str or not os.path.isdir(pasta_str):
            self.after(0, lambda: messagebox.showerror(
                "Erro", "Selecione uma pasta de fotos valida."))
            return

        p_texto = self.fotos_prompt_text.get("1.0", "end").rstrip()
        if not p_texto:
            self.after(0, lambda: messagebox.showerror(
                "Erro", "O prompt esta vazio."))
            return

        exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        pasta = Path(pasta_str)
        todas_fotos = sorted(
            f for f in pasta.iterdir()
            if f.is_file() and f.suffix.lower() in exts
            and not f.name.endswith(".bak")
        )

        sel = self.fotos_listbox.curselection()
        fotos_sel = ([todas_fotos[i] for i in sel if i < len(todas_fotos)]
                     if sel else todas_fotos)

        if not fotos_sel:
            self.after(0, lambda: messagebox.showwarning(
                "Aviso", "Nenhuma foto encontrada na pasta."))
            return

        fotos_sel = self._deduplicar_caminhos_por_imagem(
            fotos_sel,
            imagem_resolver=lambda foto: Path(foto),
            label="foto"
        )
        if not fotos_sel:
            self.after(0, lambda: messagebox.showwarning(
                "Fotos", "Nenhuma foto única sobrou para enviar."))
            return

        perfis_todos = self._flow_perfis_ativos()
        if not perfis_todos:
            self.after(0, lambda: messagebox.showwarning(
                "Perfis Flow",
                "Marque pelo menos um perfil Flow como ativo (na aba Flow)."))
            return
        perfis, limite_perfis = self._limitar_perfis_ativos(
            perfis_todos,
            getattr(self, "fotos_max_parallel_profiles", None),
            padrao=0
        )
        if not perfis:
            self.after(0, lambda: messagebox.showwarning(
                "Perfis Flow",
                "O limite de perfis simultaneos deixou a fila vazia."))
            return

        try:
            delay_img = float(self.fotos_delay.get())
        except ValueError:
            delay_img = 10.0
        try:
            cycle_interval = float(self.fotos_cycle_interval.get())
        except ValueError:
            cycle_interval = 60.0
        try:
            sends_per_cycle = max(1, int(self.fotos_sends_per_cycle.get()))
        except ValueError:
            sends_per_cycle = 3

        fazer_backup = self.fotos_backup_var.get()

        # Modelos selecionadas com fotos de referência
        modelos_sel = self._fotos_modelos_selecionadas()

        # Se há modelos selecionadas, expande: cada foto × cada modelo
        # Cada item: (foto_path, nome_modelo, [ref1, ref2])
        # Se nenhuma modelo: item = (foto_path, None, [])
        if modelos_sel:
            # Agrupa por foto: [foto1_A, foto1_B, ..., foto2_A, foto2_B, ...]
            # Assim a mesma foto base não é enviada para perfis diferentes ao mesmo tempo.
            por_modelo = []
            for foto in fotos_sel:
                for nome_mod, ref1, ref2 in modelos_sel:
                    refs = [r for r in [ref1, ref2] if r and os.path.isfile(r)]
                    por_modelo.append((foto, nome_mod, refs))
            fotos_expandidas = por_modelo
        else:
            fotos_expandidas = [(foto, None, []) for foto in fotos_sel]

        distribuicoes = []
        if modelos_sel:
            # Agrupa por foto: cada foto vai para um único perfil com todos os modelos
            # fotos_expandidas = [foto1_A, foto1_B, foto1_C, foto2_A, foto2_B, foto2_C, ...]
            n_modelos = len(modelos_sel)
            n_fotos = len(fotos_sel)
            n_perfis = len(perfis)
            lotes = [[] for _ in perfis]
            for foto_idx in range(n_fotos):
                perfil_idx = foto_idx % n_perfis
                inicio = foto_idx * n_modelos
                lotes[perfil_idx].extend(fotos_expandidas[inicio:inicio + n_modelos])
            for perfil, lote in zip(perfis, lotes):
                if lote:
                    distribuicoes.append((perfil, lote))
        else:
            for indice, perfil in enumerate(perfis):
                lote = fotos_expandidas[indice::len(perfis)]
                if lote:
                    distribuicoes.append((perfil, lote))

        capacidade_simultanea = max(1, sends_per_cycle) * max(1, len(distribuicoes))
        self._log("\U0001f4f8 Iniciando Fotos em multiplos perfis...")
        self._log(f"   Perfis ativos : {len(perfis_todos)}")
        self._log(f"   Perfis em uso : {len(distribuicoes)}" + (f" de {limite_perfis}" if limite_perfis else ""))
        self._log(f"   Abas por perfil: {sends_per_cycle}")
        self._log(f"   Produção simult.: até {capacidade_simultanea} imagem(ns)")
        self._log(f"   Fotos totais  : {len(fotos_expandidas)}"
                  + (f" ({len(fotos_sel)} foto(s) × {len(modelos_sel)} modelo(s))" if modelos_sel else ""))
        for perfil, lote in distribuicoes:
            self._log(f"   {perfil['name']} (porta {perfil['port']}): {len(lote)} item(s)")

        resultados = await asyncio.gather(*[
            self._fotos_enviar_perfil_async(
                perfil, lote, p_texto,
                delay_img, cycle_interval, sends_per_cycle, fazer_backup)
            for perfil, lote in distribuicoes
        ])

        erros = []
        fotos_geradas = []
        for r in resultados:
            erros.extend(r.get("erros", []))
            fotos_geradas.extend(r.get("fotos_ok", []))

        total = len(fotos_expandidas)
        concluidos = total - len({f for f, _ in erros})
        msg = f"Concluido!\n{concluidos}/{total} foto(s) gerada(s)."
        if erros:
            msg += "\n\nErros em:\n" + "\n".join(
                dict.fromkeys(n for n, _ in erros))
        self.after(0, lambda: messagebox.showinfo("Fotos", msg))
        self.after(0, self._fotos_atualizar_lista)
        self._log("\u2500" * 50)

        # Envia todas as fotos geradas para a aba Revisão
        if fotos_geradas or erros:
            itens_revisao = [
                {"pasta": f.parent, "arquivo": f, "pos": i + 1}
                for i, f in enumerate(fotos_geradas)
            ]
            # Adiciona erros à revisão marcados para refazer
            pos_extra = len(fotos_geradas)
            vistos = set()
            for nome, foto_path in erros:
                chave = str(foto_path)
                if chave in vistos:
                    continue
                vistos.add(chave)
                pos_extra += 1
                pasta = foto_path.parent if isinstance(foto_path, Path) else Path(foto_path).parent
                itens_revisao.append({
                    "pasta": pasta,
                    "arquivo": None,
                    "pos": pos_extra,
                    "erro": True,
                })
            itens_revisao.sort(key=lambda item: item["pos"])
            self.after(0, lambda itens=itens_revisao: self._abrir_revisao(itens))

    async def _fotos_enviar_perfil_async(
            self, perfil, fotos, p_texto,
            delay_img, cycle_interval, sends_per_cycle, fazer_backup):
        porta = perfil["port"]
        projeto_url = perfil["url"]
        prefixo = f"[{perfil['name']}]"
        total = len(fotos)
        total_ciclos = (total + sends_per_cycle - 1) // sends_per_cycle
        erros = []
        fotos_ok = []  # fotos substituídas com sucesso
        erro_geral = None

        self._log(f"{prefixo} Projeto: {projeto_url}")
        self._log(f"{prefixo} Fotos: {total} | Ciclos: {total_ciclos}")

        try:
            try:
                self._flow_garantir_perfil_aberto(perfil)
            except Exception as exc:
                raise RuntimeError(
                    f"Nao foi possivel abrir o perfil '{perfil['name']}': "
                    f"{exc}"
                ) from exc

            async with async_playwright() as pw:
                try:
                    browser = await pw.chromium.connect_over_cdp(f"http://localhost:{porta}")
                except Exception as exc:
                    raise RuntimeError(
                        f"Nao foi possivel conectar a porta {porta}. "
                        f"O perfil '{perfil['name']}' foi aberto automaticamente, "
                        "mas a porta ainda nao respondeu."
                    ) from exc

                context = browser.contexts[0]
                abas_flow = self._obter_abas_flow_abertas(context, projeto_url)
                if abas_flow:
                    self._log(f"   Abas Flow reutilizadas: {len(abas_flow)}")

                for ciclo_idx in range(total_ciclos):
                    ciclo_num   = ciclo_idx + 1
                    inicio      = ciclo_idx * sends_per_cycle
                    fim         = min(inicio + sends_per_cycle, total)
                    ciclo_fotos = fotos[inicio:fim]
                    n_abas      = len(ciclo_fotos)

                    self._log(f"\n{'\u2500'*46}")
                    self._log(f"\U0001f504  CICLO {ciclo_num}/{total_ciclos}  \u2014  {n_abas} aba(s)  (foto {inicio+1}\u2013{fim} de {total})")
                    self._log(f"{'\u2500'*46}")

                    async def _abrir_aba(slot):
                        self._log(f"  \U0001f310 Abrindo aba {slot}/{n_abas}...")
                        nova = await context.new_page()
                        await nova.goto(projeto_url)
                        await nova.wait_for_load_state("networkidle", timeout=30000)
                        self._log(f"  \u2713 Aba {slot} pronta")
                        return nova

                    while len(abas_flow) < n_abas:
                        faltam = n_abas - len(abas_flow)
                        slots = list(range(len(abas_flow) + 1, len(abas_flow) + faltam + 1))
                        novas = await asyncio.gather(*[_abrir_aba(s) for s in slots])
                        abas_flow.extend(novas)

                    # FASE 1
                    self._log(f"\n  \U0001f4e4 FASE 1 \u2014 Upload + prompt simultaneo nas {n_abas} aba(s)...")

                    async def _preparar_slot_foto(tab_i, item_tuple):
                        foto_path, nome_mod, refs = item_tuple
                        aba = abas_flow[tab_i]
                        label = f"{foto_path.name}" + (f" [{nome_mod}]" if nome_mod else "")
                        self._log(f"\n  [Aba {tab_i+1}/{n_abas}] \U0001f4f7 {label}")
                        try:
                            await self._fotos_preparar_aba_async(aba, str(foto_path), p_texto, fotos_ref=refs)
                            return (aba, foto_path, nome_mod, True)
                        except Exception as e:
                            self._log(f"  [Aba {tab_i+1}] \u2717 Erro na preparacao: {e}")
                            erros.append((foto_path.name, foto_path))
                            return (aba, foto_path, nome_mod, False)

                    abas_info = await asyncio.gather(*[
                        _preparar_slot_foto(i, item) for i, item in enumerate(ciclo_fotos)
                    ])
                    abas_ok = [(aba, foto, nome_mod) for aba, foto, nome_mod, ok in abas_info if ok]

                    if abas_ok:
                        self._log(f"\n  \u23f3 FASE 2 \u2014 Aguardando {delay_img}s...")
                        await asyncio.sleep(delay_img)

                    self._log(f"\n  \U0001f680 FASE 3 \u2014 Enviando em {len(abas_ok)} aba(s)...")

                    srcs_anteriores_fotos = {}

                    async def _enviar_aba_foto(aba, foto, num, total_ok):
                        try:
                            self._log(f"\n  [Aba {num}/{total_ok}] \u2192 {foto.name}")
                            try:
                                srcs_anteriores_fotos[foto] = (
                                    await self._obter_src_primeira_galeria_async(
                                        aba, timeout_ms=3000
                                    )
                                )
                            except Exception:
                                srcs_anteriores_fotos[foto] = None
                            await self._selecionar_upload_edicao_async(aba)
                            await self._clicar_criar_flow_async(aba)
                            await self._deletar_ultima_imagem_uploads_flow_async(aba)
                            self._log(f"  [Aba {num}/{total_ok}] \u2713 Criado!")
                        except Exception as e:
                            self._log(f"  [Aba {num}/{total_ok}] \u2717 Erro: {e}")
                            erros.append((foto.name, foto))

                    await asyncio.gather(*[
                        _enviar_aba_foto(aba, foto, i + 1, len(abas_ok))
                        for i, (aba, foto, nome_mod) in enumerate(abas_ok)
                    ])

                    # FASE 4 download e substituicao
                    if abas_ok:
                        self._log(f"\n  \u23f3 Ciclo {ciclo_num}: aguardando {cycle_interval:.0f}s para gerar...")
                        await asyncio.sleep(cycle_interval)
                        self._log(f"\n  \U0001f4e5 Baixando e salvando {len(abas_ok)} foto(s)...")

                        async def _baixar_e_substituir(dl_aba, foto_orig, nome_mod, pos):
                            self._log(f"  [{pos}] \u2193 {foto_orig.name}" + (f" [{nome_mod}]" if nome_mod else ""))
                            try:
                                foto_saida = await self._fotos_baixar_e_substituir_async(
                                    dl_aba, foto_orig, pos, False, nome_mod,
                                    src_anterior=srcs_anteriores_fotos.get(foto_orig))
                                if foto_saida is None:
                                    erros.append((foto_orig.name, foto_orig))
                                else:
                                    fotos_ok.append(foto_saida)
                            except Exception as e:
                                self._log(f"  [{pos}] \u26a0 Falha: {e}")
                                erros.append((foto_orig.name, foto_orig))

                        await asyncio.gather(*[
                            _baixar_e_substituir(aba, foto, nome_mod, i + 1)
                            for i, (aba, foto, nome_mod) in enumerate(abas_ok)
                        ])

        except Exception as e:
            erro_geral = str(e)
            self._log(f"{prefixo} \u2717 Erro geral Playwright: {e}")
            existentes = {f for _, f in erros}
            for item in fotos:
                foto = item[0] if isinstance(item, tuple) else item
                if foto not in existentes:
                    erros.append((foto.name, foto))

        return {"perfil": perfil["name"], "erros": erros, "fotos_ok": fotos_ok, "erro_geral": erro_geral}

    async def _fotos_preparar_aba_async(self, page, foto_path, prompt_texto, fotos_ref=None):
        """
        FASE 1 — Envia imagens para a galeria Uploads, igual ao fluxo Flow.
        Com fotos_ref (ref1, ref2): envia ref1 → ref2 → foto_path sem abrir
        o painel antes, abre DEPOIS (mesmo comportamento de _preparar_aba_flow_async).
        Sem refs: abre o painel antes e envia só a foto (comportamento original).
        """
        refs_validas = [r for r in (fotos_ref or []) if r and os.path.isfile(r)]

        if refs_validas:
            # Fluxo com referências: NÃO abre Uploads antes — envia direto via
            # _upload_arquivo_para_galeria_async, igual ao Flow original.
            total = len(refs_validas) + 1
            self._log(f"    → Enviando {total} imagens para Uploads...")
            for idx, ref_path in enumerate(refs_validas, start=1):
                self._log(f"    → [{idx}/{total}] referência {idx}: {Path(ref_path).name}")
                await self._upload_arquivo_para_galeria_async(page, ref_path)
                await asyncio.sleep(1.2)
            self._log(f"    → [{total}/{total}] foto: {Path(foto_path).name}")
            await self._upload_arquivo_para_galeria_async(page, foto_path)
            await asyncio.sleep(1.2)
            # Abre o painel Uploads APÓS o envio de todas as imagens (igual ao Flow)
            await self._abrir_uploads_flow_async(page)
        else:
            # Fluxo sem referências: comportamento original
            await self._abrir_uploads_flow_async(page)
            self._log(f"    → [1/1] foto: {Path(foto_path).name}")
            await self._upload_arquivo_para_galeria_async(page, foto_path)
            await asyncio.sleep(1.2)

        CAMPO = '[data-slate-editor="true"]'
        await page.wait_for_selector(CAMPO, timeout=15000)
        campo = page.locator(CAMPO).first
        self._log("    → Colando prompt...")
        await campo.click()
        await asyncio.sleep(0.5)
        await self._colar_prompt_async(page, prompt_texto)
        await asyncio.sleep(0.3)
        self._log("    ✓ Imagens + prompt prontos")

    async def _fotos_baixar_e_substituir_async(
            self, page, foto_orig: Path, pos: int, fazer_backup: bool,
            nome_modelo: str = None, src_anterior=None):
        IMG_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-682f0b3f-0.iPxPxr "
            "> div.sc-e4f4e472-0.iUuqJB "
            "> div > div > div > div.sc-888a6226-2.iyGxUz "
            "> div > div "
            "> div:nth-child(1) > div > div > span > div > div > div > div > span > div > a > img"
        )
        TODAS_MIDIAS_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-8d642504-0.hMSKOY "
            "> div.sc-559b4cd2-0.eEmtGh "
            "> nav.sc-559b4cd2-2.iKQMcG "
            "> button:nth-child(1)"
        )
        try:
            try:
                todas = page.locator(TODAS_MIDIAS_SEL).first
                await todas.wait_for(state="visible", timeout=5000)
                await todas.click()
                await asyncio.sleep(0.8)
            except Exception:
                pass

            if src_anterior:
                src = await self._obter_src_primeira_galeria_async(
                    page, timeout_ms=60000, diferente_de=src_anterior
                )
            else:
                img_el = page.locator(IMG_SEL).first
                await img_el.wait_for(state="visible", timeout=15000)
                src = await img_el.get_attribute("src")

            if not src:
                self._log("    \u26a0 Sem src na imagem gerada")
                return None

            if src.startswith("/"):
                src = "https://labs.google" + src

            response = await page.context.request.get(src)
            if response.status != 200:
                self._log(f"    \u26a0 Download falhou (HTTP {response.status})")
                return None

            body = await response.body()

            if fazer_backup and foto_orig.exists():
                backup = foto_orig.with_suffix(f"{foto_orig.suffix}.bak")
                shutil.copy2(foto_orig, backup)

            foto_orig.write_bytes(body)
            foto_saida = self._converter_foto_celular(foto_orig)
            self._log(f"    \u2713 Salva/convertida: {foto_saida.name}  ({len(body)//1024} KB)")
            return foto_saida

        except Exception as e:
            self._log(f"    \u26a0 Erro ao baixar/salvar: {e}")
            return None

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — REVISAO
    # ══════════════════════════════════════════════════════════════════════════
    def _build_tab_revisao(self):
        C = self.colors
        self._revisao_frame = tk.Frame(self.notebook, bg=C["BG"])
        self.notebook.add(self._revisao_frame, text="  Revisão  ")
        self._revisao_itens = []   # list de dicts com info de cada imagem
        self._revisao_vars  = []   # list de BooleanVar (checkbox marcada = refazer)
        self._revisao_widgets = [] # list de frames de card
        self._revisao_canvas = None
        self._revisao_inner  = None
        self._build_revisao_vazia()

    def _build_revisao_vazia(self):
        C = self.colors
        for w in self._revisao_frame.winfo_children():
            w.destroy()
        tk.Label(self._revisao_frame,
                 text="Nenhuma revisão disponível.\nExecute o processo Flow para gerar imagens.",
                 bg=C["BG"], fg=C["FG2"], font=("Segoe UI", 13)).pack(expand=True)

    def _revisao_sort_key(self, item):
        if item.get("editado"):
            prioridade = 0
        elif item.get("regenerado"):
            prioridade = 1
        elif item.get("erro"):
            prioridade = 2
        else:
            prioridade = 3
        momento = item.get("editado_em") or item.get("gerado_em") or 0
        return (prioridade, -float(momento), item.get("pos", 0))

    def _abrir_revisao(self, itens):
        """
        Chamado ao fim do processo com a lista de itens gerados.
        itens: list de dicts {"pasta": Path, "arquivo": Path, "pos": int}

        Se já houver itens de uma revisão anterior (ex: reprocessamento de
        imagens marcadas), mescla: os itens novos substituem os antigos com
        a mesma pasta, e os demais itens antigos são preservados no carrossel.
        """
        C = self.colors

        anteriores = getattr(self, "_revisao_itens", []) or []
        pastas_novas = {item["pasta"] for item in itens if item.get("pasta")}
        # Detecta pastas que existiam antes (são regenerações)
        pastas_anteriores = {it["pasta"] for it in anteriores if it.get("pasta")}
        for item in itens:
            if item.get("pasta") and item["pasta"] in pastas_anteriores:
                item["regenerado"] = True
                item["gerado_em"] = time.time()
        mesclados = [it for it in anteriores if it.get("pasta") and it["pasta"] not in pastas_novas]
        mesclados.extend(itens)
        mesclados.sort(key=self._revisao_sort_key)

        self._revisao_itens = mesclados
        self._revisao_vars  = [tk.BooleanVar(value=bool(item.get("erro"))) for item in mesclados]
        self._revisao_idx   = 0
        self._revisao_photo = None  # evita GC

        for w in self._revisao_frame.winfo_children():
            w.destroy()

        # ── Header ──
        header = tk.Frame(self._revisao_frame, bg=C["BG"])
        header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(header, text="REVISÃO", bg=C["BG"], fg=C["FG2"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        ttk.Button(header, text="✓ Refazer marcadas", style="Accent.TButton",
                   command=self._refazer_marcadas).pack(side="right")
        ttk.Button(header, text="Aprovadas -> Separação",
                   command=self._abrir_videos_da_revisao).pack(side="right", padx=(0, 6))
        ttk.Button(header, text="Desmarcar todas",
                   command=self._desmarcar_todas).pack(side="right", padx=(0, 6))
        ttk.Button(header, text="Marcar todas",
                   command=self._marcar_todas).pack(side="right", padx=(0, 4))
        ttk.Button(header, text="🗑 Deletar marcadas",
                   command=self._deletar_marcadas).pack(side="right", padx=(0, 4))
        tk.Frame(self._revisao_frame, bg=C["BORDER"], height=1).pack(fill="x")

        # ── Contador  (ex: 3 / 12) ──
        self._rev_contador = tk.Label(
            self._revisao_frame, bg=C["BG"], fg=C["FG2"],
            font=("Segoe UI Semibold", 11))
        self._rev_contador.pack(pady=(10, 0))

        # ── Imagem grande ──
        self._rev_img_label = tk.Label(
            self._revisao_frame, bg=C["BG3"],
            text="", cursor="hand2")
        self._rev_img_label.pack(expand=True, fill="both", padx=40, pady=(8, 0))

        # ── Barra inferior: seta ← | nome pasta | marcador | seta → ──
        bar = tk.Frame(self._revisao_frame, bg=C["BG"])
        bar.pack(fill="x", padx=40, pady=(8, 16))

        self._rev_btn_prev = ttk.Button(bar, text="◀", width=4,
                                        command=lambda: self._rev_navegar(-1))
        self._rev_btn_prev.pack(side="left")

        info = tk.Frame(bar, bg=C["BG"])
        info.pack(side="left", expand=True, fill="x", padx=12)

        self._rev_nome_label = tk.Label(info, bg=C["BG"], fg=C["FG"],
                                        font=("Segoe UI Semibold", 12))
        self._rev_nome_label.pack()
        self._rev_arq_label  = tk.Label(info, bg=C["BG"], fg=C["FG2"],
                                        font=("Segoe UI", 9))
        self._rev_arq_label.pack()
        self._rev_marca_label = tk.Label(info, bg=C["BG"],
                                         font=("Segoe UI Semibold", 11))
        self._rev_marca_label.pack(pady=(4, 0))

        self._rev_btn_next = ttk.Button(bar, text="▶", width=4,
                                        command=lambda: self._rev_navegar(+1))
        self._rev_btn_next.pack(side="right")

        # ── Atalhos de teclado (só enquanto a aba Revisão estiver ativa) ──
        self._revisao_frame.bind("<Left>",  lambda e: self._rev_navegar(-1))
        self._revisao_frame.bind("<Right>", lambda e: self._rev_navegar(+1))
        self._revisao_frame.bind("<Return>", lambda e: self._rev_toggle_atual())
        self._revisao_frame.bind("<space>",  lambda e: self._rev_toggle_atual())
        self._revisao_frame.bind("<e>", lambda e: self._rev_abrir_edicao())
        self._revisao_frame.bind("<E>", lambda e: self._rev_abrir_edicao())
        self._rev_img_label.bind("<Button-1>", lambda e: self._rev_toggle_atual())

        # foca o frame para receber teclas ao entrar na aba
        self._revisao_frame.focus_set()
        self.notebook.bind("<<NotebookTabChanged>>", self._rev_on_tab_change, add="+")

        self._rev_mostrar(0)

        # Vai para a aba Revisão
        try:
            tab_id = self.notebook.index(self._revisao_frame)
        except Exception:
            tab_id = 3
        self.notebook.select(tab_id)

    def _rev_on_tab_change(self, event):
        try:
            if self.notebook.index("current") == self.notebook.index(self._revisao_frame):
                self._revisao_frame.focus_set()
        except Exception:
            pass

    def _rev_mostrar(self, idx):
        """Renderiza o item idx no carrossel."""
        C = self.colors
        itens = self._revisao_itens
        n = len(itens)
        idx = max(0, min(idx, n - 1))
        self._revisao_idx = idx
        item = itens[idx]
        marcado = self._revisao_vars[idx].get()

        # Contador
        self._rev_contador.configure(text=f"{idx + 1}  /  {n}")

        # Imagem — ocupa todo o espaço disponível
        if not item.get("pasta"):
            self._rev_img_label.configure(
                image="", compound="center",
                text="⚠ Item sem pasta definida",
                fg=C["ERR"], font=("Segoe UI", 13))
            self._revisao_photo = None
            self._rev_nome_label.configure(text="(desconhecido)")
            self._rev_arq_label.configure(text="")
            self._rev_marca_label.configure(text="", fg=C["FG2"])
            self._rev_btn_prev.state(["disabled"] if idx == 0     else ["!disabled"])
            self._rev_btn_next.state(["disabled"] if idx == n - 1 else ["!disabled"])
            return
        frameog_path = item["pasta"] / "frameog.jpg"
        if item.get("erro") or not item["arquivo"]:
            if PIL_AVAILABLE and frameog_path.exists():
                try:
                    self._rev_img_label.update_idletasks()
                    w = max(self._revisao_frame.winfo_width() - 80,  600)
                    h = max(self._revisao_frame.winfo_height() - 200, 400)
                    img = Image.open(frameog_path)
                    img.thumbnail((w, h), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._rev_img_label.configure(
                        image=photo,
                        text="⚠ Falha na geração — mostrando frame original (frameog.jpg)"
                              "\nMarcada para refazer automaticamente",
                        fg=C["ERR"], compound="bottom")
                    self._rev_img_label._photo = photo
                    self._revisao_photo = photo
                except Exception:
                    self._rev_img_label.configure(
                        image="", compound="center",
                        text="⚠ Falha na geração\nMarcada para refazer automaticamente",
                        fg=C["ERR"], font=("Segoe UI", 13))
                    self._revisao_photo = None
            else:
                self._rev_img_label.configure(
                    image="", compound="center",
                    text="⚠ Falha na geração\nMarcada para refazer automaticamente",
                    fg=C["ERR"], font=("Segoe UI", 13))
                self._revisao_photo = None
        elif PIL_AVAILABLE and Path(item["arquivo"]).exists():
            try:
                self._rev_img_label.update_idletasks()
                w = max(self._revisao_frame.winfo_width() - 80,  600)
                h = max(self._revisao_frame.winfo_height() - 200, 400)
                img = Image.open(item["arquivo"])
                img.thumbnail((w, h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                extra_text = "🔄 Imagem regenerada" if item.get("regenerado") else ""
                self._rev_img_label.configure(
                    image=photo,
                    text=extra_text,
                    compound="bottom",
                    fg=C["INFO"],
                    font=("Segoe UI Semibold", 10))
                self._rev_img_label._photo = photo
                self._revisao_photo = photo
            except Exception:
                self._rev_img_label.configure(image="", text="[erro ao carregar imagem]",
                                              fg=C["FG2"], font=("Segoe UI", 12), compound="center")
        else:
            self._rev_img_label.configure(image="", text="[imagem não encontrada]",
                                          fg=C["FG2"], font=("Segoe UI", 12), compound="center")

        # Info
        nome_display = item["pasta"].name
        if item.get("regenerado"):
            nome_display = "🔄 " + nome_display
        elif item.get("erro"):
            nome_display = "⚠ " + nome_display
        self._rev_nome_label.configure(text=nome_display)
        if item.get("arquivo"):
            self._rev_arq_label.configure(text=item["arquivo"].name)
        elif frameog_path.exists():
            self._rev_arq_label.configure(text=f"(falha — origem: {frameog_path.name})")
        else:
            self._rev_arq_label.configure(text="(falha — sem arquivo gerado)")

        # Indicador de marcado / regenerado
        if marcado:
            self._rev_marca_label.configure(
                text="🔴  MARCADA PARA REFAZER  —  Enter para desmarcar",
                fg=C["ERR"])
            self._rev_img_label.configure(bg="#1f1116")
        elif item.get("regenerado"):
            self._rev_marca_label.configure(
                text="🔄  REGENERADA  —  Enter ou clique para marcar para refazer",
                fg=C["INFO"])
            self._rev_img_label.configure(bg="#101820")
        else:
            self._rev_marca_label.configure(
                text="Enter ou clique na imagem para marcar para refazer",
                fg=C["FG2"])
            self._rev_img_label.configure(bg=C["BG3"])

        # Setas
        self._rev_btn_prev.state(["disabled"] if idx == 0     else ["!disabled"])
        self._rev_btn_next.state(["disabled"] if idx == n - 1 else ["!disabled"])

    def _rev_navegar(self, delta):
        self._rev_mostrar(self._revisao_idx + delta)

    def _rev_toggle_atual(self):
        idx = self._revisao_idx
        self._revisao_vars[idx].set(not self._revisao_vars[idx].get())
        self._rev_mostrar(idx)

    def _rev_abrir_edicao(self):
        """
        Abre um campo para digitar um prompt de edição.
        Ao confirmar, envia APENAS a imagem atual da galeria (primeira da
        galeria de uploads) ao Flow com esse prompt, e depois deleta apenas
        o primeiro item dos uploads.
        """
        C = self.colors
        idx = self._revisao_idx
        item = self._revisao_itens[idx]

        # Janela modal de prompt
        win = tk.Toplevel(self)
        win.title("Editar imagem")
        win.configure(bg=C["BG"])
        win.resizable(True, False)
        win.grab_set()
        win.focus_set()

        # Centraliza
        self.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() // 2 - 300
        y = self.winfo_rooty() + self.winfo_height() // 2 - 80
        win.geometry(f"600x160+{x}+{y}")

        tk.Label(win, text="Prompt de edição:", bg=C["BG"], fg=C["FG"],
                 font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=16, pady=(14, 4))

        entry_frame = tk.Frame(win, bg=C["BG"])
        entry_frame.pack(fill="x", padx=16)
        entry_var = tk.StringVar(value=getattr(self, "_rev_ultimo_prompt_edicao", ""))
        entry = ttk.Entry(entry_frame, textvariable=entry_var, font=("Segoe UI", 11))
        entry.pack(fill="x")
        entry.select_range(0, "end")
        entry.focus_set()

        btn_frame = tk.Frame(win, bg=C["BG"])
        btn_frame.pack(pady=(12, 0))

        def _confirmar():
            prompt = entry_var.get().strip()
            if not prompt:
                messagebox.showwarning("Aviso", "Digite um prompt antes de continuar.", parent=win)
                return
            self._rev_ultimo_prompt_edicao = prompt
            win.destroy()
            self._rev_enviar_edicao(item, prompt)

        def _cancelar():
            win.destroy()

        ttk.Button(btn_frame, text="Enviar", style="Accent.TButton",
                   command=_confirmar).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Cancelar",
                   command=_cancelar).pack(side="left")

        entry.bind("<Return>", lambda e: _confirmar())
        entry.bind("<Escape>", lambda e: _cancelar())

    def _rev_enviar_edicao(self, item, prompt):
        """
        Dispara o fluxo de edição em thread separada:
        - Envia apenas a imagem atual (item['arquivo']) ao Flow
        - O flow usa apenas 1 imagem (fluxo de edição, não de swap)
        - Após envio, seleciona apenas o primeiro upload e o deleta
        """
        if not PLAYWRIGHT_AVAILABLE:
            messagebox.showerror("Erro", "Playwright não está instalado.")
            return

        arquivo = item.get("arquivo")
        if not arquivo or not Path(arquivo).exists():
            # Tenta frameog como fallback
            pasta = item.get("pasta")
            if pasta:
                frameog = pasta / "frameog.jpg"
                if frameog.exists():
                    arquivo = frameog
            if not arquivo or not Path(arquivo).exists():
                messagebox.showerror("Erro", "Imagem não encontrada para esta entrada.")
                return

        arquivo = Path(arquivo)
        self._log(f"\n✏ Edição: {arquivo.name}")
        self._log(f"   Prompt: {prompt}")

        def _run():
            try:
                destino = asyncio.run(
                    self._rev_enviar_edicao_async(arquivo, prompt)
                )
                self.after(
                    0, lambda: self._rev_finalizar_edicao(item, destino)
                )
            except Exception as e:
                self._log(f"✏ Edição ERRO: {e}")
                self.after(0, lambda: messagebox.showerror("Edição", str(e)))

        threading.Thread(target=_run, daemon=True).start()

    def _rev_finalizar_edicao(self, item, destino):
        if not destino:
            messagebox.showerror(
                "Edicao",
                "Nao foi possivel baixar a imagem editada."
            )
            return

        destino = Path(destino)
        item["arquivo"] = destino
        item["editado"] = True
        item["editado_em"] = time.time()
        self._revisao_itens.sort(key=self._revisao_sort_key)
        self._revisao_idx = self._revisao_itens.index(item)
        try:
            self._rev_mostrar(self._revisao_idx)
        except Exception:
            pass
        messagebox.showinfo(
            "Edicao",
            f"Edicao concluida!\nArquivo substituido: {destino.name}"
        )

    async def _rev_enviar_edicao_async(self, arquivo: Path, prompt: str):
        """
        Fluxo de edição de uma única imagem na aba Revisão (tecla E).

        Sequência correta — imagem ANTES do prompt:
        1. Envia 'arquivo' para a galeria Uploads
        2. Aguarda 15 s para a imagem carregar
        3. Abre Uploads e seleciona a imagem via Shift+mouse.click nas coords reais
        4. Cola o prompt no editor de texto (seleção mantida)
        5. Clica em Enviar
        6. Abre Uploads, seleciona + Delete
        7. Volta para "Todas as mídias"
        8. Baixa a imagem gerada
        """
        # ── Seletores ─────────────────────────────────────────────────────────
        UPLOAD_LINK_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-682f0b3f-0.iPxPxr "
            "> div.sc-e4f4e472-0.iUuqJB "
            "> div > div > div > div.sc-888a6226-2.iyGxUz "
            "> div > div > div > div > div > span "
            "> div > div > div > div > span > div > a"
        )
        UPLOAD_IMG_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-682f0b3f-0.iPxPxr "
            "> div.sc-e4f4e472-0.iUuqJB "
            "> div > div > div > div.sc-888a6226-2.iyGxUz "
            "> div > div > div > div > div > span "
            "> div > div > div > div > span > div > a > img"
        )
        ENVIAR_BTN_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-682f0b3f-1.cLCWIL "
            "> div > div > div > div "
            "> div.sc-26b30722-1.kZzgCz "
            "> div.sc-26b30722-10.eTAJIl "
            "> button.sc-e8425ea6-0.hOBPaw.sc-d3791a4f-0.sc-d3791a4f-4"
            ".sc-26b30722-5.ewGlDn.famhRe.jDvIwb"
        )
        UPLOADS_BTN_SEL = FLOW_UPLOADS_BTN_SEL
        TODAS_MIDIAS_SEL = (
            "#__next > div.sc-c7ee1759-1.jhwuTJ "
            "> div.sc-682f0b3f-0.iPxPxr "
            "> div.sc-265fb5e0-1.kSJyDR "
            "> div.sc-3ce961f7-1.gAnqsv"
        )

        async def _selecionar_primeira_imagem_uploads(page):
            """
            Seleciona a 1ª imagem nos Uploads pelo método visual/posição de tela.
            Não usa seletor legado nem Ctrl+A.
            """
            await self._abrir_uploads_flow_async(page)
    
            rects = []
            limite = time.monotonic() + 12
            while time.monotonic() < limite:
                rects = await self._obter_uploads_visiveis_por_posicao_async(page)
                if rects:
                    break
                await asyncio.sleep(0.35)

            if not rects:
                self._log("   ⚠ Nenhuma imagem visível nos Uploads")
                return False

            item = rects[0]
            await page.keyboard.down("Control")
            await page.mouse.click(float(item["cx"]), float(item["cy"]))
            await page.keyboard.up("Control")
            await asyncio.sleep(0.3)
            self._log(f"   ✓ 1ª imagem selecionada visualmente ({len(rects)} item(ns) visível(is))")
            return True

        # ── Conectar ──────────────────────────────────────────────────────────
        perfis = self._flow_profiles_obter()
        perfis_ativos = [p for p in perfis if p.get("active")]
        if not perfis_ativos:
            raise RuntimeError("Nenhum perfil Flow ativo configurado.")
        perfil = perfis_ativos[0]
        porta = int(perfil.get("port", 9222))
        self._log(f"   → Conectando ao perfil '{perfil['name']}' (porta {porta})...")
        try:
            self._flow_garantir_perfil_aberto(perfil)
        except Exception as exc:
            raise RuntimeError(
                f"Nao foi possivel abrir o perfil '{perfil['name']}': {exc}"
            ) from exc

        async with async_playwright() as pw:
            try:
                browser = await pw.chromium.connect_over_cdp(
                    f"http://localhost:{porta}", timeout=10000)
            except Exception as e:
                raise RuntimeError(
                    f"Não foi possível conectar ao Chrome na porta {porta}: {e}")

            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = None
            for p in ctx.pages:
                if "labs.google" in p.url or "flow" in p.url.lower():
                    page = p
                    break
            if page is None:
                page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            self._log(f"   → Aba: {page.url[:60]}...")

            # ── FASE 1: Upload ────────────────────────────────────────────────
            self._log(f"   → [1] Enviando {arquivo.name} para Uploads...")
            await self._upload_arquivo_para_galeria_async(page, str(arquivo))
            self._log("   ✓ Upload concluído")

            # ── FASE 2: Aguarda galeria carregar ──────────────────────────────
            self._log("   ⏳ [2] Aguardando 15 s para a imagem carregar na galeria...")
            await asyncio.sleep(15)

            # ── FASE 3: Seleciona a imagem no Uploads ─────────────────────────
            # DEVE ser feito ANTES de colar o prompt para que o Flow associe
            # a imagem ao prompt corretamente.
            self._log("   → [3] Abrindo Uploads e selecionando a imagem...")
            try:
                await _selecionar_primeira_imagem_uploads(page)
            except Exception as e:
                self._log(f"   ⚠ Seleção FASE 3 falhou: {e}")

            # ── FASE 4: Cola o prompt SEM clicar fora (mantém seleção) ────────
            self._log("   → [4] Inserindo prompt de edição...")
            CAMPO = '[data-slate-editor="true"]'
            try:
                await page.wait_for_selector(CAMPO, timeout=10000)
                campo = page.locator(CAMPO).first
                await campo.click()
                await asyncio.sleep(0.4)
                await self._colar_prompt_async(page, prompt)
                await asyncio.sleep(0.3)
                self._log("   ✓ Prompt inserido")
            except Exception as e:
                self._log(f"   ⚠ Falha ao inserir prompt: {e}")

            # Captura src atual para detectar nova imagem após geração
            src_anterior = None
            try:
                src_anterior = await self._obter_src_primeira_galeria_async(
                    page, timeout_ms=3000
                )
            except Exception:
                pass

            # ── FASE 5: Clica em Enviar ───────────────────────────────────────
            self._log("   → [5] Clicando em Enviar...")
            enviado = False
            try:
                btn_enviar = page.locator(ENVIAR_BTN_SEL).first
                await btn_enviar.wait_for(state="visible", timeout=8000)
                await btn_enviar.click()
                await asyncio.sleep(0.8)
                self._log("   ✓ Enviado ao Flow!")
                enviado = True
            except Exception as e:
                self._log(f"   ~ Seletor botão Enviar falhou ({e}), tentando fallback...")
                try:
                    await self._clicar_criar_flow_async(page)
                    self._log("   ✓ Enviado ao Flow (fallback)!")
                    enviado = True
                except Exception as e2:
                    self._log(f"   ⚠ Falha ao clicar em Enviar: {e2}")

            if not enviado:
                raise RuntimeError("Não foi possível clicar em Enviar.")

            # ── FASE 6: Delete — imagem já fica selecionada após o envio ─────
            self._log("   → [6] Deletando imagem enviada (já selecionada)...")
            try:
                await page.keyboard.press("Delete")
                await asyncio.sleep(0.5)
                self._log("   ✓ Imagem deletada dos Uploads")
            except Exception as e:
                self._log(f"   ⚠ Não foi possível deletar o upload: {e}")

            # ── FASE 7: Volta para "Todas as mídias" ──────────────────────────
            self._log("   → [7] Voltando para a galeria de todas as mídias...")
            try:
                btn_todas = page.locator(TODAS_MIDIAS_SEL).first
                await btn_todas.wait_for(state="visible", timeout=8000)
                await btn_todas.click()
                await asyncio.sleep(0.8)
                self._log("   ✓ Galeria de todas as mídias aberta")
            except Exception as e:
                self._log(f"   ~ Não foi possível clicar em 'Todas as mídias': {e}")

            # ── FASE 8: Baixa a imagem gerada ────────────────────────────────
            try:
                send_interval = float(self.opt_send_interval.get())
            except Exception:
                send_interval = 10.0
            self._log(f"   ⏳ Aguardando {send_interval:g}s antes de baixar...")
            await asyncio.sleep(send_interval)

            self._log("   → [8] Baixando imagem gerada...")
            try:
                pasta_destino = arquivo.parent
                ok_baixou = await self._baixar_primeira_galeria_async(
                    page, pasta_destino, src_anterior=src_anterior,
                    destino=arquivo
                )
                if ok_baixou:
                    self._log("   ✓ Imagem baixada com sucesso")
                    return arquivo
                else:
                    self._log("   ⚠ Não foi possível baixar a imagem gerada")
            except Exception as e:
                self._log(f"   ⚠ Erro ao baixar imagem gerada: {e}")

        return None


    def _marcar_todas(self):
        for v in self._revisao_vars:
            v.set(True)
        self._rev_mostrar(self._revisao_idx)

    def _desmarcar_todas(self):
        for v in self._revisao_vars:
            v.set(False)
        self._rev_mostrar(self._revisao_idx)

    def _deletar_marcadas(self):
        marcadas = [self._revisao_itens[i]
                    for i, v in enumerate(self._revisao_vars) if v.get()]
        if not marcadas:
            messagebox.showinfo("Revisão", "Nenhuma imagem marcada para deletar.")
            return
        nomes = "\n".join(
            f"• {it['pasta'].name}" if it.get("pasta") else "• (pasta desconhecida)"
            for it in marcadas
        )
        if not messagebox.askyesno("Confirmar exclusão",
                f"Deletar {len(marcadas)} pasta(s) permanentemente?\n\n{nomes}\n\n"
                "Esta ação não pode ser desfeita."):
            return
        removidos = 0
        for item in marcadas:
            pasta = item.get("pasta")
            if not pasta:
                self._log("  ⚠ Item sem pasta definida, ignorado.")
                continue
            try:
                if pasta.exists():
                    shutil.rmtree(pasta)
                    self._log(f"  🗑 Pasta deletada: {pasta.name}")
                    removidos += 1
                else:
                    self._log(f"  ⚠ Pasta não encontrada: {pasta.name}")
            except Exception as e:
                self._log(f"  ❌ Erro ao deletar {pasta.name}: {e}")
        # Remove os itens deletados do carrossel
        indices_manter = [
            i for i, item in enumerate(self._revisao_itens)
            if not (self._revisao_vars[i].get() and item.get("pasta") and not item["pasta"].exists())
        ]
        novos_itens = [self._revisao_itens[i] for i in indices_manter]
        if novos_itens:
            self._abrir_revisao([])  # reseta e reconstrói com itens restantes
            self._revisao_itens = novos_itens
            self._revisao_vars = [tk.BooleanVar(value=bool(it.get("erro"))) for it in novos_itens]
            self._revisao_idx = 0
            self._rev_mostrar(0)
        else:
            self._build_revisao_vazia()
        self._log(f"  ✓ {removidos} pasta(s) deletada(s).")
        messagebox.showinfo("Deletar marcadas", f"{removidos} pasta(s) deletada(s) com sucesso.")

    def _refazer_marcadas(self):
        marcadas = [self._revisao_itens[i]
                    for i, v in enumerate(self._revisao_vars) if v.get()]
        if not marcadas:
            messagebox.showinfo("Revisão", "Nenhuma imagem marcada para refazer.")
            return
        nomes = "\n".join(
            f"• {it['pasta'].name}" if it.get("pasta") else "• (pasta desconhecida)"
            for it in marcadas
        )
        if not messagebox.askyesno("Confirmar",
                f"Refazer {len(marcadas)} imagem(ns)?\n\n{nomes}\n\n"
                "O arquivo gerado será apagado e o processo será refeito."):
            return
        # Apaga os frameNew marcados e dispara o reprocessamento
        pastas_refazer = []
        for item in marcadas:
            pasta_nome = item["pasta"].name if item.get("pasta") else "(desconhecida)"
            if item.get("arquivo"):
                try:
                    if item["arquivo"].exists():
                        item["arquivo"].unlink()
                        self._log(f"  🗑 {item['arquivo'].name} removido de {pasta_nome}")
                except Exception as e:
                    self._log(f"  ⚠ Não foi possível remover {item['arquivo'].name}: {e}")
            else:
                self._log(f"  ↩ {pasta_nome} — sem arquivo gerado, será reprocessada")
            if item.get("pasta"):
                pastas_refazer.append(item["pasta"])

        # Valida perfis e prompt ANTES de lançar a thread (na thread principal do tkinter)
        perfis = self._flow_perfis_ativos()
        if not perfis:
            messagebox.showwarning(
                "Perfis Flow",
                "Marque pelo menos um perfil Flow como ativo antes de refazer."
            )
            return

        p_texto = self.prompt_text.get("1.0", "end").rstrip()
        if not p_texto:
            messagebox.showerror(
                "Erro",
                "O prompt está vazio. Escreva ou selecione um prompt antes de refazer."
            )
            return

        # Reutiliza a lógica de envio Flow com as pastas marcadas
        self._log(f"\n🔁 Refazendo {len(pastas_refazer)} pasta(s)...")
        self._iniciar_flow_com_pastas(pastas_refazer)

    def _iniciar_flow_com_pastas(self, pastas):
        """Dispara o envio Flow para uma lista específica de pastas (reprocessamento)."""
        def _run():
            try:
                asyncio.run(self._enviar_flow_async(pastas_override=pastas))
            except Exception as exc:
                import traceback
                erro_txt = traceback.format_exc()
                self._log(f"❌ ERRO ao refazer: {exc}")
                self._log(erro_txt)
                self.after(
                    0, lambda: messagebox.showerror(
                        "Erro ao refazer",
                        f"Falha ao iniciar o reprocessamento:\n\n{exc}"
                    )
                )
        threading.Thread(target=_run, daemon=True).start()

    # =========================================================================
    # TAB 5 - VIDEOS
    # =========================================================================
    def _build_tab_videos(self):
        C = self.colors
        if not hasattr(self, "_video_frame") or self._video_frame is None:
            self._video_frame = ttk.LabelFrame(self.notebook, text="Separação")
            self.notebook.add(self._video_frame, text="  Separação  ")
        self._video_itens = []
        self._video_escolhas = []
        self._video_idx = 0
        self._video_photo = None
        self._video_processando = False
        # Player de vídeo original
        self._video_cap = None          # cv2.VideoCapture atual
        self._video_playing = False     # se está reproduzindo
        self._video_after_id = None     # id do after agendado
        self._video_player_photo = None # PhotoImage do frame do player
        self._video_player_label = None # Label que exibe o vídeo
        self._video_frame_novo_label = None  # Label do novo frame (frameNew)
        self._video_play_btn = None     # Botão play/pause
        self._video_frame_novo_photo = None  # PhotoImage do frame novo
        self._video_audio_proc = None   # subprocess do ffplay para áudio
        self._build_videos_vazio()

    def _build_videos_vazio(self):
        C = self.colors
        for widget in self._video_frame.winfo_children():
            widget.destroy()
        centro = tk.Frame(self._video_frame, bg=C["BG"])
        centro.pack(expand=True)
        tk.Label(
            centro,
            text="Nenhuma imagem carregada para separação.",
            bg=C["BG"], fg=C["FG2"], font=("Segoe UI", 13)
        ).pack(pady=(0, 12))
        ttk.Button(
            centro, text="Carregar imagens de assets/work",
            command=self._carregar_videos_work
        ).pack()

    def _abrir_videos_da_revisao(self):
        aprovados = [
            item for i, item in enumerate(self._revisao_itens)
            if i < len(self._revisao_vars) and not self._revisao_vars[i].get()
        ]
        if not aprovados:
            messagebox.showinfo(
                "Separação",
                "Nenhuma imagem aprovada. Desmarque ao menos uma imagem na revisao."
            )
            return
        self._abrir_videos(aprovados)

    def _carregar_videos_work(self):
        itens = []
        if WORK_DIR.exists():
            for pasta in sorted(WORK_DIR.iterdir(), key=lambda p: p.name.lower()):
                if not pasta.is_dir() or pasta.name.startswith("_falhas"):
                    continue
                imagens = [
                    p for p in pasta.glob("frameNew*")
                    if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
                ]
                if imagens:
                    arquivo = max(imagens, key=lambda p: p.stat().st_mtime)
                    itens.append({"pasta": pasta, "arquivo": arquivo, "pos": 0})
        if not itens:
            messagebox.showinfo(
                "Separação", f"Nenhuma imagem frameNew encontrada em:\n{WORK_DIR}"
            )
            return
        self._abrir_videos(itens)

    def _mostrar_secao_separacao(self):
        try:
            self.notebook.select(self.notebook.index(self._tab_video_frame))
        except Exception:
            try:
                self.notebook.select(self.notebook.index(self._video_frame))
            except Exception:
                pass
        try:
            self.update_idletasks()
            self._video_tab_canvas.yview_moveto(1.0)
        except Exception:
            pass
        try:
            self._video_frame.focus_set()
        except Exception:
            pass

    def _abrir_videos(self, itens):
        C = self.colors
        validos = []
        sem_original = []
        for item in itens:
            pasta = Path(item["pasta"])
            original = self._video_original_da_pasta(pasta)
            if not original:
                sem_original.append(pasta.name)
                continue
            novo = dict(item)
            novo["original"] = original
            novo["modelo"] = self._detectar_modelo_pasta(pasta.name) or "Sem modelo"
            validos.append(novo)

        if not validos:
            messagebox.showerror(
                "Separação",
                "Nenhum dos itens possui o video original na pasta de trabalho."
            )
            return
        if sem_original:
            self._log("Videos ignorados sem original: " + ", ".join(sem_original))

        # Para o player antes de destruir os widgets
        self._video_parar_player()

        self._video_itens = validos
        self._video_escolhas = [None] * len(validos)
        self._video_pausas  = [None] * len(validos)  # segundos do ponto de pausa p/ Edit
        self._video_idx = 0
        self._video_photo = None
        self._video_player_label = None
        self._video_frame_novo_label = None
        self._video_play_btn = None
        for widget in self._video_frame.winfo_children():
            widget.destroy()

        header = tk.Frame(self._video_frame, bg=C["BG"])
        header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(
            header, text="SEPARAÇÃO", bg=C["BG"], fg=C["FG2"],
            font=("Segoe UI Semibold", 9)
        ).pack(side="left")
        self._video_btn_processar = ttk.Button(
            header, text="Criar videos marcados", style="Accent.TButton",
            command=self._video_confirmar_processamento
        )
        self._video_btn_processar.pack(side="right")
        ttk.Button(
            header, text="Recarregar assets/work",
            command=self._carregar_videos_work
        ).pack(side="right", padx=(0, 6))
        tk.Frame(self._video_frame, bg=C["BORDER"], height=1).pack(fill="x")

        instrucoes = tk.Frame(self._video_frame, bg=C["BG"])
        instrucoes.pack(fill="x", padx=40, pady=(10, 0))
        tk.Label(
            instrucoes,
            text="1  Estatico (7-11s)     2  Foto + audio original     3  Motion     4  Edit",
            bg=C["BG"], fg=C["FG"], font=("Segoe UI Semibold", 11)
        ).pack()
        self._video_contador = tk.Label(
            instrucoes, bg=C["BG"], fg=C["FG2"], font=("Segoe UI", 10)
        )
        self._video_contador.pack(pady=(4, 0))

        # ── Layout lado a lado: vídeo original | novo frame ──
        viewers = tk.Frame(self._video_frame, bg=C["BG"])
        viewers.pack(expand=True, fill="both", padx=40, pady=(8, 0))
        viewers.columnconfigure(0, weight=1)
        viewers.columnconfigure(1, weight=1)
        viewers.rowconfigure(0, weight=0)
        viewers.rowconfigure(1, weight=1)

        # Cabeçalhos
        tk.Label(
            viewers, text="▶  Vídeo original", bg=C["BG"], fg=C["FG2"],
            font=("Segoe UI Semibold", 9)
        ).grid(row=0, column=0, pady=(0, 4))
        tk.Label(
            viewers, text="🖼  Novo frame gerado", bg=C["BG"], fg=C["FG2"],
            font=("Segoe UI Semibold", 9)
        ).grid(row=0, column=1, pady=(0, 4))

        self._video_player_label = tk.Label(
            viewers, bg=C["BG3"], text="", width=1, height=1
        )
        self._video_player_label.grid(row=1, column=0, sticky="nsew", padx=(0, 6))

        self._video_frame_novo_label = tk.Label(
            viewers, bg=C["BG3"], text="", width=1, height=1
        )
        self._video_frame_novo_label.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

        # ── Barra de navegação + play/pause ──
        barra = tk.Frame(self._video_frame, bg=C["BG"])
        barra.pack(fill="x", padx=40, pady=(8, 4))
        self._video_btn_prev = ttk.Button(
            barra, text="<", width=4, command=lambda: self._video_navegar(-1)
        )
        self._video_btn_prev.pack(side="left")

        # Play/Pause centralizado
        player_ctrl = tk.Frame(barra, bg=C["BG"])
        player_ctrl.pack(side="left", expand=True, fill="x", padx=8)

        info = tk.Frame(player_ctrl, bg=C["BG"])
        info.pack(fill="x")
        self._video_nome_label = tk.Label(
            info, bg=C["BG"], fg=C["FG"], font=("Segoe UI Semibold", 12)
        )
        self._video_nome_label.pack()
        self._video_arq_label = tk.Label(
            info, bg=C["BG"], fg=C["FG2"], font=("Segoe UI", 9)
        )
        self._video_arq_label.pack()
        self._video_escolha_label = tk.Label(
            info, bg=C["BG"], fg=C["ACCFG"], font=("Segoe UI Semibold", 11)
        )
        self._video_escolha_label.pack(pady=(2, 0))

        self._video_play_btn = ttk.Button(
            player_ctrl, text="⏸ Pausar", command=self._video_toggle_play
        )
        self._video_play_btn.pack(pady=(4, 0))

        self._video_btn_next = ttk.Button(
            barra, text=">", width=4, command=lambda: self._video_navegar(1)
        )
        self._video_btn_next.pack(side="right")

        botoes = tk.Frame(self._video_frame, bg=C["BG"])
        botoes.pack(pady=(0, 14))
        ttk.Button(
            botoes, text="1 - Estatico", command=lambda: self._video_marcar(1)
        ).pack(side="left", padx=4)
        ttk.Button(
            botoes, text="2 - Com audio", command=lambda: self._video_marcar(2)
        ).pack(side="left", padx=4)
        ttk.Button(
            botoes, text="3 - Motion", command=lambda: self._video_marcar(3)
        ).pack(side="left", padx=4)
        ttk.Button(
            botoes, text="4 - Edit", command=lambda: self._video_marcar(4)
        ).pack(side="left", padx=4)

        self._video_frame.bind("<Left>", lambda e: self._video_navegar(-1))
        self._video_frame.bind("<Right>", lambda e: self._video_navegar(1))
        self._video_frame.bind("1", lambda e: self._video_marcar(1))
        self._video_frame.bind("2", lambda e: self._video_marcar(2))
        self._video_frame.bind("3", lambda e: self._video_marcar(3))
        self._video_frame.bind("4", lambda e: self._video_marcar(4))
        self._video_frame.bind("<space>", lambda e: self._video_toggle_play())
        self.notebook.bind(
            "<<NotebookTabChanged>>", self._video_on_tab_change, add="+"
        )

        self._video_mostrar(0)
        self._mostrar_secao_separacao()

    def _video_on_tab_change(self, event):
        try:
            alvo = getattr(self, "_tab_video_frame", self._video_frame)
            if self.notebook.index("current") == self.notebook.index(alvo):
                self._video_frame.focus_set()
            else:
                # Pausa o player ao sair da aba Vídeo/Separação
                self._video_parar_player()
        except Exception:
            pass

    def _video_original_da_pasta(self, pasta):
        extensoes = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
        candidatos = [
            p for p in pasta.iterdir()
            if p.is_file() and p.suffix.lower() in extensoes
        ]
        if not candidatos:
            return None
        exatos = [p for p in candidatos if p.stem.lower() == pasta.name.lower()]
        if exatos:
            return sorted(exatos, key=lambda p: p.name.lower())[0]
        return sorted(candidatos, key=lambda p: p.name.lower())[0]

    def _video_mostrar(self, idx):
        if not self._video_itens:
            return
        C = self.colors
        total = len(self._video_itens)
        idx = max(0, min(idx, total - 1))
        self._video_idx = idx
        item = self._video_itens[idx]
        escolha = self._video_escolhas[idx]
        marcados = sum(valor is not None for valor in self._video_escolhas)
        self._video_contador.configure(
            text=f"{idx + 1} / {total}   |   {marcados} marcados"
        )

        # ── Inicia o player com o vídeo original ──
        self._video_parar_player()
        if CV2_AVAILABLE and self._video_player_label is not None:
            try:
                self._video_cap = cv2.VideoCapture(str(item["original"]))
                if self._video_cap.isOpened():
                    self._video_playing = True
                    self._video_iniciar_audio(item["original"], 0.0)
                    self._video_atualizar_frame_player()
                else:
                    self._video_cap.release()
                    self._video_cap = None
                    self._video_player_label.configure(
                        image="", text="[vídeo não suportado]",
                        fg=C["FG2"], font=("Segoe UI", 11)
                    )
            except Exception:
                self._video_player_label.configure(
                    image="", text="[erro ao abrir vídeo]",
                    fg=C["FG2"], font=("Segoe UI", 11)
                )
        elif self._video_player_label is not None and not CV2_AVAILABLE:
            self._video_player_label.configure(
                image="", text="[instale opencv-python para ver o vídeo]",
                fg=C["FG2"], font=("Segoe UI", 10)
            )

        # ── Novo frame gerado (frameNew) ──
        if PIL_AVAILABLE and self._video_frame_novo_label is not None and Path(item["arquivo"]).exists():
            try:
                self._video_frame_novo_label.update_idletasks()
                w = max(self._video_frame_novo_label.winfo_width(), 300)
                h = max(self._video_frame_novo_label.winfo_height(), 400)
                imagem = Image.open(item["arquivo"])
                imagem.thumbnail((w, h), Image.LANCZOS)
                photo = ImageTk.PhotoImage(imagem)
                self._video_frame_novo_label.configure(image=photo, text="")
                self._video_frame_novo_label._photo = photo
                self._video_frame_novo_photo = photo
            except Exception:
                self._video_frame_novo_label.configure(
                    image="", text="[erro ao carregar imagem]",
                    fg=C["FG2"], font=("Segoe UI", 12)
                )

        self._video_nome_label.configure(
            text=f"{item['pasta'].name}  |  {item['modelo']}"
        )
        self._video_arq_label.configure(
            text=f"{item['arquivo'].name}  <-  {item['original'].name}"
        )
        nomes = {
            1: "1 - VIDEO ESTATICO",
            2: "2 - VIDEO COM AUDIO",
            3: "3 - MOTION",
        }
        if escolha == 4:
            pausa = self._video_pausas[idx]
            texto_pausa = f"  (pausa em {pausa:.2f}s)" if pausa is not None else "  (pausa não definida)"
            texto_escolha = "4 - EDIT" + texto_pausa
        else:
            texto_escolha = nomes.get(escolha, "Pressione 1, 2, 3 ou 4")
        self._video_escolha_label.configure(text=texto_escolha)
        self._video_btn_prev.state(["disabled"] if idx == 0 else ["!disabled"])
        self._video_btn_next.state(
            ["disabled"] if idx == total - 1 else ["!disabled"]
        )
        # Atualiza botão play/pause
        if self._video_play_btn is not None:
            self._video_play_btn.configure(
                text="⏸ Pausar" if self._video_playing else "▶ Reproduzir"
            )

    def _video_parar_player(self):
        """Para a reprodução, cancela o after e libera o VideoCapture e o áudio."""
        self._video_playing = False
        if self._video_after_id is not None:
            try:
                self.after_cancel(self._video_after_id)
            except Exception:
                pass
            self._video_after_id = None
        if self._video_cap is not None:
            try:
                self._video_cap.release()
            except Exception:
                pass
            self._video_cap = None
        self._video_parar_audio()

    def _video_toggle_play(self):
        """Alterna entre play e pause. Ao pausar, registra a posição atual."""
        if self._video_cap is None:
            return
        self._video_playing = not self._video_playing
        if not self._video_playing:
            # Guarda a posição atual em segundos para uso no Edit
            pos_ms = self._video_cap.get(cv2.CAP_PROP_POS_MSEC)
            pos_s  = pos_ms / 1000.0
            idx = self._video_idx
            if 0 <= idx < len(self._video_pausas):
                self._video_pausas[idx] = pos_s
                self._log(
                    f"Edit: ponto de pausa registrado em {pos_s:.3f}s "
                    f"para {self._video_itens[idx]['pasta'].name}"
                )
            # Atualiza label de escolha se já estava em Edit
            if (0 <= idx < len(self._video_escolhas)
                    and self._video_escolhas[idx] == 4):
                self._video_mostrar_info(idx)
            # Para o áudio
            self._video_parar_audio()
        else:
            # Retoma: reinicia o áudio a partir da posição atual
            pos_ms = self._video_cap.get(cv2.CAP_PROP_POS_MSEC)
            pos_s  = pos_ms / 1000.0
            idx = self._video_idx
            if 0 <= idx < len(self._video_itens):
                self._video_iniciar_audio(
                    self._video_itens[idx]["original"], pos_s
                )

        if self._video_play_btn is not None:
            self._video_play_btn.configure(
                text="⏸ Pausar" if self._video_playing else "▶ Reproduzir"
            )
        if self._video_playing:
            self._video_atualizar_frame_player()

    def _video_mostrar_info(self, idx):
        """Atualiza apenas o label de escolha/pausa sem reiniciar o player."""
        if not self._video_itens or not (0 <= idx < len(self._video_itens)):
            return
        escolha = self._video_escolhas[idx]
        nomes = {
            1: "1 - VIDEO ESTATICO",
            2: "2 - VIDEO COM AUDIO",
            3: "3 - MOTION",
        }
        if escolha == 4:
            pausa = self._video_pausas[idx]
            texto_pausa = f"  (pausa em {pausa:.2f}s)" if pausa is not None else "  (pausa não definida)"
            texto_escolha = "4 - EDIT" + texto_pausa
        else:
            texto_escolha = nomes.get(escolha, "Pressione 1, 2, 3 ou 4")
        try:
            self._video_escolha_label.configure(text=texto_escolha)
        except Exception:
            pass

    def _video_atualizar_frame_player(self):
        """Lê o próximo frame do vídeo e agenda a atualização seguinte."""
        if not self._video_playing or self._video_cap is None:
            return
        if self._video_player_label is None:
            return
        try:
            ret, frame = self._video_cap.read()
            if not ret:
                # Chegou ao fim: reinicia o vídeo e o áudio
                self._video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self._video_cap.read()
                if self._video_itens and 0 <= self._video_idx < len(self._video_itens):
                    self._video_parar_audio()
                    self._video_iniciar_audio(
                        self._video_itens[self._video_idx]["original"], 0.0
                    )
            if ret:
                # Usa o tamanho do container pai — estável, não cresce com o conteúdo
                container = self._video_player_label.master
                container.update_idletasks()
                w = max(container.winfo_width() // 2 - 12, 100)
                h = max(container.winfo_height(), 100)
                # Converte BGR → RGB e redimensiona mantendo proporção
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                fh, fw = frame_rgb.shape[:2]
                scale = min(w / fw, h / fh)
                nw, nh = int(fw * scale), int(fh * scale)
                if nw > 0 and nh > 0:
                    frame_resized = cv2.resize(
                        frame_rgb, (nw, nh), interpolation=cv2.INTER_AREA
                    )
                    img = Image.fromarray(frame_resized)
                    photo = ImageTk.PhotoImage(img)
                    self._video_player_label.configure(image=photo, text="")
                    self._video_player_label._photo = photo
                    self._video_player_photo = photo
            # FPS do vídeo para calcular delay
            fps = self._video_cap.get(cv2.CAP_PROP_FPS) or 25
            delay = max(1, int(1000 / fps))
            self._video_after_id = self.after(delay, self._video_atualizar_frame_player)
        except Exception:
            self._video_playing = False

    # ── Áudio via ffplay ──────────────────────────────────────────────────────

    def _video_iniciar_audio(self, video_path, pos_s=0.0):
        """Inicia o ffplay em background para reproduzir o áudio do vídeo."""
        self._video_parar_audio()
        ffplay = shutil.which("ffplay")
        if not ffplay:
            return  # ffplay não disponível — sem áudio, mas sem crash
        try:
            cmd = [
                ffplay, "-nodisp", "-autoexit",
                "-loglevel", "quiet",
                "-ss", f"{pos_s:.3f}",
                str(video_path),
            ]
            self._video_audio_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            self._video_audio_proc = None

    def _video_parar_audio(self):
        """Mata o processo de áudio se estiver rodando."""
        if self._video_audio_proc is not None:
            try:
                self._video_audio_proc.terminate()
            except Exception:
                pass
            try:
                self._video_audio_proc.wait(timeout=1)
            except Exception:
                pass
            self._video_audio_proc = None

    def _video_navegar(self, delta):
        self._video_mostrar(self._video_idx + delta)

    def _video_marcar(self, escolha):
        if not self._video_itens or self._video_processando:
            return
        idx = self._video_idx
        if escolha == 4:
            pausa = self._video_pausas[idx] if idx < len(self._video_pausas) else None
            if pausa is None:
                messagebox.showinfo(
                    "Edit",
                    "Para marcar como Edit, primeiro pause o vídeo no ponto desejado.\n"
                    "Use o botão ⏸ Pausar ou a tecla Espaço."
                )
                return
        self._video_escolhas[idx] = escolha
        self._video_mostrar(idx + 1 if idx < len(self._video_itens) - 1 else idx)

    def _video_confirmar_processamento(self):
        if self._video_processando:
            return
        faltando = [
            i for i, escolha in enumerate(self._video_escolhas)
            if escolha is None
        ]
        if faltando:
            self._video_mostrar(faltando[0])
            messagebox.showinfo(
                "Videos",
                f"Ainda faltam {len(faltando)} item(ns). Marque cada um com 1, 2, 3 ou 4."
            )
            return

        quantidades = {
            escolha: self._video_escolhas.count(escolha)
            for escolha in (1, 2, 3, 4)
        }
        if not messagebox.askyesno(
            "Criar videos",
            "Processar as escolhas?\n\n"
            f"Estaticos: {quantidades[1]}\n"
            f"Com audio: {quantidades[2]}\n"
            f"Motion: {quantidades[3]}\n"
            f"Edit: {quantidades[4]}"
        ):
            return

        self._video_processando = True
        self._video_btn_processar.state(["disabled"])
        threading.Thread(
            target=self._video_processar_worker,
            args=(
                [dict(item) for item in self._video_itens],
                list(self._video_escolhas),
                list(self._video_pausas),
            ),
            daemon=True
        ).start()

    def _video_processar_worker(self, itens, escolhas, pausas=None):
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        erros = []
        concluidos = 0
        if not ffmpeg:
            self.after(
                0, lambda: self._video_finalizar(
                    0, ["FFmpeg nao foi encontrado no PATH."]
                )
            )
            return

        if pausas is None:
            pausas = [None] * len(itens)

        READY_DIR.mkdir(parents=True, exist_ok=True)
        MOTION_DIR.mkdir(parents=True, exist_ok=True)
        for numero, (item, escolha, pausa) in enumerate(zip(itens, escolhas, pausas), 1):
            pasta = Path(item["pasta"])
            imagem = Path(item["arquivo"])
            original = Path(item["original"])
            modelo = str(item["modelo"])
            try:
                self._log(
                    f"[Videos {numero}/{len(itens)}] {pasta.name} - opcao {escolha}"
                )
                if escolha == 1:
                    destino_dir = READY_DIR / modelo
                    destino_dir.mkdir(parents=True, exist_ok=True)
                    destino = destino_dir / f"{original.stem}.mp4"
                    duracao = random.randint(7, 11)
                    self._video_criar_estatico(
                        ffmpeg, imagem, destino, duracao
                    )
                    self._log(f"  OK Estatico ({duracao}s): {destino}")
                elif escolha == 2:
                    destino_dir = READY_DIR / modelo
                    destino_dir.mkdir(parents=True, exist_ok=True)
                    destino = destino_dir / f"{original.stem}.mp4"
                    duracao, _ = self._video_duracoes_original(ffprobe, original)
                    self._video_criar_com_audio(
                        ffmpeg, imagem, original, destino, duracao
                    )
                    self._log(f"  OK Com audio ({duracao:.3f}s): {destino}")
                elif escolha == 3:
                    destino_dir = MOTION_DIR / modelo / pasta.name
                    destino_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(original, destino_dir / original.name)
                    shutil.copy2(imagem, destino_dir / imagem.name)
                    self._log(f"  OK Motion: {destino_dir}")
                elif escolha == 4:
                    destino_dir = READY_DIR / modelo
                    destino_dir.mkdir(parents=True, exist_ok=True)
                    destino = destino_dir / f"{original.stem}.mp4"
                    duracao_total, _ = self._video_duracoes_original(ffprobe, original)
                    self._video_criar_edit(
                        ffmpeg, imagem, original, destino,
                        pausa_s=pausa, duracao_total=duracao_total
                    )
                    self._log(
                        f"  OK Edit (pausa={pausa:.3f}s, total={duracao_total:.3f}s): {destino}"
                    )
                concluidos += 1
            except Exception as exc:
                erros.append(f"{pasta.name}: {exc}")
                self._log(f"  ERRO: {pasta.name}: {exc}")
        self.after(0, lambda: self._video_finalizar(concluidos, erros))

    def _video_duracoes_original(self, ffprobe, original):
        if ffprobe:
            processo = subprocess.run(
                [
                    ffprobe, "-v", "error",
                    "-show_entries", "format=duration:stream=codec_type,duration",
                    "-of", "json",
                    str(original)
                ],
                capture_output=True, text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if processo.returncode == 0:
                try:
                    dados = json.loads(processo.stdout)
                    duracao = float(dados["format"]["duration"])
                    duracao_video = next(
                        float(stream["duration"])
                        for stream in dados.get("streams", [])
                        if stream.get("codec_type") == "video"
                        and stream.get("duration")
                    )
                    if duracao > 0 and duracao_video > 0:
                        return duracao, duracao_video
                except (KeyError, TypeError, ValueError, StopIteration, json.JSONDecodeError):
                    pass
        if CV2_AVAILABLE:
            captura = cv2.VideoCapture(str(original))
            fps = captura.get(cv2.CAP_PROP_FPS)
            frames = captura.get(cv2.CAP_PROP_FRAME_COUNT)
            captura.release()
            if fps > 0 and frames > 0:
                duracao = frames / fps
                return duracao, duracao
        raise RuntimeError("Nao foi possivel obter a duracao do video original.")

    def _video_criar_estatico(self, ffmpeg, imagem, destino, duracao):
        self._video_executar_ffmpeg([
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-framerate", "30", "-i", str(imagem),
            "-t", str(duracao),
            "-vf", VIDEO_FILTER_4K,
            "-r", "30", "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-profile:v", "high", "-level:v", "5.1",
            "-tag:v", "avc1", "-color_range", "tv", "-an",
            "-movflags", "+faststart", str(destino)
        ])

    def _video_criar_com_audio(
            self, ffmpeg, imagem, original, destino, duracao):
        self._video_executar_ffmpeg([
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-framerate", "30", "-i", str(imagem),
            "-i", str(original),
            "-map", "0:v:0", "-map", "1:a:0?",
            "-t", f"{duracao:.6f}", "-vf", VIDEO_FILTER_4K,
            "-r", "30", "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-profile:v", "high", "-level:v", "5.1",
            "-tag:v", "avc1", "-color_range", "tv",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(destino)
        ])

    def _video_criar_edit(
            self, ffmpeg, imagem, original, destino, pausa_s, duracao_total):
        """
        Monta o vídeo Edit:
          [0 → pausa_s]       : frame novo (imagem estática)  +  áudio do original
          [pausa_s → fim]     : vídeo original continuando    +  áudio do original

        Estratégia FFmpeg (filter_complex + concat):
          - Segmento A: imagem em loop por pausa_s segundos, sem áudio
          - Segmento B: vídeo original de pausa_s até duracao_total, sem áudio
          - Áudio inteiro do original mapeado sobre a saída concatenada
          - Resultado tem exatamente duracao_total segundos
        """
        import tempfile

        duracao_b = duracao_total - pausa_s
        if duracao_b <= 0:
            raise RuntimeError(
                f"O ponto de pausa ({pausa_s:.3f}s) é maior ou igual à "
                f"duração do vídeo ({duracao_total:.3f}s). "
                "Escolha um ponto anterior."
            )

        # Arquivo de lista para concat demuxer
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            lista_path = f.name

        # Segmento A: frame novo em loop por pausa_s
        seg_a = Path(lista_path).with_suffix(".seg_a.mp4")
        # Segmento B: vídeo original de pausa_s em diante
        seg_b = Path(lista_path).with_suffix(".seg_b.mp4")

        try:
            sem_audio = Path(lista_path).with_suffix(".sem_audio.mp4")

            # ── Segmento A: frame novo estático ──────────────────────────────
            self._video_executar_ffmpeg([
                ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-loop", "1", "-framerate", "30", "-i", str(imagem),
                "-t", f"{pausa_s:.6f}",
                "-vf", VIDEO_FILTER_4K,
                "-r", "30", "-c:v", "libx264", "-preset", "medium",
                "-crf", "18", "-profile:v", "high", "-level:v", "5.1",
                "-tag:v", "avc1", "-color_range", "tv", "-an",
                "-movflags", "+faststart", str(seg_a)
            ])

            # ── Segmento B: vídeo original a partir de pausa_s ───────────────
            self._video_executar_ffmpeg([
                ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-ss", f"{pausa_s:.6f}",
                "-i", str(original),
                "-t", f"{duracao_b:.6f}",
                "-vf", VIDEO_FILTER_4K,
                "-r", "30", "-c:v", "libx264", "-preset", "medium",
                "-crf", "18", "-profile:v", "high", "-level:v", "5.1",
                "-tag:v", "avc1", "-color_range", "tv", "-an",
                "-movflags", "+faststart", str(seg_b)
            ])

            # ── Concat dos dois segmentos (sem áudio ainda) ──────────────────
            with open(lista_path, "w", encoding="utf-8") as f:
                f.write(f"file '{seg_a.as_posix()}'\n")
                f.write(f"file '{seg_b.as_posix()}'\n")
            self._video_executar_ffmpeg([
                ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-f", "concat", "-safe", "0", "-i", lista_path,
                "-c", "copy",
                "-movflags", "+faststart", str(sem_audio)
            ])

            # ── Mescla com áudio completo do original ────────────────────────
            self._video_executar_ffmpeg([
                ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(sem_audio),
                "-i", str(original),
                "-map", "0:v:0",
                "-map", "1:a:0?",
                "-t", f"{duracao_total:.6f}",
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(destino)
            ])
        finally:
            for tmp in [lista_path, str(seg_a), str(seg_b), str(sem_audio)]:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except Exception:
                    pass

    def _video_executar_ffmpeg(self, comando):
        processo = subprocess.run(
            comando, capture_output=True, text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if processo.returncode != 0:
            detalhe = (
                processo.stderr or processo.stdout or "falha desconhecida"
            ).strip()
            raise RuntimeError(detalhe[-1200:])

    def _video_finalizar(self, concluidos, erros):
        self._video_processando = False
        try:
            self._video_btn_processar.state(["!disabled"])
        except Exception:
            pass
        mensagem = f"{concluidos} item(ns) processado(s)."
        if erros:
            mensagem += "\n\nErros:\n" + "\n".join(erros[:8])
            messagebox.showwarning("Videos concluidos com erros", mensagem)
        else:
            mensagem += f"\n\nPronto: {READY_DIR}\nMotion: {MOTION_DIR}"
            messagebox.showinfo("Videos concluidos", mensagem)

    # =========================================================================
    # TAB 6 - MOTION
    # =========================================================================
    def _build_tab_motion(self):
        C = self.colors
        if not hasattr(self, "_motion_frame") or self._motion_frame is None:
            self._motion_frame = ttk.LabelFrame(self.notebook, text="Motion")
            self.notebook.add(self._motion_frame, text="  Motion  ")
        self._motion_busy = False
        self._motion_items = []
        self._motion_buttons = []

        motion_body = tk.Frame(self._motion_frame, bg=C["BG"])
        motion_body.pack(fill="both", expand=True, padx=14, pady=14)

        left = ttk.LabelFrame(motion_body, text="Fila e processamento")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_wrap = tk.Frame(motion_body, bg=C["BG"], width=520)
        right_wrap.pack(side="left", fill="y")
        right_wrap.pack_propagate(False)

        self._motion_right_canvas = tk.Canvas(
            right_wrap, bg=C["BG"], highlightthickness=0, borderwidth=0
        )
        self._motion_right_scrollbar = ttk.Scrollbar(
            right_wrap, orient="vertical", style="Vertical.TScrollbar", command=self._motion_right_canvas.yview
        )
        self._motion_right_canvas.configure(
            yscrollcommand=self._motion_right_scrollbar.set
        )
        self._motion_right_canvas.pack(side="left", fill="both", expand=True)
        self._motion_right_scrollbar.pack(side="right", fill="y")

        right = tk.Frame(self._motion_right_canvas, bg=C["BG"])
        self._motion_right_window = self._motion_right_canvas.create_window(
            (0, 0), window=right, anchor="nw"
        )

        queue = ttk.LabelFrame(left, text="Fila em assets/• Motion")
        queue.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(queue, style="Vertical.TScrollbar")
        scroll.pack(side="right", fill="y")
        self._motion_listbox = tk.Listbox(
            queue, bg=C["BG3"], fg=C["FG"],
            selectbackground=C["ACC"], selectforeground=C["FG"],
            font=("Consolas", 9), relief="flat", borderwidth=0,
            highlightthickness=0, yscrollcommand=scroll.set
        )
        self._motion_listbox.pack(fill="both", expand=True)
        scroll.config(command=self._motion_listbox.yview)
        queue_buttons = tk.Frame(queue, bg=C["BG2"])
        queue_buttons.pack(fill="x", pady=(8, 0))
        btn_motion_atualizar = ttk.Button(
            queue_buttons, text="Atualizar fila", command=self._motion_atualizar_fila
        )
        btn_motion_atualizar.pack(side="left", fill="x", expand=True, padx=(0, 3))
        btn_motion_limpar = ttk.Button(
            queue_buttons, text="Limpar Motion", command=self._motion_limpar_pasta
        )
        btn_motion_limpar.pack(side="left", fill="x", expand=True, padx=(3, 0))

        calibration = ttk.LabelFrame(
            right, text="Posicoes fixas na tela"
        )
        calibration.pack(fill="x", pady=(10, 0))
        calibration_buttons = tk.Frame(calibration, bg=C["BG2"])
        calibration_buttons.pack(fill="x")
        for tipo, texto in (
                ("video", "Apontar VIDEO"),
                ("imagem", "Apontar FOTO"),
                ("run", "Apontar RUN")):
            ttk.Button(
                calibration_buttons, text=texto,
                command=lambda t=tipo: self._motion_calibrar_posicao(t)
            ).pack(side="left", fill="x", expand=True, padx=2)
        self._motion_positions_label = tk.Label(
            calibration, text="", justify="left", anchor="w",
            bg=C["BG2"], fg=C["FG2"], font=("Consolas", 8)
        )
        self._motion_positions_label.pack(fill="x", pady=(6, 0))
        self._motion_use_positions_var = tk.BooleanVar(
            value=self.config.get("motion_use_screen_positions", False)
        )
        ttk.Checkbutton(
            calibration, text="Usar estas posicoes no upload e no RUN",
            variable=self._motion_use_positions_var,
            command=lambda: self.config.update({
                "motion_use_screen_positions":
                    self._motion_use_positions_var.get()
            })
        ).pack(anchor="w", pady=(4, 0))
        tk.Label(
            calibration,
            text=(
                "Clique em Apontar, deixe o mouse no local indicado "
                "e aguarde 5 segundos."
            ),
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8),
            justify="left"
        ).pack(fill="x", pady=(2, 0))
        tk.Label(
            calibration,
            text=(
                "Deixe DESMARCADO no uso normal: o envio acontece via "
                "DevTools (sem mouse), funciona com o Chrome em segundo "
                "plano e permite rodar varios perfis ao mesmo tempo. So "
                "marque isto como ultimo recurso, sabendo que nesse modo "
                "so 1 Chrome pode rodar por vez (o mouse e unico)."
            ),
            bg=C["BG2"], fg=C["WARN"], font=("Segoe UI", 8),
            justify="left", wraplength=380
        ).pack(fill="x", pady=(2, 0))
        self._motion_atualizar_posicoes_label()

        def _motion_right_configure_scroll(_event=None):
            try:
                self._motion_right_canvas.configure(
                    scrollregion=self._motion_right_canvas.bbox("all")
                )
            except Exception:
                pass

        def _motion_right_canvas_width(event):
            try:
                self._motion_right_canvas.itemconfigure(
                    self._motion_right_window, width=event.width
                )
            except Exception:
                pass

        def _motion_right_mousewheel(event):
            passo = self._mousewheel_delta(event)
            if passo:
                self._motion_right_canvas.yview_scroll(passo, "units")
            return "break"

        def _motion_right_bind_wheel(_event=None):
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                try:
                    self._motion_right_canvas.bind_all(
                        seq, _motion_right_mousewheel, add="+"
                    )
                except Exception:
                    pass

        def _motion_right_unbind_wheel(_event=None):
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                try:
                    self._motion_right_canvas.unbind_all(seq)
                except Exception:
                    pass

        right.bind("<Configure>", _motion_right_configure_scroll)
        self._motion_right_canvas.bind("<Configure>", _motion_right_canvas_width)
        self._motion_right_canvas.bind("<Enter>", _motion_right_bind_wheel)
        self._motion_right_canvas.bind("<Leave>", _motion_right_unbind_wheel)
        self._bind_canvas_mousewheel(self._motion_right_canvas, right)

        connection = ttk.LabelFrame(right, text="Perfis e conexão")
        connection.pack(fill="x")

        # ── lista de perfis (estilo Flow) ────────────────────────────────────
        profiles_body = tk.Frame(connection, bg=C["BG2"])
        profiles_body.pack(fill="x", pady=(0, 4))

        self.motion_profiles_checks_frame = tk.Frame(profiles_body, bg=C["BG2"])
        self.motion_profiles_checks_frame.pack(side="left", fill="y", padx=(0, 4))

        motion_list_wrap = tk.Frame(profiles_body, bg=C["BG3"], relief="flat", bd=0)
        motion_list_wrap.pack(side="left", fill="both", expand=True)
        self._motion_profiles_list_frame = tk.Frame(motion_list_wrap, bg=C["BG3"])
        self._motion_profiles_list_frame.pack(fill="both", expand=True)

        self.motion_profiles_listbox = tk.Listbox(
            profiles_body, height=0, width=0,
            bg=C["BG3"], fg=C["FG"],
            selectbackground=C["ACC"], selectforeground=C["FG"],
            font=("Consolas", 8), relief="flat", borderwidth=0,
            highlightthickness=0, exportselection=False
        )
        self.motion_profiles_listbox.pack_forget()
        self.motion_profiles_listbox.bind(
            "<<ListboxSelect>>", self._motion_profile_selecionado_editor
        )

        editor = tk.Frame(profiles_body, bg=C["BG2"])
        editor.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.motion_profile_active_var = tk.BooleanVar(value=True)
        tk.Label(
            editor, text="Nome:", bg=C["BG2"], fg=C["FG"],
            font=("Segoe UI", 8)
        ).grid(row=0, column=0, sticky="e", pady=2)
        self.motion_profile_name_var = tk.StringVar()
        ttk.Entry(
            editor, textvariable=self.motion_profile_name_var, width=13
        ).grid(row=0, column=1, columnspan=2, sticky="ew", padx=(4, 0), pady=2)
        tk.Label(
            editor, text="Porta:", bg=C["BG2"], fg=C["FG"],
            font=("Segoe UI", 8)
        ).grid(row=1, column=0, sticky="w", pady=2)
        self.motion_profile_port_var = tk.StringVar()
        ttk.Entry(
            editor, textvariable=self.motion_profile_port_var, width=8
        ).grid(row=1, column=1, columnspan=2, sticky="w", padx=(4, 0), pady=2)
        editor.columnconfigure(2, weight=1)

        prof_buttons = tk.Frame(connection, bg=C["BG2"])
        prof_buttons.pack(fill="x", pady=(0, 4))
        ttk.Button(
            prof_buttons, text="Novo",
            command=self._motion_profile_novo
        ).pack(side="left", padx=(0, 3))
        ttk.Button(
            prof_buttons, text="Salvar",
            command=self._motion_profile_salvar
        ).pack(side="left", padx=3)
        ttk.Button(
            prof_buttons, text="Excluir",
            command=self._motion_profile_excluir
        ).pack(side="left", padx=3)
        open_button = ttk.Button(
            prof_buttons, text="Abrir selecionado",
            command=self._motion_abrir_perfil_selecionado
        )
        open_button.pack(side="left", padx=3)
        reset_button = ttk.Button(
            connection, text="Testar conexao com perfil aberto",
            command=self._motion_testar_conexao_aberta
        )
        reset_button.pack(fill="x", pady=(0, 3))
        tk.Label(
            connection,
            text=(
                "Clique em Novo para criar um perfil isolado. "
                "Abrir selecionado abre o Chrome para voce fazer login "
                "(o login fica salvo para proximas vezes).\n"
                "Apos abrir, clique em Testar conexao."
            ),
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8),
            justify="left", wraplength=380
        ).pack(fill="x", pady=(4, 0))

        credenciais = ttk.LabelFrame(right, text="Token RunningHub")
        credenciais.pack(fill="x", pady=(10, 0))
        btn_credenciais = ttk.Button(
            credenciais, text="Capturar token no Perfil 1",
            style="Accent.TButton",
            command=self._motion_capturar_credenciais_iniciar
        )
        btn_credenciais.pack(fill="x")
        self._motion_token_label = tk.Label(
            credenciais, text="", justify="left", anchor="w",
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8),
            wraplength=380
        )
        self._motion_token_label.pack(fill="x", pady=(4, 0))
        self._motion_atualizar_token_label()

        creditos = ttk.LabelFrame(right, text="Créditos diários")
        creditos.pack(fill="x", pady=(10, 0))
        creditos_row = tk.Frame(creditos, bg=C["BG2"])
        creditos_row.pack(fill="x", pady=(0, 4))
        tk.Label(
            creditos_row, text="Fechar apos (s):",
            bg=C["BG2"], fg=C["FG"]
        ).pack(side="left")
        self._motion_creditos_delay_var = tk.StringVar(
            value=self.config.get("motion_creditos_delay", "30")
        )
        ttk.Entry(
            creditos_row, textvariable=self._motion_creditos_delay_var,
            width=8
        ).pack(side="right")
        self._motion_creditos_delay_var.trace_add(
            "write",
            lambda *a: self.config.update({
                "motion_creditos_delay": self._motion_creditos_delay_var.get()
            })
        )
        btn_creditos = ttk.Button(
            creditos, text="Creditos diarios", style="Accent.TButton",
            command=self._motion_creditos_diarios_iniciar
        )
        btn_creditos.pack(fill="x")
        self._motion_creditos_status_label = tk.Label(
            creditos, text="", bg=C["BG2"], fg=C["ACCFG"],
            font=("Segoe UI", 8), justify="left", anchor="w", wraplength=380
        )
        self._motion_creditos_status_label.pack(fill="x", pady=(5, 0))
        self._motion_creditos_atualizar_label(agendar=True)
        tk.Label(
            creditos,
            text=(
                "Abre todos os perfis ativos no link do Motion, aguarda "
                "o tempo definido acima e fecha todos os Chrome."
            ),
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8),
            justify="left", wraplength=380
        ).pack(fill="x", pady=(4, 0))

        timers = ttk.LabelFrame(right, text="Intervalos e paralelismo")
        timers.pack(fill="x", pady=(10, 0))
        row1 = tk.Frame(timers, bg=C["BG2"])
        row1.pack(fill="x", pady=3)
        tk.Label(
            row1, text="Apos selecionar as midias (s):",
            bg=C["BG2"], fg=C["FG"]
        ).pack(side="left")
        self._motion_media_delay_var = tk.StringVar(
            value=self.config.get("motion_media_delay", "5")
        )
        ttk.Entry(
            row1, textvariable=self._motion_media_delay_var, width=8
        ).pack(side="right")
        self._motion_media_delay_var.trace_add(
            "write",
            lambda *a: self.config.update({
                "motion_media_delay": self._motion_media_delay_var.get()
            })
        )

        row2 = tk.Frame(timers, bg=C["BG2"])
        row2.pack(fill="x", pady=3)
        tk.Label(
            row2, text="Aguardar video ficar pronto (min):",
            bg=C["BG2"], fg=C["FG"]
        ).pack(side="left")
        minutos_salvos = self.config.get("motion_generation_minutes")
        if minutos_salvos is None:
            try:
                minutos_salvos = (
                    float(self.config.get("motion_generation_delay", "120"))
                    / 60
                )
                minutos_salvos = (
                    str(int(minutos_salvos))
                    if minutos_salvos.is_integer()
                    else f"{minutos_salvos:g}"
                )
            except (TypeError, ValueError):
                minutos_salvos = "2"
        self.config["motion_generation_minutes"] = str(minutos_salvos)
        self._motion_generation_delay_var = tk.StringVar(
            value=str(minutos_salvos)
        )
        ttk.Entry(
            row2, textvariable=self._motion_generation_delay_var, width=8
        ).pack(side="right")
        self._motion_generation_delay_var.trace_add(
            "write",
            lambda *a: self.config.update({
                "motion_generation_minutes":
                    self._motion_generation_delay_var.get()
            })
        )

        row3 = tk.Frame(timers, bg=C["BG2"])
        row3.pack(fill="x", pady=3)
        tk.Label(
            row3, text="Aguardar Chrome abrir (s):",
            bg=C["BG2"], fg=C["FG"]
        ).pack(side="left")
        self._motion_aguardar_abrir_var = tk.StringVar(
            value=self.config.get("motion_aguardar_abrir", "10")
        )
        ttk.Entry(
            row3, textvariable=self._motion_aguardar_abrir_var, width=8
        ).pack(side="right")
        self._motion_aguardar_abrir_var.trace_add(
            "write",
            lambda *a: self.config.update({
                "motion_aguardar_abrir":
                    self._motion_aguardar_abrir_var.get()
            })
        )
        tk.Label(
            timers,
            text=(
                "Usado quando 'Processar fila' detecta que o perfil "
                "ainda nao esta aberto: o Mimic abre o Chrome sozinho e "
                "espera esse tempo antes de conectar."
            ),
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8),
            justify="left", wraplength=380
        ).pack(fill="x", pady=(2, 0))

        row4 = tk.Frame(timers, bg=C["BG2"])
        row4.pack(fill="x", pady=3)
        tk.Label(
            row4, text="Maximo de perfis simultaneos:",
            bg=C["BG2"], fg=C["FG"]
        ).pack(side="left")
        self._motion_max_paralelo_var = tk.StringVar(
            value=self.config.get("motion_max_paralelo", "2")
        )
        ttk.Entry(
            row4, textvariable=self._motion_max_paralelo_var, width=8
        ).pack(side="right")
        self._motion_max_paralelo_var.trace_add(
            "write",
            lambda *a: self.config.update({
                "motion_max_paralelo": self._motion_max_paralelo_var.get()
            })
        )
        tk.Label(
            timers,
            text=(
                "Quantos Chrome(s) podem rodar ao mesmo tempo durante "
                "'Processar fila'. Os perfis ativos sao divididos em "
                "grupos desse tamanho e usados em rodadas (grupo 1 "
                "processa um lote de videos, depois fecha e o grupo 2 "
                "processa o lote seguinte, e assim por diante, "
                "voltando ao grupo 1 quando todos os grupos ja "
                "tiverem sido usados). Reduza se o PC nao aguentar "
                "todos os perfis ativos abertos ao mesmo tempo."
            ),
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8),
            justify="left", wraplength=380
        ).pack(fill="x", pady=(2, 0))

        calibration.pack_forget()
        calibration.pack(fill="x", pady=(10, 0))

        info = ttk.LabelFrame(right, text="Item de teste")
        info.pack(fill="x", pady=(10, 0))
        self._motion_item_label = tk.Label(
            info, text="Nenhum item encontrado.", justify="left",
            anchor="w", bg=C["BG2"], fg=C["FG2"], wraplength=380
        )
        self._motion_item_label.pack(fill="x")

        tests = ttk.LabelFrame(left, text="Ações")
        tests.pack(fill="x", pady=(10, 0))
        btn_all = ttk.Button(
            tests, text="Processar fila completa", style="Accent.TButton",
            command=lambda: self._motion_iniciar_acao("all")
        )
        btn_all.pack(fill="x")

        tests_row = tk.Frame(tests, bg=C["BG2"])
        tests_row.pack(fill="x", pady=(6, 0))
        btn_upload = ttk.Button(
            tests_row, text="1. Enviar mídia",
            command=lambda: self._motion_iniciar_acao("upload")
        )
        btn_upload.pack(side="left", fill="x", expand=True, padx=(0, 3))
        btn_run = ttk.Button(
            tests_row, text="2. RUN",
            command=lambda: self._motion_iniciar_acao("run")
        )
        btn_run.pack(side="left", fill="x", expand=True, padx=3)
        btn_download = ttk.Button(
            tests_row, text="3. Baixar",
            command=lambda: self._motion_iniciar_acao("download")
        )
        btn_download.pack(side="left", fill="x", expand=True, padx=(3, 0))

        tests_row2 = tk.Frame(tests, bg=C["BG2"])
        tests_row2.pack(fill="x", pady=(4, 0))
        btn_testar_painel = ttk.Button(
            tests_row2, text="Testar painel/video",
            command=self._motion_testar_painel_video
        )
        btn_testar_painel.pack(side="left", fill="x", expand=True, padx=(0, 3))
        btn_testar_marca_dagua = ttk.Button(
            tests_row2, text="Testar marca d'agua",
            command=self._motion_testar_marca_dagua
        )
        btn_testar_marca_dagua.pack(side="left", fill="x", expand=True, padx=(3, 0))

        posproc = ttk.LabelFrame(left, text="Pós-processamento")
        posproc.pack(fill="x", pady=(10, 0))
        self.config["motion_remover_marca_dagua"] = True
        self._motion_marca_dagua_var = tk.BooleanVar(
            value=self.config.get("motion_remover_marca_dagua", True)
        )
        ttk.Checkbutton(
            posproc,
            text="Aplicar tarja preta no topo e exportar video Motion em 4K",
            variable=self._motion_marca_dagua_var,
            command=lambda: self.config.update({
                "motion_remover_marca_dagua":
                    self._motion_marca_dagua_var.get()
            })
        ).pack(anchor="w")
        tk.Label(
            posproc,
            text=(
                "Aplicado automaticamente apos cada download (botao "
                "'3. Baixar video' e 'Processar fila'). Precisa do "
                "FFmpeg instalado e no PATH. O audio e reconvertido "
                "para AAC para garantir compatibilidade com celular."
            ),
            bg=C["BG2"], fg=C["FG2"], font=("Segoe UI", 8),
            justify="left", wraplength=380
        ).pack(fill="x", pady=(2, 0))

        self._motion_buttons = [
            open_button, reset_button,
            btn_upload, btn_run, btn_download, btn_testar_painel,
            btn_all, btn_creditos, btn_credenciais,
            btn_testar_marca_dagua, btn_motion_atualizar, btn_motion_limpar
        ]
        self._motion_status_label = tk.Label(
            right, text="Pronto.", bg=C["BG"], fg=C["FG2"],
            justify="left", anchor="w", wraplength=400
        )
        self._motion_status_label.pack(fill="x", pady=(12, 0))
        self._motion_atualizar_fila()
        self._motion_profiles_carregar()

    # ── profile helpers (estilo Flow) ────────────────────────────────────────

    def _motion_profiles_padrao(self):
        return [{
            "id": "motion_1",
            "name": "Perfil 1",
            "port": "9223",
            "session": f"{MOTION_SESSION_BASE}_1",
            "active": True,
        }]

    def _motion_profiles_obter(self):
        perfis = self.config.get("motion_profiles", [])
        # migra formato antigo (lista de dicts com chave "perfil")
        if perfis and isinstance(perfis[0], dict) and "perfil" in perfis[0]:
            perfis = []
        if not isinstance(perfis, list) or not perfis:
            perfis = self._motion_profiles_padrao()
            self.config["motion_profiles"] = perfis
        normalizados = []
        for indice, p in enumerate(perfis, 1):
            if not isinstance(p, dict):
                continue
            normalizados.append({
                "id": str(p.get("id") or f"motion_{indice}"),
                "name": str(p.get("name") or f"Perfil {indice}").strip(),
                "port": str(p.get("port") or (9222 + indice)).strip(),
                "session": str(
                    p.get("session") or f"{MOTION_SESSION_BASE}_{indice}"
                ),
                "active": bool(p.get("active", True)),
            })
        if not normalizados:
            normalizados = self._motion_profiles_padrao()
        self.config["motion_profiles"] = normalizados
        return normalizados

    def _motion_profiles_salvar_config(self):
        save_json(CONFIG_FILE, self.config)

    def _motion_profiles_carregar(self, selecionar=0):
        self.motion_profiles_listbox.delete(0, "end")
        if hasattr(self, "motion_profiles_checks_frame"):
            for w in self.motion_profiles_checks_frame.winfo_children():
                w.destroy()
        if hasattr(self, "_motion_profiles_list_frame"):
            for w in self._motion_profiles_list_frame.winfo_children():
                w.destroy()
        self._motion_profile_check_vars = {}
        self._motion_profile_row_frames = {}
        C = self.colors
        perfis = self._motion_profiles_obter()
        for indice, perfil in enumerate(perfis):
            var = tk.BooleanVar(value=perfil["active"])
            self._motion_profile_check_vars[indice] = var

            if hasattr(self, "_motion_profiles_list_frame"):
                row = tk.Frame(self._motion_profiles_list_frame, bg=C["BG3"], cursor="hand2")
                row.pack(fill="x", pady=0)
                self._motion_profile_row_frames[indice] = row

                def _toggle_profile(i=indice, v=var):
                    self._motion_profile_toggle_active(i, v.get())
                    self._motion_profile_selecionar_linha(i)
                cb = ttk.Checkbutton(row, variable=var, command=_toggle_profile)
                cb.pack(side="left", padx=(5, 2))

                lbl = tk.Label(
                    row,
                    text=f"{perfil['name']}  |  {perfil['port']}",
                    bg=C["BG3"], fg=C["FG"], font=("Consolas", 8),
                    anchor="w", cursor="hand2"
                )
                lbl.pack(side="left", fill="x", expand=True, padx=(2, 4), pady=3)

                def _select_row(e, i=indice):
                    self._motion_profile_selecionar_linha(i)
                for w in (row, lbl):
                    w.bind("<Button-1>", _select_row)

            self.motion_profiles_listbox.insert(
                "end",
                f"{'✓' if perfil['active'] else ' '} {perfil['name']} | porta {perfil['port']}"
            )

        if perfis:
            selecionar = max(0, min(selecionar, len(perfis) - 1))
            self.motion_profiles_listbox.selection_clear(0, "end")
            self.motion_profiles_listbox.selection_set(selecionar)
            self.motion_profiles_listbox.activate(selecionar)
            self._motion_profile_selecionar_linha(selecionar)
            self._motion_profile_carregar_editor(selecionar)

    def _motion_profile_selecionar_linha(self, indice):
        C = self.colors
        if not hasattr(self, "_motion_profile_row_frames"):
            return
        for i, row in self._motion_profile_row_frames.items():
            bg = C["ACC"] if i == indice else C["BG3"]
            fg = C["FG"] if i == indice else C["FG"]
            row.configure(bg=bg)
            for w in row.winfo_children():
                try:
                    if isinstance(w, tk.Label):
                        w.configure(bg=bg, fg=fg)
                except Exception:
                    pass
        self.motion_profiles_listbox.selection_clear(0, "end")
        self.motion_profiles_listbox.selection_set(indice)
        self.motion_profiles_listbox.activate(indice)
        self._motion_profile_carregar_editor(indice)

    def _motion_profile_toggle_active(self, indice, ativo):
        perfis = self._motion_profiles_obter()
        if indice is None or not (0 <= indice < len(perfis)):
            return
        perfis[indice]["active"] = bool(ativo)
        self.config["motion_profiles"] = perfis
        self._motion_profiles_salvar_config()
        self.motion_profiles_listbox.delete(indice)
        marcador = "✓" if ativo else " "
        perfil = perfis[indice]
        self.motion_profiles_listbox.insert(
            indice, f"[{marcador}] {perfil['name']} | porta {perfil['port']}"
        )
        self.motion_profiles_listbox.selection_clear(0, "end")
        self.motion_profiles_listbox.selection_set(indice)
        self.motion_profiles_listbox.activate(indice)
        self.motion_profile_active_var.set(bool(ativo))
        self._log(f"Perfil Motion {'ativado' if ativo else 'desativado'}: {perfil['name']}")

    def _motion_profile_indice(self):
        selecao = self.motion_profiles_listbox.curselection()
        return selecao[0] if selecao else None

    def _motion_profile_carregar_editor(self, indice):
        perfis = self._motion_profiles_obter()
        if indice is None or not (0 <= indice < len(perfis)):
            return
        p = perfis[indice]
        self.motion_profile_active_var.set(p["active"])
        self.motion_profile_name_var.set(p["name"])
        self.motion_profile_port_var.set(p["port"])

    def _motion_profile_selecionado_editor(self, _event=None):
        self._motion_profile_carregar_editor(self._motion_profile_indice())

    def _motion_profile_selecionado_dados(self):
        indice = self._motion_profile_indice()
        perfis = self._motion_profiles_obter()
        if indice is None or not (0 <= indice < len(perfis)):
            return None
        return dict(perfis[indice])

    def _motion_porta_ativa(self):
        """Porta do perfil selecionado na listbox (fallback 9223)."""
        p = self._motion_profile_selecionado_dados()
        return p["port"] if p else "9223"

    def _motion_profile_salvar(self):
        indice = self._motion_profile_indice()
        if indice is None:
            return
        nome = self.motion_profile_name_var.get().strip()
        porta = self.motion_profile_port_var.get().strip()
        if not nome:
            messagebox.showerror("Perfil Motion", "Informe um nome para o perfil.")
            return
        try:
            porta_num = int(porta)
            if not (1024 <= porta_num <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Perfil Motion", "Porta invalida (1024-65535).")
            return
        perfis = self._motion_profiles_obter()
        for i, outro in enumerate(perfis):
            if i != indice and outro["port"] == str(porta_num):
                messagebox.showerror(
                    "Perfil Motion",
                    f"A porta {porta_num} ja esta sendo usada por '{outro['name']}'."
                )
                return
        perfis[indice].update({
            "name": nome,
            "port": str(porta_num),
            "active": self.motion_profile_active_var.get(),
        })
        self.config["motion_profiles"] = perfis
        self._motion_profiles_salvar_config()
        self._motion_profiles_carregar(indice)

    def _motion_profile_novo(self):
        perfis = self._motion_profiles_obter()
        portas_usadas = {
            int(p["port"]) for p in perfis
            if str(p.get("port", "")).isdigit()
        }
        porta = 9223
        while porta in portas_usadas:
            porta += 1
        numero = 1
        ids = {p["id"] for p in perfis}
        while f"motion_{numero}" in ids:
            numero += 1
        perfil = {
            "id": f"motion_{numero}",
            "name": f"Perfil {numero}",
            "port": str(porta),
            "session": f"{MOTION_SESSION_BASE}_{numero}",
            "active": True,
        }
        perfis.append(perfil)
        self.config["motion_profiles"] = perfis
        self._motion_profiles_salvar_config()
        self._motion_profiles_carregar(len(perfis) - 1)

    def _motion_profile_excluir(self):
        indice = self._motion_profile_indice()
        perfis = self._motion_profiles_obter()
        if indice is None or len(perfis) <= 1:
            messagebox.showwarning(
                "Perfil Motion", "Deve existir pelo menos um perfil."
            )
            return
        perfil = perfis[indice]
        if not messagebox.askyesno(
                "Excluir perfil",
                f"Excluir '{perfil['name']}' da lista?\n\n"
                "O login salvo ainda sera mantido no computador."):
            return
        perfis.pop(indice)
        self.config["motion_profiles"] = perfis
        self._motion_profiles_salvar_config()
        self._motion_profiles_carregar(max(0, indice - 1))

    def _motion_perfis_ativos(self):
        """Retorna lista de dicts dos perfis marcados como ativos."""
        return [p for p in self._motion_profiles_obter() if p.get("active")]

    def _motion_max_paralelo(self):
        """Le o limite de Chromes simultaneos configurado pelo usuario.
        Sempre retorna pelo menos 1. Se o campo estiver vazio/invalido,
        usa 1 (sem paralelismo) para nao sobrecarregar o PC por engano."""
        try:
            valor = int(str(self._motion_max_paralelo_var.get()).strip())
        except (ValueError, AttributeError):
            return 1
        return max(1, valor)

    def _motion_abrir_perfil_selecionado(self):
        """Abre o Chrome com debug remoto usando a session isolada do perfil
        selecionado. Se a pasta ainda nao existe, o Chrome abre em branco e
        o login feito fica salvo ali para as proximas vezes."""
        perfil = self._motion_profile_selecionado_dados()
        if not perfil:
            messagebox.showwarning("Motion", "Selecione um perfil.")
            return
        chrome = self._motion_chrome_path()
        if not chrome:
            messagebox.showerror("Motion", "Chrome nao encontrado.")
            return
        session_path = Path(perfil["session"])
        perfil_existe = session_path.exists()
        session_path.mkdir(parents=True, exist_ok=True)
        subprocess.Popen([
            str(chrome),
            f"--remote-debugging-port={perfil['port']}",
            f"--user-data-dir={perfil['session']}",
            "--no-first-run",
            "--no-default-browser-check",
            MOTION_LOGIN_URL,
        ])
        self._log(
            f"Chrome Motion aberto: {perfil['name']} | "
            f"porta {perfil['port']} | {MOTION_LOGIN_URL}"
        )
        self._motion_status_label.configure(
            text=(
                f"Chrome ({perfil['name']}) aberto com debug na porta "
                f"{perfil['port']}. Faca login (se necessario) e clique "
                "em Testar conexao."
            )
        )
        if not perfil_existe:
            messagebox.showinfo(
                "Novo perfil Motion",
                f"Um perfil novo foi criado para '{perfil['name']}'.\n\n"
                "1. Faca login manualmente na pagina aberta.\n"
                "2. O login fica salvo neste perfil para as proximas vezes.\n"
                "3. Volte ao Mimic e clique em Testar conexao."
            )

    def _motion_creditos_status_texto(self):
        ts = self.config.get("motion_creditos_last_opened_ts")
        if not ts:
            return "Ultima abertura: nunca\nStatus: ja pode abrir para pegar creditos."
        try:
            ts = float(ts)
        except (TypeError, ValueError):
            return "Ultima abertura: registro invalido\nStatus: ja pode abrir para pegar creditos."
        ultima = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(ts))
        restante = max(0, (24 * 60 * 60) - (time.time() - ts))
        if restante <= 0:
            return f"Ultima abertura: {ultima}\nStatus: ja pode pegar creditos novamente."
        horas = int(restante // 3600)
        minutos = int((restante % 3600) // 60)
        return f"Ultima abertura: {ultima}\nFaltam: {horas:02d}h {minutos:02d}min para tentar novamente."

    def _motion_creditos_atualizar_label(self, agendar=False):
        try:
            if hasattr(self, "_motion_creditos_status_label"):
                self._motion_creditos_status_label.config(
                    text=self._motion_creditos_status_texto()
                )
        except Exception:
            pass
        if agendar:
            try:
                self.after(60000, lambda: self._motion_creditos_atualizar_label(agendar=True))
            except Exception:
                pass

    def _motion_creditos_registrar_abertura(self):
        self.config["motion_creditos_last_opened_ts"] = time.time()
        save_json(CONFIG_FILE, self.config)
        self._motion_creditos_atualizar_label()

    def _motion_creditos_diarios_segundos(self):
        try:
            return max(1, int(float(self._motion_creditos_delay_var.get())))
        except (ValueError, AttributeError):
            return 30

    def _motion_creditos_diarios_iniciar(self):
        """Abre todos os perfis Motion ativos na URL configurada, aguarda
        alguns segundos (tempo para a pagina creditar o acesso diario) e
        fecha todos os Chrome em seguida."""
        if self._motion_busy:
            return
        perfis = self._motion_perfis_ativos()
        if not perfis:
            messagebox.showwarning(
                "Creditos diarios", "Marque pelo menos um perfil como ativo."
            )
            return
        chrome = self._motion_chrome_path()
        if not chrome:
            messagebox.showerror("Creditos diarios", "Chrome nao encontrado.")
            return
        segundos = self._motion_creditos_diarios_segundos()
        self._motion_creditos_registrar_abertura()
        self._motion_busy = True
        for botao in self._motion_buttons:
            botao.state(["disabled"])
        self._motion_status_label.configure(
            text=(
                f"Creditos diarios: abrindo {len(perfis)} perfil(is)..."
            )
        )
        threading.Thread(
            target=self._motion_creditos_diarios_worker,
            args=(perfis, chrome, segundos),
            daemon=True
        ).start()

    def _motion_creditos_diarios_worker(self, perfis, chrome, segundos):
        erro = None
        abertos = []
        try:
            for perfil in perfis:
                session_path = Path(perfil["session"])
                session_path.mkdir(parents=True, exist_ok=True)
                subprocess.Popen([
                    str(chrome),
                    f"--remote-debugging-port={perfil['port']}",
                    f"--user-data-dir={perfil['session']}",
                    "--no-first-run",
                    "--no-default-browser-check",
                    MOTION_LOGIN_URL,
                ])
                abertos.append(perfil["name"])
                self._log(
                    f"Creditos diarios: Chrome aberto para "
                    f"{perfil['name']} | porta {perfil['port']}"
                )
                time.sleep(0.4)
            self.after(
                0, lambda: self._motion_status_label.configure(
                    text=(
                        f"Creditos diarios: {len(abertos)} perfil(is) "
                        f"aberto(s). Aguardando {segundos}s antes de "
                        "fechar..."
                    )
                )
            )
            time.sleep(segundos)
        except Exception as exc:
            erro = str(exc)
            self._log(f"Creditos diarios ERRO: {erro}")
        finally:
            self._motion_fechar_chrome()
            self._log("Creditos diarios: Chrome fechado.")
        self.after(
            0, lambda: self._motion_creditos_diarios_finalizar(abertos, erro)
        )

    def _motion_creditos_diarios_finalizar(self, abertos, erro):
        self._motion_busy = False
        for botao in self._motion_buttons:
            botao.state(["!disabled"])
        if erro:
            self._motion_status_label.configure(text=f"Erro: {erro}")
            messagebox.showerror("Creditos diarios", erro)
        else:
            resumo = (
                f"{len(abertos)} perfil(is) processado(s) e Chrome "
                "fechado:\n" + "\n".join(abertos)
            )
            self._motion_status_label.configure(
                text="Creditos diarios: concluido. Chrome fechado."
            )
            messagebox.showinfo("Creditos diarios", resumo)

    def _motion_perfis_chrome(self):
        if not CHROME_USER_DATA.exists():
            return []
        perfis = []
        for pasta in CHROME_USER_DATA.iterdir():
            if not pasta.is_dir():
                continue
            if pasta.name == "Default" or (
                    pasta.name.startswith("Profile ")
                    and pasta.name[8:].isdigit()):
                perfis.append(pasta.name)
        return sorted(
            perfis,
            key=lambda nome: (
                nome != "Default",
                int(nome[8:]) if nome.startswith("Profile ") else -1
            )
        )

    def _motion_posicoes_tela(self):
        posicoes = self.config.get("motion_screen_positions", {})
        return posicoes if isinstance(posicoes, dict) else {}

    def _motion_posicao_tela(self, tipo):
        valor = self._motion_posicoes_tela().get(tipo)
        if (
                not isinstance(valor, (list, tuple))
                or len(valor) != 2):
            return None
        try:
            return int(valor[0]), int(valor[1])
        except (TypeError, ValueError):
            return None

    def _motion_atualizar_posicoes_label(self):
        if not hasattr(self, "_motion_positions_label"):
            return
        nomes = {"video": "VIDEO", "imagem": "FOTO ", "run": "RUN  "}
        linhas = []
        for tipo in ("video", "imagem", "run"):
            posicao = self._motion_posicao_tela(tipo)
            valor = (
                f"X={posicao[0]}  Y={posicao[1]}"
                if posicao else "nao definida"
            )
            linhas.append(f"{nomes[tipo]}: {valor}")
        self._motion_positions_label.configure(text="   |   ".join(linhas))

    def _motion_calibrar_posicao(self, tipo):
        if not SCREEN_AUTOMATION_AVAILABLE:
            messagebox.showerror(
                "Calibrar Motion",
                "As bibliotecas pyautogui e pyperclip nao estao instaladas."
            )
            return
        nomes = {
            "video": "campo do VIDEO (seta roxa)",
            "imagem": "campo da FOTO (seta vermelha)",
            "run": "botao RUN",
        }
        messagebox.showinfo(
            "Calibrar posicao",
            f"O Mimic sera minimizado.\n\n"
            f"Deixe o cursor exatamente sobre o {nomes[tipo]}.\n"
            "A posicao sera capturada em 5 segundos."
        )
        self.iconify()
        threading.Thread(
            target=self._motion_capturar_posicao_worker,
            args=(tipo,), daemon=True
        ).start()

    def _motion_capturar_posicao_worker(self, tipo):
        time.sleep(5)
        try:
            ponto = pyautogui.position()
            erro = None
        except Exception as exc:
            ponto = None
            erro = str(exc)
        self.after(
            0, lambda: self._motion_finalizar_calibracao(tipo, ponto, erro)
        )

    def _motion_finalizar_calibracao(self, tipo, ponto, erro):
        self.deiconify()
        self.lift()
        if erro:
            messagebox.showerror("Calibrar Motion", erro)
            return
        posicoes = dict(self._motion_posicoes_tela())
        posicoes[tipo] = [int(ponto.x), int(ponto.y)]
        self.config["motion_screen_positions"] = posicoes
        save_json(CONFIG_FILE, self.config)
        self._motion_atualizar_posicoes_label()
        nomes = {"video": "VIDEO", "imagem": "FOTO", "run": "RUN"}
        self._motion_status_label.configure(
            text=f"{nomes[tipo]} salvo em X={ponto.x}, Y={ponto.y}."
        )

    def _motion_chrome_path(self):
        candidatos = [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        ]
        return next((path for path in candidatos if path.exists()), None)

    def _motion_chrome_em_execucao(self):
        try:
            resultado = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                capture_output=True, text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            return "chrome.exe" in resultado.stdout.lower()
        except Exception:
            return False

    def _motion_fechar_chrome(self):
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "chrome.exe"],
                capture_output=True, text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
        except Exception:
            pass

    def _motion_porta_respondendo(self, porta, timeout=1.5):
        """Verifica se ha um Chrome com debug remoto respondendo nesta
        porta (sem depender do MCP, so um GET simples no endpoint
        padrao do DevTools)."""
        try:
            with urllib.request.urlopen(
                    f"http://localhost:{porta}/json/version",
                    timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _motion_abrir_chrome_perfil(self, perfil):
        """Abre o Chrome com debug remoto para este perfil (mesmo
        padrao usado em 'Abrir selecionado' e 'Creditos diarios')."""
        chrome = self._motion_chrome_path()
        if not chrome:
            raise RuntimeError("Chrome nao encontrado.")
        session_path = Path(perfil["session"])
        session_path.mkdir(parents=True, exist_ok=True)
        subprocess.Popen([
            str(chrome),
            f"--remote-debugging-port={perfil['port']}",
            f"--user-data-dir={perfil['session']}",
            "--no-first-run",
            "--no-default-browser-check",
            MOTION_LOGIN_URL,
        ])

    def _motion_garantir_perfil_aberto(self, perfil, rotulo=""):
        """Se a porta do perfil ja estiver respondendo, nao faz nada.
        Caso contrario, abre o Chrome sozinho e aguarda o tempo
        configurado em 'Aguardar Chrome abrir' antes de seguir, para
        dar tempo da pagina carregar antes de tentar conectar."""
        prefixo = f"{rotulo} " if rotulo else ""
        porta = perfil.get("port")
        if self._motion_porta_respondendo(porta):
            return False
        self._log(
            f"{prefixo}Perfil '{perfil.get('name', '?')}' nao estava "
            f"aberto na porta {porta}. Abrindo Chrome..."
        )
        self._motion_abrir_chrome_perfil(perfil)
        espera = self._motion_aguardar_abrir_segundos()
        self._log(
            f"{prefixo}Aguardando {espera}s para a pagina carregar..."
        )
        time.sleep(espera)
        return True

    def _motion_aguardar_abrir_segundos(self):
        try:
            return max(1, int(float(
                self._motion_aguardar_abrir_var.get()
            )))
        except (ValueError, AttributeError):
            return 10

    def _motion_pressionar_esc_repetido(
            self, vezes=5, intervalo=3.0, rotulo="",
            cliente=None, usar_posicoes=False):
        """Envia ESC 'vezes' vezes, esperando 'intervalo' segundos
        entre cada uma. Usado antes de enviar foto+video para fechar
        possiveis popups/dialogs deixados abertos na pagina.

        Quando 'cliente' (MotionMcpClient) e informado, primeiro traz a
        pagina RunningHub daquele perfil para frente e entao envia ESC.
        O ESC fisico tambem e usado quando pyautogui esta disponivel,
        porque alguns popups do site so fecham com a janela em foco."""
        prefixo = f"{rotulo} " if rotulo else ""
        for i in range(1, vezes + 1):
            try:
                if cliente is not None and not usar_posicoes:
                    try:
                        self._motion_mcp_selecionar_runninghub(cliente)
                        time.sleep(0.15)
                    except Exception as exc:
                        self._log(
                            f"{prefixo}Aviso: nao foi possivel focar "
                            f"RunningHub antes do ESC: {exc}"
                        )
                    cliente.tool("evaluate_script", {"function": """
                        () => {
                            try { window.focus(); } catch (e) {}
                            const alvos = [
                                document,
                                window,
                                document.activeElement,
                            ].filter(Boolean);
                            for (const alvo of alvos) {
                                for (const tipo of
                                        ['keydown', 'keyup']) {
                                    alvo.dispatchEvent(
                                        new KeyboardEvent(tipo, {
                                            key: 'Escape',
                                            code: 'Escape',
                                            keyCode: 27,
                                            which: 27,
                                            bubbles: true,
                                            cancelable: true,
                                        })
                                    );
                                }
                            }
                            return true;
                        }
                    """}, timeout=15)
                    if SCREEN_AUTOMATION_AVAILABLE:
                        time.sleep(0.15)
                        pyautogui.click(
                            pyautogui.size().width // 2,
                            pyautogui.size().height // 2
                        )
                        time.sleep(0.1)
                        pyautogui.press("esc")
                elif SCREEN_AUTOMATION_AVAILABLE:
                    pyautogui.click(
                        pyautogui.size().width // 2,
                        pyautogui.size().height // 2
                    )
                    time.sleep(0.1)
                    pyautogui.press("esc")
                else:
                    self._log(
                        f"{prefixo}Aviso: nenhuma forma de enviar ESC "
                        "disponivel (sem cliente MCP e sem pyautogui)."
                    )
                    return
            except Exception as exc:
                self._log(f"{prefixo}Falha ao enviar ESC: {exc}")
                break
            self._log(f"{prefixo}ESC {i}/{vezes}")
            if i < vezes:
                time.sleep(intervalo)

    def _motion_testar_conexao_aberta(self):
        if self._motion_busy:
            return
        self._motion_busy = True
        for botao in self._motion_buttons:
            botao.state(["disabled"])
        self._motion_status_label.configure(
            text="Solicitando acesso ao perfil aberto. Clique Allow no Chrome..."
        )
        threading.Thread(
            target=self._motion_testar_mcp_worker,
            daemon=True
        ).start()

    def _motion_testar_mcp_worker(self):
        cliente = MotionMcpClient(log=self._log)
        erro = None
        paginas = ""
        try:
            cliente.start(porta=self._motion_porta_ativa())
            paginas = cliente.tool("list_pages", timeout=120)
            if "runninghub.ai" not in paginas:
                raise RuntimeError(
                    "Conexao autorizada, mas a pagina RunningHub nao esta "
                    "aberta neste perfil."
                )
        except Exception as exc:
            erro = str(exc)
        finally:
            cliente.close()
        self.after(
            0, lambda: self._motion_finalizar_teste_mcp(paginas, erro)
        )

    def _motion_finalizar_teste_mcp(self, paginas, erro):
        self._motion_busy = False
        for botao in self._motion_buttons:
            botao.state(["!disabled"])
        if erro:
            self._motion_status_label.configure(text=f"Erro: {erro}")
            messagebox.showerror("Conexao Motion", erro)
        else:
            self._motion_status_label.configure(
                text="Perfil aberto conectado. RunningHub encontrado."
            )
            messagebox.showinfo(
                "Conexao Motion",
                "Perfil existente conectado e pagina RunningHub encontrada."
            )

    def _motion_testar_painel_video(self):
        """Botao de teste: conecta no Chrome do perfil ativo, clica no
        hide-btn pra abrir o painel de resultado e tenta ler o src do
        video que aparece dentro dele. Nao baixa nada -- so confirma
        que os seletores estao funcionando."""
        if self._motion_busy:
            messagebox.showinfo(
                "Motion", "Ja existe uma operacao Motion em andamento."
            )
            return
        self._motion_busy = True
        for botao in self._motion_buttons:
            botao.state(["disabled"])
        self._motion_status_label.configure(
            text="Testando painel de resultado e video..."
        )
        threading.Thread(
            target=self._motion_testar_painel_video_worker,
            daemon=True
        ).start()

    def _motion_testar_painel_video_worker(self):
        cliente = MotionMcpClient(log=self._log)
        erro = None
        src = ""
        try:
            cliente.start(porta=self._motion_porta_ativa())
            self._motion_mcp_selecionar_runninghub(cliente)
            src = self._motion_mcp_video_src(cliente)
            if not src:
                raise RuntimeError(
                    "Painel aberto, mas nenhum video foi encontrado "
                    "(o video pode ainda nao ter sido gerado)."
                )
        except Exception as exc:
            erro = str(exc)
        finally:
            cliente.close()
        self.after(
            0, lambda: self._motion_finalizar_teste_painel_video(src, erro)
        )

    def _motion_finalizar_teste_painel_video(self, src, erro):
        self._motion_busy = False
        for botao in self._motion_buttons:
            botao.state(["!disabled"])
        if erro:
            self._motion_status_label.configure(text=f"Erro: {erro}")
            messagebox.showerror("Testar painel/video", erro)
        else:
            resumo = src if len(src) <= 200 else f"{src[:200]}..."
            self._motion_status_label.configure(
                text=f"Painel aberto e video encontrado: {resumo}"
            )
            messagebox.showinfo(
                "Testar painel/video",
                f"Painel aberto e video encontrado.\n\nsrc: {resumo}"
            )

    def _motion_testar_marca_dagua(self):
        """Botao de teste: deixa escolher um video qualquer, faz uma
        copia e aplica a remocao de marca d'agua (tarja preta + 4K +
        audio AAC) nessa copia, sem tocar no arquivo original."""
        if self._motion_busy:
            messagebox.showinfo(
                "Motion", "Ja existe uma operacao Motion em andamento."
            )
            return
        caminho = filedialog.askopenfilename(
            title="Escolha um video para testar a remocao de marca d'agua",
            filetypes=[
                ("Videos", "*.mp4 *.mov *.m4v *.mkv *.avi"),
                ("Todos os arquivos", "*.*"),
            ]
        )
        if not caminho:
            return
        origem = Path(caminho)
        self._motion_busy = True
        for botao in self._motion_buttons:
            botao.state(["disabled"])
        self._motion_status_label.configure(
            text=f"Testando remocao de marca d'agua em {origem.name}..."
        )
        threading.Thread(
            target=self._motion_testar_marca_dagua_worker,
            args=(origem,), daemon=True
        ).start()

    def _motion_testar_marca_dagua_worker(self, origem):
        erro = None
        destino = None
        try:
            destino = origem.with_name(
                f"{origem.stem}_teste_sem_marca{origem.suffix}"
            )
            shutil.copy2(str(origem), str(destino))
            self._motion_remover_marca_dagua(destino)
        except Exception as exc:
            erro = str(exc)
        self.after(
            0, lambda: self._motion_finalizar_teste_marca_dagua(destino, erro)
        )

    def _motion_finalizar_teste_marca_dagua(self, destino, erro):
        self._motion_busy = False
        for botao in self._motion_buttons:
            botao.state(["!disabled"])
        if erro:
            self._motion_status_label.configure(text=f"Erro: {erro}")
            messagebox.showerror("Testar remocao de marca d'agua", erro)
        else:
            self._motion_status_label.configure(
                text=f"Teste concluido: {destino}"
            )
            messagebox.showinfo(
                "Testar remocao de marca d'agua",
                f"Video de teste gerado (4K, sem marca d'agua, audio "
                f"AAC):\n\n{destino}\n\nO original nao foi alterado."
            )

    def _motion_token_status_texto(self):
        info = rh_token_info()
        qs = info.get("qs", "")
        expire = info.get("signExpire", 0)
        if not qs:
            return "Token salvo: nenhum."
        return (
            "Token salvo em assets/rh_token.json\n"
            f"Expira em: {rh_token_expiracao_texto(expire)}"
        )

    def _motion_atualizar_token_label(self):
        if hasattr(self, "_motion_token_label"):
            self._motion_token_label.configure(
                text=self._motion_token_status_texto()
            )

    def _motion_capturar_credenciais_iniciar(self):
        if self._motion_busy:
            messagebox.showwarning(
                "Motion", "Ja existe uma operacao Motion em andamento."
            )
            return
        if not PLAYWRIGHT_AVAILABLE:
            messagebox.showerror("Motion", "Playwright nao esta instalado.")
            return

        perfis = self._motion_profiles_obter()
        if not perfis:
            messagebox.showerror("Motion", "Nenhum perfil Motion configurado.")
            return

        perfil = dict(perfis[0])
        self._motion_busy = True
        for botao in self._motion_buttons:
            botao.state(["disabled"])
        self._motion_status_label.configure(
            text=f"Capturando token no {perfil['name']}..."
        )
        threading.Thread(
            target=self._motion_capturar_credenciais_worker,
            args=(perfil,),
            daemon=True
        ).start()

    def _motion_capturar_credenciais_worker(self, perfil):
        erro = None
        info = None
        url = ""
        try:
            self._motion_garantir_perfil_aberto(
                perfil, rotulo="[Credenciais]"
            )
            url, info = asyncio.run(
                self._motion_capturar_credenciais_async(perfil)
            )
        except Exception as exc:
            erro = str(exc)
        self.after(
            0,
            lambda: self._motion_capturar_credenciais_finalizar(
                info, url, erro
            )
        )

    async def _motion_enviar_video_captura_token_async(self, page, item):
        detalhes = await self._motion_detalhar_inputs_async(page)
        if not detalhes:
            raise RuntimeError("Campo de upload do video nao encontrado.")
        video_input = self._motion_escolher_input(
            detalhes, "video", set()
        )
        if not video_input:
            raise RuntimeError("Campo de upload do video nao encontrado.")
        self._log(
            "Credenciais: enviando video para capturar /upload/image..."
        )
        await video_input["campo"].set_input_files(str(item["video"]))

    async def _motion_capturar_credenciais_async(self, perfil):
        porta = perfil.get("port") or self._motion_porta_ativa()
        async with async_playwright() as playwright:
            browser, context, page = await self._motion_conectar_async(
                playwright, porta
            )
            await page.bring_to_front()
            loop = asyncio.get_running_loop()
            futuro = loop.create_future()

            def _capturar(request):
                if futuro.done():
                    return
                url = request.url
                if (
                        MOTION_RELOAD_YAMLS_ENDPOINT in url
                        and "Rh-Comfy-Auth=" in url):
                    futuro.set_result(url)

            context.on("request", _capturar)
            page.on("request", _capturar)
            espera = self._motion_aguardar_abrir_segundos()
            self._log(
                f"Credenciais: aguardando {espera}s antes de recarregar..."
            )
            await asyncio.sleep(espera)
            self._log(
                "Credenciais: recarregando pagina para capturar "
                "reload_yamls..."
            )
            await page.reload(wait_until="domcontentloaded", timeout=60000)
            self._log(
                f"Credenciais: aguardando mais {espera}s apos recarregar..."
            )
            try:
                url = await asyncio.wait_for(futuro, timeout=max(30, espera))
            except asyncio.TimeoutError as exc:
                raise RuntimeError(
                    "Nao encontrei a request /sum_text_list/reload_yamls "
                    "com Rh-Comfy-Auth no Network apos recarregar a pagina."
                ) from exc

            qs = url.split("?", 1)[1] if "?" in url else ""
            if not qs or "Rh-Comfy-Auth=" not in qs:
                raise RuntimeError(
                    "Request capturada nao tinha Rh-Comfy-Auth."
                )
            info = rh_token_salvar(qs)
            if not info:
                raise RuntimeError("Nao foi possivel salvar assets/rh_token.json.")
            self._log(
                "Credenciais capturadas. Expira em: "
                f"{rh_token_expiracao_texto(info.get('signExpire'))}"
            )
            return url, info

    def _motion_capturar_credenciais_finalizar(self, info, url, erro):
        self._motion_busy = False
        for botao in self._motion_buttons:
            botao.state(["!disabled"])
        self._motion_atualizar_token_label()
        if erro:
            self._motion_status_label.configure(text=f"Erro: {erro}")
            messagebox.showerror("Credenciais RunningHub", erro)
            return
        expire = rh_token_expiracao_texto(info.get("signExpire"))
        self._motion_status_label.configure(
            text=f"Token capturado. Expira em: {expire}"
        )
        messagebox.showinfo(
            "Credenciais RunningHub",
            "Token capturado e salvo em assets/rh_token.json.\n\n"
            f"Expira em: {expire}\n\n"
            f"URL capturada:\n{url}"
        )

    def _motion_perfil_token_para_fila(
            self, perfis_ativos, perfil_selecionado=None,
            perfis_para_rodar=None):
        """Escolhe o perfil usado para renovar o token automaticamente
        antes de iniciar o processamento da fila Motion.

        Preferencia:
        1. primeiro perfil que realmente sera usado na fila;
        2. primeiro perfil ativo;
        3. perfil selecionado no editor;
        4. primeiro perfil cadastrado.
        """
        candidatos = []
        if isinstance(perfis_para_rodar, list):
            candidatos.extend(perfis_para_rodar)
        if isinstance(perfis_ativos, list):
            candidatos.extend(perfis_ativos)
        if perfil_selecionado:
            candidatos.append(perfil_selecionado)
        candidatos.extend(self._motion_profiles_obter())
        for perfil in candidatos:
            if isinstance(perfil, dict) and perfil.get("port"):
                return dict(perfil)
        return None

    def _motion_preparar_token_e_executar_fila_worker(
            self, perfil_token, perfis_para_rodar, acao, itens,
            media_delay, generation_delay, usar_posicoes):
        """Renova o token RunningHub sozinho antes da fila Motion.

        O botao 'Processar fila' sempre passa por aqui: primeiro abre/
        reutiliza o Chrome do perfil escolhido, recarrega o workflow,
        captura uma URL com Rh-Comfy-Auth no Network, salva assets/rh_token.json
        e so entao dispara a fila normal.
        """
        try:
            if not PLAYWRIGHT_AVAILABLE:
                raise RuntimeError(
                    "Playwright nao esta instalado. Instale com: "
                    "pip install playwright && playwright install chromium"
                )
            if not perfil_token:
                raise RuntimeError(
                    "Nenhum perfil Motion configurado para capturar o token."
                )

            nome = perfil_token.get("name", "Perfil")
            self._log(
                f"Motion: atualizando token automaticamente antes da fila "
                f"usando {nome}..."
            )
            self.after(
                0,
                lambda: self._motion_status_label.configure(
                    text=f"Atualizando token antes da fila usando {nome}..."
                )
            )
            self._motion_garantir_perfil_aberto(
                perfil_token, rotulo="[Token fila]"
            )
            url, info = asyncio.run(
                self._motion_capturar_credenciais_async(perfil_token)
            )
            expire = rh_token_expiracao_texto(info.get("signExpire"))
            self._log(
                f"Motion: token atualizado automaticamente. "
                f"Expira em: {expire}"
            )
            self.after(0, self._motion_atualizar_token_label)
            self.after(
                0,
                lambda: self._motion_status_label.configure(
                    text="Token atualizado. Iniciando fila Motion..."
                )
            )

            self._motion_executar_em_perfis(
                perfis_para_rodar, acao, itens, media_delay,
                generation_delay, usar_posicoes
            )
        except Exception as exc:
            erro = f"Falha ao atualizar token antes da fila: {exc}"
            self._log(f"Motion ERRO: {erro}")
            self.after(
                0,
                lambda: self._motion_finalizar_acao(acao, [], erro)
            )

    def _motion_listar_itens(self, root=None):
        root = Path(root or MOTION_DIR)
        if not root.exists():
            return []
        video_exts = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
        image_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        itens = []
        pastas = [root] + sorted(
            [p for p in root.rglob("*") if p.is_dir()],
            key=lambda p: str(p).lower()
        )
        for pasta in pastas:
            arquivos = [p for p in pasta.iterdir() if p.is_file()]
            videos = sorted(
                [p for p in arquivos if p.suffix.lower() in video_exts],
                key=lambda p: p.name.lower()
            )
            imagens = sorted(
                [p for p in arquivos if p.suffix.lower() in image_exts],
                key=lambda p: (
                    0 if p.name.lower().startswith("framenew") else 1,
                    p.name.lower()
                )
            )
            if not videos or not imagens:
                continue
            relativo = pasta.relative_to(root)
            modelo = (
                relativo.parts[0] if relativo.parts
                else self._detectar_modelo_pasta(pasta.name) or "Sem modelo"
            )
            itens.append({
                "pasta": pasta,
                "modelo": modelo,
                "video": videos[0],
                "imagem": imagens[0],
            })
        return itens

    def _motion_atualizar_fila(self):
        self._motion_items = self._motion_listar_itens()
        self._motion_listbox.delete(0, "end")
        for item in self._motion_items:
            self._motion_listbox.insert(
                "end", f"{item['modelo']} | {item['pasta'].name}"
            )
        if self._motion_items:
            item = self._motion_items[0]
            self._motion_item_label.configure(
                text=(
                    f"Modelo: {item['modelo']}\n"
                    f"Video: {item['video'].name}\n"
                    f"Foto: {item['imagem'].name}"
                )
            )
        else:
            self._motion_item_label.configure(
                text="Nenhum par de foto + video encontrado em assets/• Motion."
            )

    def _motion_limpar_pasta(self):
        if getattr(self, "_motion_busy", False):
            messagebox.showinfo(
                "Motion", "Ja existe uma operacao Motion em andamento."
            )
            return
        MOTION_DIR.mkdir(parents=True, exist_ok=True)
        itens = [p for p in sorted(MOTION_DIR.iterdir(), key=lambda x: x.name.lower())]
        if not itens:
            self._motion_atualizar_fila()
            messagebox.showinfo("Motion", "A pasta assets/• Motion ja esta vazia.")
            return
        if not messagebox.askyesno(
            "Limpar Motion",
            f"Apagar {len(itens)} item(ns) dentro de:\n{MOTION_DIR}?"
        ):
            return

        base = MOTION_DIR.resolve()
        apagados = 0
        erros = []
        for item in itens:
            try:
                alvo = item.resolve()
                if alvo.parent != base:
                    raise RuntimeError("caminho fora de assets/• Motion")
                if alvo.is_dir():
                    shutil.rmtree(alvo)
                else:
                    alvo.unlink()
                apagados += 1
            except Exception as exc:
                erros.append(f"{item.name}: {exc}")

        self._motion_atualizar_fila()
        self._log(f"Motion: {apagados} item(ns) apagado(s) de assets/• Motion.")
        if erros:
            messagebox.showwarning(
                "Limpar Motion",
                "Alguns itens nao foram apagados:\n" + "\n".join(erros[:8])
            )

    def _motion_ler_intervalo(self, variavel, nome):
        try:
            valor = float(variavel.get().strip())
            if valor < 0:
                raise ValueError
            return valor
        except ValueError:
            raise ValueError(f"Intervalo invalido: {nome}")

    def _motion_validar_posicoes(self, acao):
        if not self._motion_use_positions_var.get():
            return
        necessarias = []
        if acao in {"upload", "all"}:
            necessarias.extend(("video", "imagem"))
        if acao in {"run", "all"}:
            necessarias.append("run")
        faltando = [
            tipo.upper() for tipo in necessarias
            if not self._motion_posicao_tela(tipo)
        ]
        if faltando:
            raise ValueError(
                "Calibre antes as posicoes: " + ", ".join(faltando)
            )

    def _motion_iniciar_acao(self, acao):
        if self._motion_busy:
            messagebox.showinfo(
                "Motion", "Ja existe uma operacao Motion em andamento."
            )
            return
        self._motion_atualizar_fila()
        if acao in {"upload", "download", "all"} and not self._motion_items:
            messagebox.showinfo(
                "Motion",
                "Nenhum par de foto + video foi encontrado em assets/• Motion."
            )
            return
        try:
            media_delay = self._motion_ler_intervalo(
                self._motion_media_delay_var, "apos selecionar as midias"
            )
            generation_minutes = self._motion_ler_intervalo(
                self._motion_generation_delay_var,
                "video pronto em minutos"
            )
            generation_delay = generation_minutes * 60
            self._motion_validar_posicoes(acao)
        except ValueError as exc:
            messagebox.showerror("Motion", str(exc))
            return

        self._motion_busy = True
        for botao in self._motion_buttons:
            botao.state(["disabled"])
        itens = [dict(item) for item in self._motion_items]
        usar_posicoes = self._motion_use_positions_var.get()

        perfis_ativos = self._motion_perfis_ativos()
        perfil_selecionado = self._motion_profile_selecionado_dados()
        rodar_em_paralelo = (
            acao == "all"
            and not usar_posicoes
            and len(perfis_ativos) > 1
        )
        if rodar_em_paralelo:
            perfis_para_rodar = perfis_ativos
        else:
            perfis_para_rodar = [
                perfil_selecionado
                or (perfis_ativos[0] if perfis_ativos else {
                    "name": "padrao", "port": self._motion_porta_ativa()
                })
            ]
            if usar_posicoes and acao == "all" and len(perfis_ativos) > 1:
                self._log(
                    "Aviso: com 'Usar estas posicoes' marcado, so 1 "
                    "Chrome roda por vez (o mouse e unico). Desmarque a "
                    "opcao para processar varios perfis em paralelo."
                )

        if acao == "all":
            perfil_token = self._motion_perfil_token_para_fila(
                perfis_ativos, perfil_selecionado, perfis_para_rodar
            )
            self._motion_status_label.configure(
                text=(
                    f"Atualizando token antes da fila usando "
                    f"{perfil_token.get('name', 'Perfil')}..."
                    if perfil_token else "Atualizando token antes da fila..."
                )
            )
        else:
            perfil_token = None
            self._motion_status_label.configure(
                text=(
                    f"Conectando a {len(perfis_para_rodar)} Chrome(s)..."
                    if len(perfis_para_rodar) > 1 else "Conectando ao Chrome..."
                )
            )
        if usar_posicoes and acao in {"upload", "run", "all"}:
            self.iconify()
        if acao == "all":
            threading.Thread(
                target=self._motion_preparar_token_e_executar_fila_worker,
                args=(
                    perfil_token, perfis_para_rodar, acao, itens,
                    media_delay, generation_delay, usar_posicoes
                ),
                daemon=True
            ).start()
        else:
            self._motion_executar_em_perfis(
                perfis_para_rodar, acao, itens, media_delay,
                generation_delay, usar_posicoes
            )

    def _motion_mcp_selecionar_runninghub(self, cliente):
        paginas = cliente.tool("list_pages", timeout=120)
        encontrados = []
        fallback = []
        for linha in paginas.splitlines():
            match = re.match(r"\s*(\d+)\s*[:.)-]\s*(.*)", linha)
            if not match:
                continue
            page_id = int(match.group(1))
            texto = match.group(2).strip()
            fallback.append((page_id, texto))
            if "runninghub" in texto.lower():
                encontrados.append((page_id, texto))
        if not encontrados:
            if not fallback:
                self._log(
                    "Motion: list_pages nao retornou paginas; usando "
                    "a aba ativa do perfil."
                )
                return ""
            self._log(
                "Motion: pagina RunningHub nao apareceu no list_pages; "
                "usando a ultima aba aberta do perfil."
            )
            encontrados = fallback
        page_id, url = encontrados[-1]
        cliente.tool(
            "select_page",
            {"pageId": page_id, "bringToFront": True},
            timeout=30
        )
        return url

    def _motion_mcp_valor(self, texto):
        match = re.search(r"```json\s*(.*?)\s*```", texto, re.S)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return match.group(1)
        return texto.strip()

    def _motion_mcp_upload_uids(self, cliente):
        cliente.tool("evaluate_script", {"function": """
            () => {
                const inputs = [...document.querySelectorAll('input[type="file"]')];
                const used = new Set();
                const describe = (el) => {
                    let node = el;
                    let text = '';
                    for (let i = 0; i < 6 && node; i++, node = node.parentElement) {
                        text += ' ' + (node.innerText || node.title || '');
                    }
                    return text.toLowerCase();
                };
                const score = (el, type) => {
                    const accept = (el.accept || '').toLowerCase();
                    const text = describe(el);
                    let value = 0;
                    if (accept.includes(type)) value += 100;
                    if (type === 'video' && accept.includes('image')) value -= 100;
                    if (type === 'image' && accept.includes('video')) value -= 100;
                    if (type === 'video' && /video|filme/.test(text)) value += 25;
                    if (type === 'image' && /image|imagem|foto/.test(text)) value += 25;
                    return value;
                };
                const pick = type => inputs
                    .map((el, index) => ({el, index, score: score(el, type)}))
                    .filter(item => !used.has(item.index))
                    .sort((a, b) => b.score - a.score)[0];
                const mark = (item, label) => {
                    if (!item) return;
                    used.add(item.index);
                    item.el.setAttribute('aria-label', label);
                    item.el.setAttribute('title', label);
                    const opener = item.el.closest('label') ||
                        item.el.parentElement?.querySelector('button') ||
                        item.el.parentElement;
                    if (opener) {
                        opener.setAttribute('aria-label', label);
                        opener.setAttribute('title', label);
                    }
                };
                mark(pick('video'), 'SWAP_VIDEO_UPLOAD');
                mark(pick('image'), 'SWAP_IMAGE_UPLOAD');
                return inputs.length;
            }
        """}, timeout=30)
        snapshot = cliente.tool(
            "take_snapshot", {"verbose": True}, timeout=60
        )
        video_match = re.search(
            r"uid=([^\s]+).*SWAP_VIDEO_UPLOAD", snapshot, re.I
        )
        image_match = re.search(
            r"uid=([^\s]+).*SWAP_IMAGE_UPLOAD", snapshot, re.I
        )
        if not video_match or not image_match:
            raise RuntimeError(
                "Nao foi possivel identificar os dois campos de upload "
                "no snapshot da pagina."
            )
        return video_match.group(1), image_match.group(1)

    def _motion_mcp_enviar_midias(self, cliente, item):
        video_uid, image_uid = self._motion_mcp_upload_uids(cliente)
        cliente.tool(
            "upload_file",
            {"uid": video_uid, "filePath": str(item["video"])},
            timeout=90
        )
        cliente.tool(
            "upload_file",
            {"uid": image_uid, "filePath": str(item["imagem"])},
            timeout=90
        )
        self._log(
            f"Motion enviado: {item['video'].name} + {item['imagem'].name}"
        )

    # ── Workflow novo (RunningHub / LiteGraph no canvas) ───────────────────
    # Esse workflow novo desenha os campos de FOTO e VIDEO dentro do
    # <canvas>, sem elementos DOM clicaveis equivalentes. O VIDEO ainda usa
    # um <input type="file"> escondido (igual ao workflow antigo), mas a
    # FOTO sobe via fetch('/upload/image') disparado pelo JS interno do
    # ComfyUI somente depois que o usuario escolhe o arquivo no dialogo
    # nativo do Windows -- nao existe input[type=file] reaproveitavel para
    # ela. Por isso a FOTO e enviada replicando esse mesmo fetch dentro da
    # propria pagina (usando a sessao/cookies ja autenticados do navegador)
    # e depois atualizando o widget "image" do node LoadImage no grafo.

    def _motion_mcp_enviar_video_v2(self, cliente, video_path):
        """Envia o video via fetch('/upload/image?Rh-Comfy-Auth=...').
        O token e lido do arquivo assets/rh_token.json (valido 7 dias).
        Atualiza o widget 'video' do node VHS_LoadVideo no grafo."""
        video_path = Path(video_path).resolve()
        if not video_path.exists():
            raise RuntimeError(f"Video nao encontrado: {video_path}")
        qs = rh_token_obter(parent=self)
        if not qs:
            raise RuntimeError("Token RunningHub nao fornecido. Operacao cancelada.")
        dados_b64 = base64.b64encode(
            video_path.read_bytes()
        ).decode("ascii")
        endpoint = MOTION_UPLOAD_IMAGE_ENDPOINT + "?" + qs
        texto = cliente.tool("evaluate_script", {"function": f"""
            async () => {{
                const b64 = {json.dumps(dados_b64)};
                const nomeArquivo = {json.dumps(video_path.name)};
                const tipoNode = {json.dumps(MOTION_NODE_TYPE_VIDEO)};
                const nomeWidget = {json.dumps(MOTION_WIDGET_VIDEO)};
                const endpoint = {json.dumps(endpoint)};

                const binario = atob(b64);
                const bytes = new Uint8Array(binario.length);
                for (let i = 0; i < binario.length; i++) {{
                    bytes[i] = binario.charCodeAt(i);
                }}
                const blob = new Blob([bytes]);

                const formData = new FormData();
                formData.append('image', blob, nomeArquivo);

                const resposta = await fetch(endpoint, {{
                    method: 'POST',
                    body: formData,
                }});
                if (!resposta.ok) {{
                    throw new Error(
                        `Upload do video falhou: HTTP ${{resposta.status}}`
                    );
                }}
                const corpo = await resposta.json();
                const nomeFinal = corpo.name;
                if (!nomeFinal) {{
                    throw new Error('Resposta do upload sem nome de arquivo.');
                }}


                // Acessa o grafo dentro do iframe comfyUI.html
                function obterGrafo() {{
                    const iframes = [...document.querySelectorAll('iframe')];
                    for (const f of iframes) {{
                        try {{
                            const w = f.contentWindow;
                            const g = w?.graph || w?.app?.graph;
                            if (g && Array.isArray(g.nodes)) return g;
                        }} catch(e) {{}}
                    }}
                    const g = window.graph || window.app?.graph;
                    if (g && Array.isArray(g.nodes)) return g;
                    throw new Error('Grafo do ComfyUI nao encontrado no iframe comfyUI.html.');
                }}
                const grafo = obterGrafo();
                const node = grafo.nodes.find(n => n.type === tipoNode);
                if (!node) {{
                    throw new Error(`Node ${{tipoNode}} nao encontrado no grafo.`);
                }}
                const widget = (node.widgets || []).find(w => w.name === nomeWidget);
                if (!widget) {{
                    throw new Error(`Widget ${{nomeWidget}} nao encontrado no node.`);
                }}
                if (
                        Array.isArray(widget.options?.values)
                        && !widget.options.values.includes(nomeFinal)) {{
                    widget.options.values.push(nomeFinal);
                }}
                widget.value = nomeFinal;
                if (typeof widget.callback === 'function') {{
                    widget.callback(nomeFinal, grafo.canvas, node);
                }}
                node.setDirtyCanvas?.(true, true);
                grafo.canvas?.setDirty?.(true, true);
                grafo.setDirtyCanvas?.(true, true);

                return nomeFinal;
            }}
        """}, timeout=120)
        nome_final = self._motion_mcp_valor(texto)
        self._log(f"Motion video enviado: {video_path.name} -> {nome_final}")

    def _motion_mcp_enviar_foto_v2(self, cliente, imagem_path):
        """Envia a foto via fetch('/upload/image?Rh-Comfy-Auth=...').
        O token e lido do arquivo assets/rh_token.json (valido 7 dias).
        Atualiza o widget 'image' do node LoadImage no grafo."""
        imagem_path = Path(imagem_path).resolve()
        if not imagem_path.exists():
            raise RuntimeError(f"Imagem nao encontrada: {imagem_path}")
        qs = rh_token_obter(parent=self)
        if not qs:
            raise RuntimeError("Token RunningHub nao fornecido. Operacao cancelada.")
        dados_b64 = base64.b64encode(
            imagem_path.read_bytes()
        ).decode("ascii")
        endpoint = MOTION_UPLOAD_IMAGE_ENDPOINT + "?" + qs
        texto = cliente.tool("evaluate_script", {"function": f"""
            async () => {{
                const b64 = {json.dumps(dados_b64)};
                const nomeArquivo = {json.dumps(imagem_path.name)};
                const tipoNode = {json.dumps(MOTION_NODE_TYPE_IMAGEM)};
                const nomeWidget = {json.dumps(MOTION_WIDGET_IMAGEM)};
                const endpoint = {json.dumps(endpoint)};

                const binario = atob(b64);
                const bytes = new Uint8Array(binario.length);
                for (let i = 0; i < binario.length; i++) {{
                    bytes[i] = binario.charCodeAt(i);
                }}
                const blob = new Blob([bytes]);

                const formData = new FormData();
                formData.append('image', blob, nomeArquivo);

                const resposta = await fetch(endpoint, {{
                    method: 'POST',
                    body: formData,
                }});
                if (!resposta.ok) {{
                    throw new Error(
                        `Upload da foto falhou: HTTP ${{resposta.status}}`
                    );
                }}
                const corpo = await resposta.json();
                const nomeFinal = corpo.name;
                if (!nomeFinal) {{
                    throw new Error(
                        'Resposta do upload sem nome de arquivo.'
                    );
                }}

                // Acessa o grafo dentro do iframe comfyUI.html
                function obterGrafo() {{
                    const iframes = [...document.querySelectorAll('iframe')];
                    for (const f of iframes) {{
                        try {{
                            const w = f.contentWindow;
                            const g = w?.graph || w?.app?.graph;
                            if (g && Array.isArray(g.nodes)) return g;
                        }} catch(e) {{}}
                    }}
                    const g = window.graph || window.app?.graph;
                    if (g && Array.isArray(g.nodes)) return g;
                    throw new Error('Grafo do ComfyUI nao encontrado no iframe comfyUI.html.');
                }}
                const grafo = obterGrafo();
                const node = grafo.nodes.find(n => n.type === tipoNode);
                if (!node) {{
                    throw new Error(
                        `Node ${{tipoNode}} nao encontrado no grafo.`
                    );
                }}
                const widget = (node.widgets || []).find(
                    w => w.name === nomeWidget
                );
                if (!widget) {{
                    throw new Error(
                        `Widget ${{nomeWidget}} nao encontrado no node.`
                    );
                }}
                if (
                        Array.isArray(widget.options?.values)
                        && !widget.options.values.includes(nomeFinal)) {{
                    widget.options.values.push(nomeFinal);
                }}
                widget.value = nomeFinal;
                if (typeof widget.callback === 'function') {{
                    widget.callback(nomeFinal, grafo.canvas, node);
                }}
                node.setDirtyCanvas?.(true, true);
                grafo.canvas?.setDirty?.(true, true);
                grafo.setDirtyCanvas?.(true, true);

                return nomeFinal;
            }}
        """}, timeout=90)
        nome_final = self._motion_mcp_valor(texto)
        self._log(f"Motion foto enviada: {imagem_path.name} -> {nome_final}")
        return nome_final

    def _motion_mcp_enviar_midias_v2(self, cliente, item):
        self._motion_mcp_enviar_video_v2(cliente, item["video"])
        self._motion_mcp_enviar_foto_v2(cliente, item["imagem"])
        self._log(
            f"Motion enviado (workflow novo): "
            f"{item['video'].name} + {item['imagem'].name}"
        )

    def _motion_tela_selecionar_arquivo(self, tipo, arquivo):
        posicao = self._motion_posicao_tela(tipo)
        if not posicao:
            raise RuntimeError(f"Posicao de {tipo} nao foi calibrada.")
        arquivo = Path(arquivo).resolve()
        if not arquivo.exists():
            raise RuntimeError(f"Arquivo nao encontrado: {arquivo}")
        if not WINDOWS_DIALOG_AUTOMATION_AVAILABLE:
            raise RuntimeError(
                "A automacao da janela Abrir requer o pacote pywin32."
            )

        dialogos_anteriores = set(self._motion_dialogos_arquivo())
        pyautogui.click(*posicao)
        dialogo = self._motion_aguardar_dialogo_arquivo(
            ignorar=dialogos_anteriores, timeout=12
        )
        campo = self._motion_campo_nome_arquivo(dialogo)
        botao_abrir = win32gui.GetDlgItem(dialogo, 1)
        if not campo or not botao_abrir:
            raise RuntimeError(
                "A janela Abrir apareceu, mas os controles Nome/Abrir "
                "nao foram encontrados."
            )

        win32gui.SetForegroundWindow(dialogo)
        win32gui.SendMessage(
            campo, win32con.WM_SETTEXT, 0, str(arquivo)
        )
        time.sleep(0.3)
        win32gui.SendMessage(
            botao_abrir, win32con.BM_CLICK, 0, 0
        )

        limite = time.monotonic() + 15
        while time.monotonic() < limite and win32gui.IsWindow(dialogo):
            time.sleep(0.2)
        if win32gui.IsWindow(dialogo):
            raise RuntimeError(
                "A janela Abrir nao confirmou o arquivo. Verifique se "
                "o tipo de arquivo e aceito pelo campo."
            )
        time.sleep(2)

    def _motion_campo_nome_arquivo(self, dialogo):
        encontrado = []

        def visitar(hwnd, _):
            try:
                if (
                        win32gui.GetClassName(hwnd) == "Edit"
                        and win32gui.GetDlgCtrlID(hwnd) == 1148
                        and win32gui.IsWindowVisible(hwnd)):
                    encontrado.append(hwnd)
            except Exception:
                pass

        win32gui.EnumChildWindows(dialogo, visitar, None)
        return encontrado[0] if encontrado else None

    def _motion_dialogos_arquivo(self):
        encontrados = []

        def visitar(hwnd, _):
            try:
                if (
                        win32gui.IsWindowVisible(hwnd)
                        and win32gui.GetClassName(hwnd) == "#32770"
                        and self._motion_campo_nome_arquivo(hwnd)
                        and win32gui.GetDlgItem(hwnd, 1)):
                    encontrados.append(hwnd)
            except Exception:
                pass

        win32gui.EnumWindows(visitar, None)
        return encontrados

    def _motion_aguardar_dialogo_arquivo(self, ignorar=None, timeout=12):
        ignorar = set(ignorar or ())
        limite = time.monotonic() + timeout
        while time.monotonic() < limite:
            novos = [
                hwnd for hwnd in self._motion_dialogos_arquivo()
                if hwnd not in ignorar
            ]
            if novos:
                return novos[-1]
            time.sleep(0.2)
        raise RuntimeError(
            "A janela Abrir nao apareceu. Confirme a posicao calibrada "
            "e deixe o Chrome visivel no mesmo monitor."
        )

    def _motion_tela_enviar_midias(self, item):
        if not SCREEN_AUTOMATION_AVAILABLE:
            raise RuntimeError(
                "pyautogui e pyperclip sao necessarios para o modo fixo."
            )
        self._motion_tela_selecionar_arquivo("video", item["video"])
        self._motion_tela_selecionar_arquivo("imagem", item["imagem"])
        self._log(
            f"Motion enviado por posicao fixa: "
            f"{item['video'].name} + {item['imagem'].name}"
        )

    def _motion_tela_run(self):
        if not SCREEN_AUTOMATION_AVAILABLE:
            raise RuntimeError("pyautogui nao esta instalado.")
        posicao = self._motion_posicao_tela("run")
        if not posicao:
            raise RuntimeError("Posicao do RUN nao foi calibrada.")
        pyautogui.click(*posicao)
        self._log(
            f"Motion RUN clicado por posicao fixa: "
            f"X={posicao[0]}, Y={posicao[1]}"
        )

    def _motion_mcp_run(self, cliente):
        texto = cliente.tool("evaluate_script", {"function": f"""
            () => {{
                const target = document.querySelector(
                    {json.dumps(MOTION_RUN_SELECTOR)}
                );
                const button = target?.closest('button') || target ||
                    [...document.querySelectorAll('button')]
                        .find(el => el.textContent.trim() === 'Run');
                if (!button) throw new Error('Botao RUN nao encontrado');
                button.click();
                return true;
            }}
        """}, timeout=30)
        self._log(f"Motion RUN: {self._motion_mcp_valor(texto)}")

    def _motion_mcp_abrir_painel_resultado(self, cliente):
        """Clica no botao que abre/expande o painel de resultado
        (workflow-result-wrap), onde o video gerado fica visivel.
        Se o painel ja estiver aberto ou o botao nao existir, nao faz
        nada (nao e' erro)."""
        texto = cliente.tool("evaluate_script", {"function": f"""
            () => {{
                const btn = document.querySelector(
                    {json.dumps(MOTION_RESULT_HIDE_BTN_SELECTOR)}
                );
                if (btn) {{
                    btn.click();
                    return 'painel aberto';
                }}
                return 'painel ja aberto ou botao nao encontrado';
            }}
        """}, timeout=15)
        self._log(f"Motion painel: {self._motion_mcp_valor(texto)}")

    def _motion_mcp_video_src(self, cliente, tentativas=8, intervalo=1.5):
        try:
            self._motion_mcp_abrir_painel_resultado(cliente)
        except Exception as exc:
            self._log(f"Motion: nao foi possivel abrir o painel ({exc}).")
        script = f"""
            () => {{
                const candidatos = [];
                const exato = document.querySelector(
                    {json.dumps(MOTION_RESULT_PANEL_VIDEO_SELECTOR)}
                );
                if (exato) candidatos.push(exato);
                document.querySelectorAll(
                    {json.dumps(MOTION_RESULT_PANEL_VIDEO_FALLBACK_SELECTOR)}
                ).forEach(v => candidatos.push(v));
                const antigo = document.querySelector(
                    {json.dumps(MOTION_OUTPUT_VIDEO_SELECTOR)}
                );
                if (antigo) candidatos.push(antigo);
                document.querySelectorAll(
                    '#graph-canvas-container video'
                ).forEach(v => candidatos.push(v));
                for (const video of candidatos) {{
                    const src = video.currentSrc || video.src ||
                        video.querySelector('source')?.src || '';
                    if (src) return src;
                }}
                return '';
            }}
        """
        for tentativa in range(1, tentativas + 1):
            texto = cliente.tool(
                "evaluate_script", {"function": script}, timeout=30
            )
            src = self._motion_mcp_valor(texto) or ""
            if src:
                return src
            if tentativa < tentativas:
                self._log(
                    f"Motion: video ainda nao apareceu "
                    f"(tentativa {tentativa}/{tentativas}), aguardando..."
                )
                time.sleep(intervalo)
        return ""

    def _motion_download_dir(self):
        return Path.home() / "Downloads"

    # ── Remocao de marca d'agua (tarja preta) + 4K, pos-download ───────────
    def _motion_remover_marca_dagua_ativo(self):
        return bool(self.config.get("motion_remover_marca_dagua", True))

    def _motion_ffmpeg_info_video(self, ffprobe, caminho_video):
        """Le largura/altura/rotacao do video via ffprobe (mesma logica
        do wmRunninghub.py)."""
        comando = [
            ffprobe, "-v", "error", "-select_streams", "v:0",
            "-show_entries",
            "stream=width,height:stream_tags=rotate:"
            "stream_side_data=rotation",
            "-of", "json", str(caminho_video),
        ]
        processo = subprocess.run(
            comando, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if processo.returncode != 0:
            raise RuntimeError(f"ffprobe falhou:\n{processo.stderr}")
        dados = json.loads(processo.stdout)
        streams = dados.get("streams", [])
        if not streams:
            raise RuntimeError("Nenhum stream de video encontrado.")
        stream = streams[0]
        largura = int(stream.get("width", 0))
        altura = int(stream.get("height", 0))
        rotacao = 0
        tags = stream.get("tags", {})
        if "rotate" in tags:
            try:
                rotacao = int(float(tags["rotate"]))
            except Exception:
                rotacao = 0
        for item in stream.get("side_data_list", []):
            if "rotation" in item:
                try:
                    rotacao = int(float(item["rotation"]))
                except Exception:
                    pass
        rotacao = rotacao % 360
        if rotacao in (90, 270):
            largura, altura = altura, largura
        return largura, altura

    def _motion_ffmpeg_resolucao_celular(self, largura, altura):
        # 4K vertical/horizontal compativel com celulares modernos e redes sociais.
        return self._mobile_target_size(largura, altura)

    def _motion_ffmpeg_montar_filtro(self, largura, altura):
        altura_tarja = f"ih*{MOTION_TARJA_ALTURA_PERCENTUAL}"
        filtros = [
            f"drawbox=x=0:y=0:w=iw:h={altura_tarja}:color=black:t=fill"
        ]
        # Redimensiona para 4K com bordas (sem cortar), compativel com celular.
        alvo_w, alvo_h = self._motion_ffmpeg_resolucao_celular(largura, altura)
        filtros.append(
            f"scale={alvo_w}:{alvo_h}:"
            "force_original_aspect_ratio=decrease"
        )
        filtros.append(
            f"pad={alvo_w}:{alvo_h}:(ow-iw)/2:(oh-ih)/2:color=black"
        )
        filtros.append("setsar=1")
        filtros.append("format=yuv420p")
        return ",".join(filtros)

    def _motion_ffmpeg_validar(self, ffprobe, caminho_video):
        if not caminho_video.exists() or caminho_video.stat().st_size <= 0:
            return False
        comando = [
            ffprobe, "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0",
            str(caminho_video),
        ]
        processo = subprocess.run(
            comando, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        return processo.returncode == 0 and "," in processo.stdout

    def _motion_remover_marca_dagua(self, caminho_video):
        """Aplica tarja preta no topo + exporta em 4K + garante audio
        AAC (compatibilidade com celular), substituindo o arquivo
        original somente se tudo correr bem. Levanta RuntimeError se
        ffmpeg/ffprobe nao estiverem disponiveis ou a conversao falhar;
        quem chama decide se trata isso como erro fatal ou so avisa."""
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if not ffmpeg or not ffprobe:
            raise RuntimeError(
                "ffmpeg/ffprobe nao encontrados no PATH; instale o "
                "FFmpeg para remover a marca d'agua."
            )
        largura, altura = self._motion_ffmpeg_info_video(ffprobe, caminho_video)
        filtro = self._motion_ffmpeg_montar_filtro(largura, altura)
        temp = caminho_video.with_name(
            f"{caminho_video.stem}.__TEMP_TARJA__{caminho_video.suffix}"
        )
        if temp.exists():
            temp.unlink()
        comando = [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(caminho_video),
            "-map", "0:v:0", "-map", "0:a?",
            "-vf", filtro,
            "-c:v", "libx264",
            "-profile:v", MOBILE_VIDEO_PROFILE,
            "-level", MOBILE_VIDEO_LEVEL,
            "-preset", MOTION_TARJA_PRESET,
            "-crf", MOTION_TARJA_CRF,
            "-pix_fmt", "yuv420p",
            "-c:a", MOTION_TARJA_AUDIO_CODEC,
            "-b:a", MOTION_TARJA_AUDIO_BITRATE,
            "-movflags", "+faststart",
            "-map_metadata", "-1",
            str(temp),
        ]
        processo = subprocess.run(
            comando, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if processo.returncode != 0:
            if temp.exists():
                try:
                    temp.unlink()
                except Exception:
                    pass
            detalhe = (processo.stderr or processo.stdout or "").strip()
            raise RuntimeError(f"ffmpeg falhou ao remover marca d'agua: {detalhe[-1200:]}")
        if not self._motion_ffmpeg_validar(ffprobe, temp):
            if temp.exists():
                try:
                    temp.unlink()
                except Exception:
                    pass
            raise RuntimeError(
                "Arquivo gerado ao remover marca d'agua ficou invalido; "
                "original mantido."
            )
        os.replace(temp, caminho_video)
        self._log(f"Motion: tarja preta aplicada e exportado em 4K -> {caminho_video}")

    def _motion_mcp_baixar(self, cliente, item):
        src = self._motion_mcp_video_src(cliente)
        if not src:
            raise RuntimeError("Video de saida nao encontrado.")
        nome_temp = f"swap_motion_{uuid.uuid4().hex}.mp4"
        cliente.tool("evaluate_script", {"function": f"""
            async () => {{
                const src = {json.dumps(src)};
                const response = await fetch(src);
                if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = {json.dumps(nome_temp)};
                document.body.appendChild(a);
                a.click();
                a.remove();
                setTimeout(() => URL.revokeObjectURL(url), 60000);
                return true;
            }}
        """}, timeout=120)
        downloads = self._motion_download_dir()
        arquivo = downloads / nome_temp
        parcial = downloads / f"{nome_temp}.crdownload"
        limite = time.monotonic() + 180
        while time.monotonic() < limite:
            if arquivo.exists() and not parcial.exists():
                destino = READY_DIR / item["modelo"] / (
                    item["video"].stem + ".mp4"
                )
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(arquivo), str(destino))
                self._log(f"Motion baixado: {destino}")
                if self._motion_remover_marca_dagua_ativo():
                    try:
                        self._log(
                            "Motion: removendo marca d'agua e "
                            "exportando em 4K..."
                        )
                        self._motion_remover_marca_dagua(destino)
                    except Exception as exc:
                        self._log(
                            f"Motion: falha ao remover marca d'agua "
                            f"({exc}). Video original mantido."
                        )
                return destino
            time.sleep(1)
        raise RuntimeError("Download do video Motion nao foi concluido.")

    def _motion_executar_acao_mcp(
            self, acao, itens, media_delay, generation_delay,
            usar_posicoes, perfil=None, rotulo=""):
        """Executa a acao conectando no Chrome do perfil indicado.

        Se a porta do perfil nao estiver respondendo, abre o Chrome
        sozinho (mesmo fluxo do botao 'Abrir selecionado') e aguarda o
        tempo configurado antes de conectar. O fechamento do Chrome
        (quando aberto automaticamente) e feito por quem chama esta
        funcao, depois que todos os perfis da fila terminarem.

        Retorna (resultados, erro, abriu_agora) em vez de finalizar a
        UI sozinho -- isso permite que _motion_executar_em_perfis
        dispare um worker destes por perfil/porta e todos rodem ao
        mesmo tempo (cada um fala com o seu Chrome via DevTools, sem
        usar o mouse nem depender de qual janela esta em primeiro
        plano)."""
        prefixo = f"{rotulo} " if rotulo else ""
        perfil = perfil or {"name": "padrao", "port": self._motion_porta_ativa()}
        porta = perfil.get("port") or self._motion_porta_ativa()
        abriu_agora = False
        if perfil.get("session"):
            try:
                abriu_agora = self._motion_garantir_perfil_aberto(
                    perfil, rotulo=rotulo
                )
            except Exception as exc:
                return [], f"Nao foi possivel abrir o Chrome: {exc}", False
        cliente = MotionMcpClient(log=lambda m: self._log(f"{prefixo}{m}"))
        resultados = []
        erro = None
        try:
            cliente.start(porta=porta)
            self._motion_mcp_selecionar_runninghub(cliente)
            if acao == "upload":
                if usar_posicoes:
                    self._motion_tela_enviar_midias(itens[0])
                else:
                    self._motion_mcp_enviar_midias_v2(cliente, itens[0])
                resultados.append("Foto e video enviados.")
            elif acao == "run":
                if usar_posicoes:
                    self._motion_tela_run()
                else:
                    self._motion_mcp_run(cliente)
                resultados.append("RUN clicado.")
            elif acao == "download":
                destino = self._motion_mcp_baixar(cliente, itens[0])
                resultados.append(f"Baixado em {destino}")
            elif acao == "all":
                for indice, item in enumerate(itens, 1):
                    self._log(
                        f"{prefixo}Motion {indice}/{len(itens)}: "
                        f"{item['pasta'].name}"
                    )
                    self._motion_pressionar_esc_repetido(
                        vezes=5, intervalo=3.0, rotulo=rotulo,
                        cliente=cliente, usar_posicoes=usar_posicoes
                    )
                    if usar_posicoes:
                        self._motion_tela_enviar_midias(item)
                    else:
                        self._motion_mcp_enviar_midias_v2(cliente, item)
                    self._log(
                        f"{prefixo}Aguardando {media_delay:.1f}s antes "
                        "do RUN..."
                    )
                    time.sleep(media_delay)
                    if usar_posicoes:
                        self._motion_tela_run()
                    else:
                        self._motion_mcp_run(cliente)
                    self._log(
                        f"{prefixo}Aguardando {generation_delay / 60:g} "
                        "min pelo video..."
                    )
                    time.sleep(generation_delay)
                    destino = self._motion_mcp_baixar(cliente, item)
                    resultados.append(str(destino))
        except Exception as exc:
            erro = str(exc)
            self._log(f"{prefixo}Motion ERRO: {erro}")
        finally:
            cliente.close()
        return resultados, erro, abriu_agora

    def _motion_agrupar(self, lista, tamanho):
        """Quebra 'lista' em pedacos de no maximo 'tamanho' itens,
        na ordem original (ex.: [1,2,3,4,5,6], 4 -> [[1,2,3,4],[5,6]])."""
        if tamanho <= 0:
            return [list(lista)]
        return [
            lista[i:i + tamanho]
            for i in range(0, len(lista), tamanho)
        ]

    def _motion_executar_em_perfis(
            self, perfis, acao, itens, media_delay, generation_delay,
            usar_posicoes):
        """Processa a fila em RODADAS, alternando entre os perfis
        ativos e respeitando o limite de Chromes simultaneos.

        Exemplo (8 perfis ativos A..H, limite=4, 12 videos):
          Rodada 1: video 1->A, video 2->B, video 3->C, video 4->D
          Rodada 2: video 5->E, video 6->F, video 7->G, video 8->H
          Rodada 3: video 9->A, video 10->B, video 11->C, video 12->D

        Dentro de cada rodada, os perfis do grupo trabalham em
        paralelo (uma thread por perfil, cada uma com sua propria
        ponte DevTools/Chrome). O codigo so avanca para a proxima
        rodada depois que todos os Chromes da rodada atual terminam
        e sao fechados -- assim nunca ha mais Chromes abertos do que
        o limite configurado."""
        if acao != "all" or len(perfis) <= 1:
            resultados, erro, _ = self._motion_executar_acao_mcp(
                acao, itens, media_delay, generation_delay,
                usar_posicoes, perfil=(perfis[0] if perfis else None)
            )
            self.after(
                0,
                lambda: self._motion_finalizar_acao(acao, resultados, erro)
            )
            return

        max_paralelo = min(self._motion_max_paralelo(), len(perfis)) or 1
        grupos_perfis = self._motion_agrupar(perfis, max_paralelo)

        # Numero de rodadas = suficiente para distribuir todos os itens
        # percorrendo os grupos de perfis em rotacao (cada rodada usa o
        # PROXIMO grupo de perfis, com o MESMO tamanho dele -- nunca um
        # tamanho fixo, senao perfis incompletos no ultimo grupo fariam
        # itens sobrarem e serem perdidos).
        grupos_itens = []
        cursor = 0
        indice_grupo = 0
        while cursor < len(itens):
            tamanho_grupo = len(grupos_perfis[indice_grupo % len(grupos_perfis)])
            grupos_itens.append(itens[cursor:cursor + tamanho_grupo])
            cursor += tamanho_grupo
            indice_grupo += 1

        self._log(
            f"Motion: {len(itens)} video(s), {len(perfis)} perfil(is) "
            f"ativo(s) em rotacao, ate {max_paralelo} Chrome(s) "
            f"simultaneo(s) -> {len(grupos_itens)} rodada(s)."
        )

        agregados = {"resultados": [], "erros": []}

        def rodar_rodada(indice_rodada):
            if indice_rodada >= len(grupos_itens):
                erro_final = (
                    "\n".join(agregados["erros"])
                    if agregados["erros"] else None
                )
                self.after(
                    0,
                    lambda: self._motion_finalizar_acao(
                        acao, agregados["resultados"], erro_final
                    )
                )
                return

            itens_rodada = grupos_itens[indice_rodada]
            grupo_perfis = grupos_perfis[indice_rodada % len(grupos_perfis)]
            duplas = list(zip(grupo_perfis, itens_rodada))
            total_dupla = len(duplas)

            self._log(
                f"Motion: rodada {indice_rodada + 1}/{len(grupos_itens)} "
                f"- perfis: {', '.join(p['name'] for p, _ in duplas)}"
            )

            lock = threading.Lock()
            restantes = [total_dupla]
            abriu_algum_rodada = [False]

            def trabalhar(perfil, item):
                rotulo = f"[{perfil.get('name', '?')}]"
                resultados, erro, abriu_agora = self._motion_executar_acao_mcp(
                    acao, [item], media_delay, generation_delay,
                    usar_posicoes, perfil=perfil, rotulo=rotulo
                )
                with lock:
                    if erro:
                        agregados["erros"].append(f"{rotulo} {erro}".strip())
                    agregados["resultados"].extend(
                        f"{rotulo} {r}".strip() for r in resultados
                    )
                    if abriu_agora:
                        abriu_algum_rodada[0] = True
                    restantes[0] -= 1
                    if restantes[0] == 0:
                        if abriu_algum_rodada[0]:
                            self._log(
                                f"Motion: fechando Chrome(s) da rodada "
                                f"{indice_rodada + 1}..."
                            )
                            self._motion_fechar_chrome()
                        rodar_rodada(indice_rodada + 1)

            for perfil, item in duplas:
                threading.Thread(
                    target=trabalhar, args=(perfil, item), daemon=True
                ).start()

        threading.Thread(
            target=lambda: rodar_rodada(0), daemon=True
        ).start()

    async def _motion_obter_pagina_async(self, context):
        for page in reversed(context.pages):
            try:
                if page.is_closed():
                    continue
                if await page.locator("#appVue").count():
                    await page.bring_to_front()
                    return page
            except Exception:
                continue
        raise RuntimeError(
            "Pagina Motion Control nao encontrada. Abra-a no Chrome de debugging."
        )

    async def _motion_conectar_async(self, playwright, porta):
        try:
            browser = await playwright.chromium.connect_over_cdp(
                f"http://localhost:{porta}"
            )
        except Exception as exc:
            raise RuntimeError(
                f"Nao foi possivel conectar ao Chrome na porta {porta}."
            ) from exc
        if not browser.contexts:
            raise RuntimeError("Chrome conectado, mas sem contexto aberto.")
        context = browser.contexts[0]
        page = await self._motion_obter_pagina_async(context)
        return browser, context, page

    async def _motion_detalhar_inputs_async(self, page):
        detalhes = []
        indice_global = 0
        for frame in page.frames:
            inputs = frame.locator('input[type="file"]')
            try:
                total = await inputs.count()
            except Exception:
                continue
            for indice in range(total):
                campo = inputs.nth(indice)
                try:
                    accept = (
                        await campo.get_attribute("accept") or ""
                    ).lower()
                    texto = await campo.evaluate("""
                        el => {
                            let node = el;
                            let parts = [];
                            for (let i = 0; i < 5 && node; i++, node = node.parentElement) {
                                parts.push(node.innerText || node.getAttribute('title') || '');
                            }
                            return parts.join(' ').slice(0, 500);
                        }
                    """)
                    detalhes.append({
                        "indice": indice_global,
                        "campo": campo,
                        "accept": accept,
                        "texto": (texto or "").lower(),
                    })
                    indice_global += 1
                except Exception:
                    continue
        return detalhes

    def _motion_escolher_input(self, detalhes, tipo, usados):
        palavra = "video" if tipo == "video" else "image"
        termos = ("video", "filme") if tipo == "video" else (
            "image", "imagem", "foto"
        )
        melhor = None
        melhor_pontos = -10000
        for detalhe in detalhes:
            if detalhe["indice"] in usados:
                continue
            accept = detalhe["accept"]
            texto = detalhe["texto"]
            pontos = 0
            if palavra in accept or f"{palavra}/*" in accept:
                pontos += 100
            if tipo == "video" and "image" in accept:
                pontos -= 100
            if tipo == "image" and "video" in accept:
                pontos -= 100
            if any(termo in texto for termo in termos):
                pontos += 25
            if not accept:
                pontos += 2
            if pontos > melhor_pontos:
                melhor = detalhe
                melhor_pontos = pontos
        return melhor

    async def _motion_enviar_midias_async(self, page, item):
        detalhes = await self._motion_detalhar_inputs_async(page)
        if len(detalhes) < 2:
            self._log(
                f"Motion: apenas {len(detalhes)} input(s) de arquivo encontrado(s); "
                "continuando mesmo assim."
            )
            if not detalhes:
                return
        usados = set()
        video_input = self._motion_escolher_input(detalhes, "video", usados)
        if not video_input:
            raise RuntimeError("Campo de upload do video nao encontrado.")
        usados.add(video_input["indice"])
        image_input = self._motion_escolher_input(detalhes, "image", usados)
        if not image_input:
            raise RuntimeError("Campo de upload da foto nao encontrado.")

        self._log(
            f"Motion video -> input {video_input['indice']} "
            f"(accept='{video_input['accept'] or 'generico'}')"
        )
        await video_input["campo"].set_input_files(str(item["video"]))
        await asyncio.sleep(0.7)
        self._log(
            f"Motion foto -> input {image_input['indice']} "
            f"(accept='{image_input['accept'] or 'generico'}')"
        )
        await image_input["campo"].set_input_files(str(item["imagem"]))
        await asyncio.sleep(1)

    async def _motion_clicar_run_async(self, page):
        botao = page.locator(MOTION_RUN_SELECTOR).first
        try:
            await botao.wait_for(state="visible", timeout=15000)
            await botao.click()
        except Exception:
            fallback = page.get_by_role(
                "button", name="Run", exact=True
            ).first
            await fallback.wait_for(state="visible", timeout=10000)
            await fallback.click()
        self._log("Motion: RUN clicado.")

    async def _motion_abrir_painel_resultado_async(self, page):
        """Clica no botao que abre o painel de resultado (hide-btn),
        revelando o video gerado. Se nao existir (painel ja aberto),
        ignora silenciosamente."""
        try:
            botao = page.locator(MOTION_RESULT_HIDE_BTN_SELECTOR).first
            if await botao.count() > 0:
                await botao.click(timeout=5000)
                self._log("Motion: painel de resultado aberto.")
        except Exception:
            pass

    async def _motion_obter_video_src_async(
            self, page, timeout_ms=30000, diferente_de=None):
        await self._motion_abrir_painel_resultado_async(page)
        seletores = [
            MOTION_RESULT_PANEL_VIDEO_SELECTOR,
            MOTION_OUTPUT_VIDEO_SELECTOR,
            "#graph-canvas-container video",
        ]
        limite = time.monotonic() + (timeout_ms / 1000)
        while time.monotonic() < limite:
            for seletor in seletores:
                videos = page.locator(seletor)
                quantidade = await videos.count()
                for indice in range(quantidade - 1, -1, -1):
                    video = videos.nth(indice)
                    try:
                        src = await video.evaluate(
                            "el => el.currentSrc || el.src || "
                            "(el.querySelector('source') || {}).src || ''"
                        )
                        if src and (not diferente_de or src != diferente_de):
                            return src
                    except Exception:
                        continue
            await asyncio.sleep(1)
        raise RuntimeError("Video gerado nao apareceu no seletor de saida.")

    async def _motion_salvar_src_async(self, page, src, destino):
        destino.parent.mkdir(parents=True, exist_ok=True)
        if src.startswith("data:"):
            cabecalho, dados = src.split(",", 1)
            conteudo = (
                base64.b64decode(dados)
                if ";base64" in cabecalho
                else dados.encode("utf-8")
            )
            destino.write_bytes(conteudo)
            return
        if src.startswith("http://") or src.startswith("https://") or src.startswith("/"):
            url = urljoin(page.url, src)
            resposta = await page.context.request.get(url)
            if resposta.status != 200:
                raise RuntimeError(
                    f"Download do video retornou HTTP {resposta.status}."
                )
            destino.write_bytes(await resposta.body())
            return

        try:
            async with page.expect_download(timeout=15000) as info:
                await page.evaluate("""
                    src => {
                        const a = document.createElement('a');
                        a.href = src;
                        a.download = 'motion.mp4';
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                    }
                """, src)
            download = await info.value
            await download.save_as(str(destino))
            return
        except Exception:
            pass

        dados_b64 = await page.evaluate("""
            async src => {
                const response = await fetch(src);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const bytes = new Uint8Array(await response.arrayBuffer());
                let binary = '';
                const chunk = 0x8000;
                for (let i = 0; i < bytes.length; i += chunk) {
                    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
                }
                return btoa(binary);
            }
        """, src)
        destino.write_bytes(base64.b64decode(dados_b64))

    async def _motion_baixar_video_async(
            self, page, item, src_anterior=None):
        try:
            src = await self._motion_obter_video_src_async(
                page, timeout_ms=45000, diferente_de=src_anterior
            )
        except RuntimeError:
            if not src_anterior:
                raise
            self._log(
                "Motion: a URL do video nao mudou; baixando a saida atual."
            )
            src = await self._motion_obter_video_src_async(
                page, timeout_ms=5000
            )
        destino_dir = READY_DIR / item["modelo"]
        destino = destino_dir / f"{item['video'].stem}.mp4"
        await self._motion_salvar_src_async(page, src, destino)
        self._log(f"Motion baixado: {destino}")
        if self._motion_remover_marca_dagua_ativo():
            try:
                self._log(
                    "Motion: removendo marca d'agua e exportando em 4K..."
                )
                self._motion_remover_marca_dagua(destino)
            except Exception as exc:
                self._log(
                    f"Motion: falha ao remover marca d'agua ({exc}). "
                    "Video original mantido."
                )
        return destino

    async def _motion_executar_acao_async(
            self, acao, itens, media_delay, generation_delay, porta):
        resultados = []
        erro = None
        try:
            if not PLAYWRIGHT_AVAILABLE:
                raise RuntimeError("Playwright nao esta instalado.")
            async with async_playwright() as playwright:
                _, _, page = await self._motion_conectar_async(
                    playwright, porta
                )
                if acao == "upload":
                    await self._motion_enviar_midias_async(page, itens[0])
                    resultados.append("Foto e video enviados.")
                elif acao == "run":
                    await self._motion_clicar_run_async(page)
                    resultados.append("RUN clicado.")
                elif acao == "download":
                    destino = await self._motion_baixar_video_async(
                        page, itens[0]
                    )
                    resultados.append(f"Baixado em {destino}")
                elif acao == "all":
                    for indice, item in enumerate(itens, 1):
                        self._log(
                            f"Motion {indice}/{len(itens)}: {item['pasta'].name}"
                        )
                        src_anterior = None
                        try:
                            src_anterior = await self._motion_obter_video_src_async(
                                page, timeout_ms=1000
                            )
                        except Exception:
                            pass
                        await self._motion_enviar_midias_async(page, item)
                        self._log(
                            f"Aguardando {media_delay:.1f}s antes do RUN..."
                        )
                        await asyncio.sleep(media_delay)
                        await self._motion_clicar_run_async(page)
                        self._log(
                            f"Aguardando {generation_delay / 60:g} min "
                            "pelo video..."
                        )
                        await asyncio.sleep(generation_delay)
                        destino = await self._motion_baixar_video_async(
                            page, item, src_anterior
                        )
                        resultados.append(str(destino))
        except Exception as exc:
            erro = str(exc)
            self._log(f"Motion ERRO: {erro}")
        self.after(
            0, lambda: self._motion_finalizar_acao(acao, resultados, erro)
        )

    def _motion_finalizar_acao(self, acao, resultados, erro):
        self._motion_busy = False
        self.deiconify()
        self.lift()
        for botao in self._motion_buttons:
            botao.state(["!disabled"])
        if erro:
            self._motion_status_label.configure(text=f"Erro: {erro}")
            resumo_ok = "\n".join(resultados) if resultados else ""
            texto = (
                f"{erro}\n\nConcluido com sucesso:\n{resumo_ok}"
                if resumo_ok else erro
            )
            messagebox.showerror("Motion", texto)
        else:
            resumo = "\n".join(resultados) or "Operacao concluida."
            self._motion_status_label.configure(text=resumo)
            messagebox.showinfo("Motion", resumo)
        self._motion_atualizar_fila()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB CONFIGURAÇÃO — sub-aba Modelos + Seletores
    # ══════════════════════════════════════════════════════════════════════════
    def _build_tab_configuracao(self):
        C = self.colors
        tab = tk.Frame(self.notebook, bg=C["BG"])
        self.notebook.add(tab, text="  Configuração  ")

        sub_nb = ttk.Notebook(tab)
        sub_nb.pack(fill="both", expand=True)

        # ── Sub-aba Modelos ───────────────────────────────────────────────────
        mod_frame = tk.Frame(sub_nb, bg=C["BG"])
        sub_nb.add(mod_frame, text="  Modelos  ")

        left = tk.Frame(mod_frame, bg=C["BG2"], width=220)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        right = tk.Frame(mod_frame, bg=C["BG"])
        right.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="MODELOS", bg=C["BG2"], fg=C["FG2"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(14, 4))
        lf = tk.Frame(left, bg=C["BG2"])
        lf.pack(fill="both", expand=True, padx=8)
        sb = ttk.Scrollbar(lf, style="Vertical.TScrollbar")
        sb.pack(side="right", fill="y")
        self.modelo_listbox = tk.Listbox(lf, bg=C["BG3"], fg=C["FG"],
            selectbackground=C["ACC"], selectforeground=C["FG"],
            font=("Segoe UI", 11), relief="flat", borderwidth=0,
            highlightthickness=0, yscrollcommand=sb.set,
            activestyle="none", cursor="hand2")
        self.modelo_listbox.pack(fill="both", expand=True)
        sb.config(command=self.modelo_listbox.yview)
        self.modelo_listbox.bind("<<ListboxSelect>>", self._on_modelo_select)
        btns = tk.Frame(left, bg=C["BG2"])
        btns.pack(fill="x", padx=8, pady=8)
        ttk.Button(btns, text="+ Novo", style="Accent.TButton",
                   command=self._novo_modelo).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(btns, text="Excluir",
                   command=self._excluir_modelo).pack(side="left", expand=True, fill="x")
        self.form_frame = tk.Frame(right, bg=C["BG"])
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=16)
        self._build_form_vazio()
        self._reload_lista_modelos()

        # ── Sub-aba Seletores ─────────────────────────────────────────────────
        sel_frame = tk.Frame(sub_nb, bg=C["BG"])
        sub_nb.add(sel_frame, text="  Seletores  ")
        self._build_seletores_content(sel_frame)

    def _build_tab_seletores(self):
        """Stub — seletores agora ficam em Configuração > Seletores."""
        pass

    def _build_seletores_content(self, frame):
        """Conteúdo dos seletores CSS, agora embutido na aba Configuração."""
        C = self.colors
        # ── Cabeçalho ────────────────────────────────────────────────────────
        hdr = tk.Frame(frame, bg=C["BG"])
        hdr.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(hdr, text="SELETORES CSS", bg=C["BG"], fg=C["FG2"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        ttk.Button(hdr, text="Restaurar padrões",
                   command=self._seletores_restaurar_padroes).pack(side="right")

        tk.Label(
            frame,
            text=(
                "Modo estrito: o programa usa somente os seletores configurados.\n"
                "Se algum seletor falhar, ele para e mostra erro — sem fallback.\n"
                "1. Capture/salve o botão Uploads\n"
                "2. Faça o upload das 3 imagens no site normalmente\n"
                "3. Capture o elemento que realmente seleciona cada imagem: 3ª → 2ª → 1ª"
            ),
            bg=C["BG"], fg=C["FG2"], font=("Segoe UI", 8),
            justify="left", anchor="w"
        ).pack(fill="x", padx=16, pady=(0, 12))

        # ── Bloco: botão Uploads (barra lateral) ─────────────────────────────
        self._sel_bloco_uploads_btn = self._build_seletor_bloco(
            frame,
            chave="uploads_btn",
            label="Botão 'Uploads' (barra lateral)",
            padrao="",
        )

        # ── Bloco: 3 imagens em sequência ────────────────────────────────────
        bloco_imgs = tk.Frame(frame, bg=C["BG2"])
        bloco_imgs.pack(fill="x", padx=16, pady=(0, 10), ipady=8, ipadx=8)

        tk.Label(bloco_imgs, text="Imagens dos uploads (3ª → 2ª → 1ª)",
                 bg=C["BG2"], fg=C["ACCFG"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=8, pady=(6, 4))

        # Status geral das 3 imagens
        sels = self.config.get("seletores", {})
        todas_salvas = all(sels.get(f"upload_img{i}") for i in [1, 2, 3])
        status_txt = "✓ 3 seletores salvos (opcional)" if todas_salvas else "· automático — clica nas 3 últimas imagens enviadas"
        status_cor = C["ACCFG"] if todas_salvas else C["FG2"]
        self._sel_imgs_status = tk.Label(
            bloco_imgs, text=status_txt, bg=C["BG2"], fg=status_cor,
            font=("Segoe UI", 8)
        )
        self._sel_imgs_status.pack(anchor="w", padx=8, pady=(0, 4))

        # Mostra os 3 seletores atuais (somente leitura resumido)
        self._sel_imgs_entries = {}
        for i in [3, 2, 1]:
            chave = f"upload_img{i}"
            linha = tk.Frame(bloco_imgs, bg=C["BG2"])
            linha.pack(fill="x", padx=8, pady=(0, 2))
            tk.Label(linha, text=f"  {i}ª imagem:", bg=C["BG2"], fg=C["FG2"],
                     font=("Consolas", 8), width=12, anchor="w").pack(side="left")
            entry = tk.Text(linha, height=1, bg=C["BG3"], fg=C["FG"],
                            font=("Consolas", 7), relief="flat", wrap="none",
                            insertbackground=C["ACC"])
            entry.insert("1.0", sels.get(chave, "— não definido —"))
            entry.pack(side="left", fill="x", expand=True)
            self._sel_imgs_entries[chave] = entry

        # Botões
        btn_frame = tk.Frame(bloco_imgs, bg=C["BG2"])
        btn_frame.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Button(
            btn_frame, text="⦿  Capturar 3 imagens (clique sequencial no Chrome)",
            command=self._seletores_capturar_3_imagens
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_frame, text="Limpar imagens",
            command=self._seletores_limpar_imagens
        ).pack(side="left")

        # ── Bloco: botão voltar à galeria principal ───────────────────────────
        self._sel_bloco_voltar_galeria = self._build_seletor_bloco(
            frame,
            chave="voltar_galeria",
            label="Botão 'Voltar à galeria' (após deletar uploads)",
            padrao="",
        )

    def _build_seletor_bloco(self, parent, chave, label, padrao):
        """Cria um bloco reutilizável com campo de texto + botões para um seletor."""
        C = self.colors
        bloco = tk.Frame(parent, bg=C["BG2"])
        bloco.pack(fill="x", padx=16, pady=(0, 10), ipady=8, ipadx=8)

        tk.Label(bloco, text=label, bg=C["BG2"], fg=C["ACCFG"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=8, pady=(6, 2))

        entry_frame = tk.Frame(bloco, bg=C["BG2"])
        entry_frame.pack(fill="x", padx=8, pady=(0, 4))

        entry = tk.Text(entry_frame, height=2, bg=C["BG3"], fg=C["FG"],
                        font=("Consolas", 8), relief="flat", wrap="char",
                        insertbackground=C["ACC"])
        entry.insert("1.0", self.config.get("seletores", {}).get(chave, padrao))
        entry.pack(side="left", fill="x", expand=True)

        valor_atual = self.config.get("seletores", {}).get(chave)
        if valor_atual:
            status_txt = "✓ configurado"
            status_cor = C["ACCFG"]
        elif padrao:
            status_txt = "· padrão"
            status_cor = C["FG2"]
        else:
            status_txt = "· não configurado"
            status_cor = C["FG2"]
        status_lbl = tk.Label(entry_frame, text=status_txt, bg=C["BG2"],
                              fg=status_cor, font=("Segoe UI", 8), width=12)
        status_lbl.pack(side="left", padx=(6, 0))

        if not hasattr(self, "_seletores_vars"):
            self._seletores_vars = {}
            self._seletores_status = {}
        self._seletores_vars[chave] = entry
        self._seletores_status[chave] = status_lbl

        btn_frame = tk.Frame(bloco, bg=C["BG2"])
        btn_frame.pack(fill="x", padx=8, pady=(0, 4))

        ttk.Button(
            btn_frame, text="Salvar texto",
            command=lambda c=chave: self._seletores_salvar_texto(c)
        ).pack(side="left", padx=(0, 4))
        ttk.Button(
            btn_frame, text="⦿ Capturar clicando no Chrome",
            command=lambda c=chave, p=padrao: self._seletores_capturar(c, p)
        ).pack(side="left", padx=(0, 4))
        ttk.Button(
            btn_frame, text="Resetar",
            command=lambda c=chave, p=padrao: self._seletores_resetar(c, p)
        ).pack(side="left")

        return bloco

    def _seletores_salvar_texto(self, chave):
        entry = self._seletores_vars[chave]
        valor = entry.get("1.0", "end").strip()
        if not valor:
            messagebox.showwarning("Seletores", "O seletor não pode ser vazio.")
            return
        self.config.setdefault("seletores", {})[chave] = valor
        save_json(CONFIG_FILE, self.config)
        self._seletores_status[chave].configure(text="✓ configurado", fg=self.colors["ACCFG"])
        self._log(f"Seletor '{chave}' salvo manualmente.")

    def _seletores_resetar(self, chave, padrao):
        self.config.get("seletores", {}).pop(chave, None)
        save_json(CONFIG_FILE, self.config)
        entry = self._seletores_vars[chave]
        entry.delete("1.0", "end")
        entry.insert("1.0", padrao)
        status_txt = "· padrão" if padrao else "· não configurado"
        self._seletores_status[chave].configure(text=status_txt, fg=self.colors["FG2"])
        self._log(f"Seletor '{chave}' resetado.")

    def _seletores_restaurar_padroes(self):
        if not messagebox.askyesno("Restaurar padrões",
                "Tem certeza? Todos os seletores serão apagados."):
            return
        self.config.pop("seletores", None)
        save_json(CONFIG_FILE, self.config)
        # Recarrega os campos de texto
        if hasattr(self, "_seletores_vars"):
            for chave, entry in self._seletores_vars.items():
                entry.delete("1.0", "end")
                entry.insert("1.0", "")
                if chave in self._seletores_status:
                    self._seletores_status[chave].configure(
                        text="· não configurado", fg=self.colors["FG2"])
        self._seletores_limpar_imagens(confirmar=False)
        self._log("Todos os seletores restaurados ao padrão.")

    def _seletores_limpar_imagens(self, confirmar=True):
        if confirmar and not messagebox.askyesno(
                "Limpar imagens", "Remover os 3 seletores de imagens salvos?"):
            return
        sels = self.config.get("seletores", {})
        for i in [1, 2, 3]:
            sels.pop(f"upload_img{i}", None)
        save_json(CONFIG_FILE, self.config)
        for i in [1, 2, 3]:
            chave = f"upload_img{i}"
            if chave in self._sel_imgs_entries:
                self._sel_imgs_entries[chave].delete("1.0", "end")
                self._sel_imgs_entries[chave].insert("1.0", "— não definido —")
        self._sel_imgs_status.configure(
            text="· automático — clica nas 3 últimas imagens enviadas", fg=self.colors["FG2"])
        self._log("Seletores das 3 imagens removidos. O fluxo usará seleção automática pelas últimas 3 imagens.")

    def _seletores_capturar(self, chave, padrao):
        """Captura um único seletor clicando no Chrome."""
        if not PLAYWRIGHT_AVAILABLE:
            messagebox.showerror("Seletores", "Playwright não instalado.")
            return
        porta = self._seletores_porta_ativa()
        if not porta:
            return

        self._seletores_status[chave].configure(text="⦿ aguardando...", fg=self.colors["WARN"])
        messagebox.showinfo("Capturar seletor",
            "Clique no elemento correto no Chrome agora.\n"
            f"(porta {porta})")

        def _thread():
            resultado = self._seletores_run_captura(porta, 1)
            self.after(0, lambda: self._seletores_finalizar_unico(chave, padrao, resultado))
        threading.Thread(target=_thread, daemon=True).start()

    def _seletores_capturar_3_imagens(self):
        """Captura os seletores das 3 imagens em sequência (3ª → 2ª → 1ª)."""
        if not PLAYWRIGHT_AVAILABLE:
            messagebox.showerror("Seletores", "Playwright não instalado.")
            return
        porta = self._seletores_porta_ativa()
        if not porta:
            return

        messagebox.showinfo(
            "Capturar 3 imagens",
            "Você vai clicar nas imagens em sequência:\n\n"
            "  1º clique → 3ª imagem\n"
            "  2º clique → 2ª imagem\n"
            "  3º clique → 1ª imagem\n\n"
            "Clique OK e vá para o Chrome."
        )

        self._sel_imgs_status.configure(text="⦿ aguardando 3ª imagem...", fg=self.colors["WARN"])

        def _thread():
            resultado = self._seletores_run_captura(porta, 3)
            self.after(0, lambda: self._seletores_finalizar_imagens(resultado))
        threading.Thread(target=_thread, daemon=True).start()

    def _seletores_porta_ativa(self):
        """Retorna a porta do primeiro perfil Flow ativo, ou None se não encontrar."""
        perfis = [p for p in self.config.get("flow_profiles", []) if p.get("active", True)]
        if not perfis:
            messagebox.showerror("Seletores",
                "Nenhum perfil Flow ativo.\nConfigure um perfil na aba Flow.")
            return None
        porta = perfis[0].get("port", "9222")
        if not self._flow_porta_respondendo(porta):
            messagebox.showerror("Seletores",
                f"Chrome não responde na porta {porta}.\nAbra o Chrome com o Flow primeiro.")
            return None
        return porta

    def _seletores_run_captura(self, porta, quantidade):
        """
        Roda no thread: injeta overlay no Chrome, captura N cliques e
        retorna lista de seletores capturados (ou string 'ERRO: ...').
        """
        import asyncio as _asyncio

        async def _run():
            try:
                async with async_playwright() as pw:
                    browser = await pw.chromium.connect_over_cdp(
                        f"http://localhost:{porta}"
                    )
                    context = browser.contexts[0]
                    page = None
                    # Preferir a aba Flow ativa/mais recente. Antes usava pages[0],
                    # o que podia capturar seletor de outra aba quando havia várias abertas.
                    for p in reversed(context.pages):
                        try:
                            if (not p.is_closed()) and "labs.google/fx/" in p.url and "/flow/" in p.url:
                                page = p
                                break
                        except Exception:
                            continue
                    if page is None:
                        page = context.pages[0]
                    try:
                        await page.bring_to_front()
                    except Exception:
                        pass

                    seletores = await page.evaluate(
                        """
                        (qtd) => new Promise((resolve) => {
                            const capturados = [];

                            const overlay = document.createElement('div');
                            overlay.style.cssText = [
                                'position:fixed','top:0','left:0',
                                'width:100vw','height:100vh',
                                'z-index:2147483647','cursor:crosshair',
                                'background:rgba(232,200,122,0.06)'
                            ].join(';');

                            const highlight = document.createElement('div');
                            highlight.style.cssText = [
                                'position:fixed','pointer-events:none',
                                'z-index:2147483646',
                                'border:2px solid #3c096c',
                                'background:rgba(232,200,122,0.15)',
                                'transition:all 0.08s'
                            ].join(';');

                            const badge = document.createElement('div');
                            badge.style.cssText = [
                                'position:fixed','top:12px','left:50%',
                                'transform:translateX(-50%)',
                                'z-index:2147483648',
                                'background:#050505','color:#c084fc',
                                'font:bold 14px monospace',
                                'padding:6px 18px','border-radius:6px',
                                'border:1px solid #3c096c',
                                'pointer-events:none'
                            ].join(';');

                            document.body.appendChild(overlay);
                            document.body.appendChild(highlight);
                            document.body.appendChild(badge);

                            function buildSelector(el) {
                                // Estratégia principal: localizar a <img> mais próxima
                                // e usar o src do thumbnail — estável entre re-renders.
                                let img = (el.tagName === 'IMG') ? el : el.querySelector('img');
                                if (!img) {
                                    // Sobe até encontrar uma img no ancestral
                                    let cur = el.parentNode;
                                    while (cur && cur !== document.documentElement) {
                                        const found = cur.querySelector('img');
                                        if (found) { img = found; break; }
                                        cur = cur.parentNode;
                                    }
                                }
                                if (img) {
                                    const src = img.currentSrc || img.src || '';
                                    if (src && !src.startsWith('data:image/svg')) {
                                        // Retorna um marcador especial que o Python
                                        // reconhece como "clique pela src da img".
                                        return '__IMGSRC__' + src;
                                    }
                                }
                                // Último recurso: retorna posição visual (% da viewport)
                                // para ser independente do tamanho da janela.
                                const r = el.getBoundingClientRect();
                                const cx = (r.left + r.width / 2) / window.innerWidth;
                                const cy = (r.top + r.height / 2) / window.innerHeight;
                                return '__XYREL__' + cx.toFixed(4) + ',' + cy.toFixed(4);
                            }

                            const nomes = ['3ª imagem', '2ª imagem', '1ª imagem'];

                            function atualizarBadge() {
                                const faltam = qtd - capturados.length;
                                if (faltam <= 0) return;
                                const nome = nomes[capturados.length] || `clique ${capturados.length + 1}`;
                                badge.textContent = `Clique na ${nome} (${capturados.length + 1}/${qtd})`;
                            }
                            atualizarBadge();

                            overlay.addEventListener('mousemove', (e) => {
                                overlay.style.pointerEvents = 'none';
                                const real = document.elementFromPoint(e.clientX, e.clientY);
                                overlay.style.pointerEvents = '';
                                if (!real) return;
                                const r = real.getBoundingClientRect();
                                highlight.style.left   = r.left   + 'px';
                                highlight.style.top    = r.top    + 'px';
                                highlight.style.width  = r.width  + 'px';
                                highlight.style.height = r.height + 'px';
                            });

                            overlay.addEventListener('click', (e) => {
                                e.stopPropagation(); e.preventDefault();
                                overlay.style.pointerEvents = 'none';
                                const real = document.elementFromPoint(e.clientX, e.clientY);
                                overlay.style.pointerEvents = '';
                                capturados.push(buildSelector(real));
                                if (capturados.length >= qtd) {
                                    overlay.remove();
                                    highlight.remove();
                                    badge.remove();
                                    resolve(capturados);
                                } else {
                                    atualizarBadge();
                                    highlight.style.border = '2px solid #5a189a';
                                    setTimeout(() => {
                                        highlight.style.border = '2px solid #3c096c';
                                    }, 300);
                                }
                            });
                        })
                        """,
                        quantidade
                    )
                    return seletores
            except Exception as exc:
                return f"ERRO: {exc}"

        return _asyncio.run(_run())

    def _seletores_finalizar_unico(self, chave, padrao, resultado):
        if isinstance(resultado, list) and resultado:
            sel = resultado[0]
            self.config.setdefault("seletores", {})[chave] = sel
            save_json(CONFIG_FILE, self.config)
            if chave in self._seletores_vars:
                self._seletores_vars[chave].delete("1.0", "end")
                self._seletores_vars[chave].insert("1.0", sel)
            if chave in self._seletores_status:
                self._seletores_status[chave].configure(
                    text="✓ customizado", fg=self.colors["ACCFG"])
            self._log(f"Seletor '{chave}' capturado:\n    {sel}")
        else:
            if chave in self._seletores_status:
                self._seletores_status[chave].configure(text="✗ erro", fg=self.colors["ERR"])
            self._log(f"Seletor '{chave}': erro — {resultado}")
            messagebox.showerror("Erro na captura", str(resultado))

    def _seletores_finalizar_imagens(self, resultado):
        if isinstance(resultado, str) and resultado.startswith("ERRO:"):
            self._sel_imgs_status.configure(text="✗ erro na captura", fg=self.colors["ERR"])
            self._log(f"Captura das 3 imagens falhou: {resultado}")
            messagebox.showerror("Erro na captura", resultado)
            return

        if not isinstance(resultado, list) or len(resultado) < 3:
            self._sel_imgs_status.configure(text="✗ captura incompleta", fg=self.colors["ERR"])
            self._log(f"Captura incompleta: {resultado}")
            messagebox.showerror("Erro", "Não foram capturados os 3 seletores.")
            return

        # resultado[0] = 3ª, resultado[1] = 2ª, resultado[2] = 1ª
        mapa = {"upload_img3": resultado[0],
                "upload_img2": resultado[1],
                "upload_img1": resultado[2]}

        sels = self.config.setdefault("seletores", {})
        sels.update(mapa)
        save_json(CONFIG_FILE, self.config)

        for chave, sel in mapa.items():
            if chave in self._sel_imgs_entries:
                self._sel_imgs_entries[chave].delete("1.0", "end")
                self._sel_imgs_entries[chave].insert("1.0", sel)

        self._sel_imgs_status.configure(text="✓ 3 seletores salvos", fg=self.colors["ACCFG"])
        self._log("3 seletores de imagem capturados e salvos:")
        for chave, sel in mapa.items():
            self._log(f"    {chave}: {sel}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 7 — LOG
    # ══════════════════════════════════════════════════════════════════════════
    def _build_tab_log(self):
        C = self.colors
        frame = tk.Frame(self.notebook, bg=C["BG"])
        self.notebook.add(frame, text="  Log  ")

        header = tk.Frame(frame, bg=C["BG"])
        header.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(header, text="LOG DE OPERAÇÕES", bg=C["BG"], fg=C["FG2"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        ttk.Button(header, text="Limpar", command=self._limpar_log).pack(side="right")

        lf = tk.Frame(frame, bg=C["BG"])
        lf.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        sc = ttk.Scrollbar(lf, style="Vertical.TScrollbar"); sc.pack(side="right", fill="y")
        self.log_text = tk.Text(lf, bg=C["BG3"], fg=C["FG"],
            font=("Consolas", 9), relief="flat", borderwidth=0,
            wrap="word", yscrollcommand=sc.set, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        sc.config(command=self.log_text.yview)

        self._log(f"{APP_NAME} iniciado.")
        self._log(f"Base : {BASE_DIR}")
        self._log(f"Work : {WORK_DIR}")
        if not PIL_AVAILABLE:
            self._log("⚠ Pillow não instalado (pip install Pillow)")
        if not CV2_AVAILABLE:
            self._log("⚠ OpenCV não instalado (pip install opencv-python)")
        if not PLAYWRIGHT_AVAILABLE:
            self._log("⚠ Playwright não instalado (pip install playwright && playwright install chromium)")

    def _report_callback_exception(self, exc, val, tb):
        import traceback
        erro_txt = "".join(traceback.format_exception(exc, val, tb))
        try:
            self._log("❌ ERRO (callback):")
            self._log(erro_txt)
        except Exception:
            pass
        try:
            messagebox.showerror("Erro inesperado", f"{val}\n\nVer aba Log para detalhes.")
        except Exception:
            pass

    def _log(self, msg):
        def _do():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.after(0, _do)

    def _limpar_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MotionHubApp()
    app.mainloop()
