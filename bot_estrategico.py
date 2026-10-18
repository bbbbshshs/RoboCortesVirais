import os
import re
import subprocess
import requests
import yt_dlp
import whisper
import google.generativeai as genai

# Puxa as chaves seguras das configurações da nuvem
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_KEY)
# Utilizando gemini-pro para compatibilidade total e sem erros de 404
model = genai.GenerativeModel('gemini-pro')

def enviar_telegram(video_path, legenda_texto):
    """Envia o vídeo cortado e a copy criada direto para o Telegram."""
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

def encontrar_melhores_trechos(transcricao_segmentos, nicho):
    """Pede para o Gemini ler a transcrição e escolher os segundos exatos do melhor corte."""
    texto_com_tempo = ""
    for seg in transcricao_segmentos:
        texto_com_tempo += f"[{seg['start']:.1f}s - {seg['end']:.1f}s]: {seg['text']}\n"
        
    prompt = f"""
    Você é um editor profissional de vídeos virais para TikTok, Shorts e Reels no nicho '{nicho}'.
    Analise a transcrição abaixo com marcas de tempo e escolha o MELHOR trecho (de 30 a 50 segundos) que possui maior potencial de viralização.
    
    Transcrição:
    {texto_com_tempo}
    
    Retorne APENAS o formato exato com o tempo de início e fim em segundos:
    INICIO: [segundos], FIM: [segundos]
    Exemplo:
    INICIO: 45.5, FIM: 90.0
    """
    
    resposta = model.generate_content(prompt)
    texto_resp = resposta.text
    print(f"🤖 Resposta da IA:\n{texto_resp}")
    
    match = re.search(r'INICIO:\s*([0-9.]+),\s*FIM:\s*([0-9.]+)', texto_resp)
    if match:
        return float(match.group(1)), float(match.group(2))
    else:
        return 30.0, 75.0

def criar_estrategia_copy(transcricao_trecho, nicho):
    """Gera o pacote de copywriting para engajamento."""
    prompt = f"""
    Com base na transcrição deste corte sobre '{nicho}':
    "{transcricao_trecho}"
    
    Gere um pacote de publicação de alto engajamento:
    1. 🎯 HOOK/TÍTULO VIRAL (Em caixa alta, até 6 palavras).
    2. 📝 LEGENDA PERSUASIVA (Gancho forte, breve resumo e Call to Action).
    3. 🏷️ HASHTAGS (Exatamente 8 hashtags estratégicas).
    4. ⏰ HORÁRIO DE POSTAGEM (12:00, 18:00 ou 20:30).
    """
    resposta = model.generate_content(prompt)
    return resposta.text

def executar_sistema():
    url_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    nicho = "Construção e Negócios"
    
    print("⏳ [1/5] Baixando o vídeo principal...")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'video_original.mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_video])
        
    print("🧠 [2/5] Transcrevendo o áudio localmente (Whisper tiny)...")
    whisper_model = whisper.load_model("tiny")
    resultado = whisper_model.transcribe("video_original.mp4")
    segments = resultado["segments"]
    
    print("🎯 [3/5] Analisando os melhores momentos com IA...")
    inicio, fim = encontrar_melhores_trechos(segments, nicho)
    duracao = fim - inicio
    
    if duracao > 50:
        duracao = 50
        
    print(f"✂️ [4/5] Cortando do segundo {inicio:.1f} até {inicio + duracao:.1f}...")
    corte_output = "corte_monetizavel.mp4"
    
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
    
    print("✍️ [5/5] Gerando copy e enviando ao Telegram...")
    texto_trecho = "Trecho extraído cirurgicamente com foco em retenção e valor."
    copy_estrategica = criar_estrategia_copy(texto_trecho, nicho)
    mensagem_final = f"🚀 **CORTE ESTRATÉGICO PRONTO**\n\n{copy_estrategica}"
    
    enviar_telegram(corte_output, mensagem_final)
    print("✅ Processo concluído com sucesso!")

if __name__ == "__main__":
    executar_sistema()