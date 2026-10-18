import os
import subprocess
import requests
import yt_dlp

# Puxa as chaves seguras do Telegram da nuvem
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(video_path, legenda_texto):
    """Envia o vídeo cortado direto para o Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    print(f"📤 Enviando {video_path} para o Telegram...")
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': legenda_texto,
            'parse_mode': 'Markdown'
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print("✅ Vídeo enviado com sucesso ao Telegram!")
        else:
            print(f"❌ Erro ao enviar no Telegram: {response.text}")

def executar_sistema():
    url_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    nicho = "Construção e Negócios"
    
    print("⏳ [1/3] Baixando o vídeo principal...")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'video_original.mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_video])
        
    print("✂️ [2/3] Processando e cortando o vídeo...")
    inicio = 30.0
    duracao = 50.0
    corte_output = "corte_monetizavel.mp4"
    
    # FFmpeg anti-copyright (espelhamento, zoom leve e ajuste de áudio)
    comando_ffmpeg = [
        'ffmpeg', '-y',
        '-ss', str(inicio),
        '-i', 'video_original.mp4',
        '-to', str(duracao),
        '-vf', 'hflip,scale=1.05*iw:-1,crop=iw/1.05:ih/1.05',
        '-filter:a', 'atempo=1.02',
        corte_output
    ]
    subprocess.run(comando_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("✍️ [3/3] Enviando ao Telegram...")
    mensagem_final = f"🚀 **CORTE ESTRATÉGICO PRONTO**\n\n📌 **Nicho:** {nicho}\n🎯 **Status:** Processado e Otimizado com Sucesso!"
    
    enviar_telegram(corte_output, mensagem_final)
    print("✅ Processo concluído com sucesso!")

if __name__ == "__main__":
    executar_sistema()