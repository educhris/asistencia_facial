
import cv2
import pandas as pd
from datetime import datetime
from deepface import DeepFace
import os
import threading
import tkinter as tk
from tkinter import ttk

# Rutas
base_path = 'base_datos'
registro_path = 'asistencia.csv'
personas_registradas = set()

if not os.path.exists(registro_path):
    pd.DataFrame(columns=["Nombre", "Fecha", "Hora"]).to_csv(registro_path, index=False)

def procesar_video(label):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        try:
            result = DeepFace.find(img_path=frame, db_path=base_path, enforce_detection=False, model_name="ArcFace")
            if len(result) > 0 and not result[0].empty:
                nombre_archivo = os.path.basename(result[0].iloc[0]['identity'])
                nombre = os.path.splitext(nombre_archivo)[0]
                if nombre not in personas_registradas:
                    ahora = datetime.now()
                    df = pd.read_csv(registro_path)
                    df.loc[len(df.index)] = [nombre, ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")]
                    df.to_csv(registro_path, index=False)
                    personas_registradas.add(nombre)
                    label.config(text=f"Asistencia registrada: {nombre}")
        except Exception as e:
            label.config(text=f"Error: {e}")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def iniciar_app():
    ventana = tk.Tk()
    ventana.title("Sistema de Asistencia Facial")
    ventana.geometry("500x250")
    label_estado = ttk.Label(ventana, text="Esperando reconocimiento...", font=("Arial", 14))
    label_estado.pack(pady=20)
    boton_iniciar = ttk.Button(ventana, text="Iniciar", command=lambda: threading.Thread(target=procesar_video, args=(label_estado,)).start())
    boton_iniciar.pack(pady=10)
    boton_salir = ttk.Button(ventana, text="Salir", command=ventana.destroy)
    boton_salir.pack(pady=10)
    ventana.mainloop()

if __name__ == "__main__":
    iniciar_app()




