import speech_recognition as sr

def listen():
    mic = sr.Recognizer()
    
    with sr.Microphone() as source:
        mic.adjust_for_ambient_noise(source)
        
        audio = mic.listen(source)
        
        try:
            text = mic.recognize_google(audio, language="pt-BR")
            return text
        
        except Exception as e:
            print("Mensagem não entendida")