import cv2
import pandas as pd
from datetime import datetime
from deepface import DeepFace
import os
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Rutas
base_path = 'base_datos'
registro_path = 'asistencia.csv'
personas_registradas = set()

if not os.path.exists(registro_path):
    pd.DataFrame(columns=["Nombre", "Fecha", "Hora"]).to_csv(registro_path, index=False)

# Función de procesamiento de video con reconocimiento facial
def procesar_video(label, lista, canvas, video_panel):
    cap = cv2.VideoCapture(0)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def loop():
        if not cap.isOpened():
            label.config(text="No se pudo abrir la cámara.")
            return

        ret, frame = cap.read()
        if not ret:
            label.config(text="No se pudo leer de la cámara.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = face_cascade.detectMultiScale(gray, 1.3, 5)

        try:
            result = DeepFace.find(img_path=frame, db_path=base_path, enforce_detection=False, model_name="ArcFace")
            nombre = ""
            if len(result) > 0 and not result[0].empty:
                nombre_archivo = os.path.basename(result[0].iloc[0]['identity'])
                nombre = os.path.splitext(nombre_archivo)[0]

                if nombre not in personas_registradas:
                    ahora = datetime.now()
                    df = pd.read_csv(registro_path)
                    df.loc[len(df.index)] = [nombre, ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")]
                    df.to_csv(registro_path, index=False)
                    personas_registradas.add(nombre)
                    label.after(0, lambda: label.config(text=f"Asistencia registrada: {nombre}"))
                    lista.after(0, lambda: lista.insert(tk.END, nombre))

            for (x, y, w, h) in caras:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if nombre:
                    cv2.putText(frame, nombre, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        except Exception as e:
            label.after(0, lambda: label.config(text=f"Error: {e}"))

        # Convertir imagen a formato compatible con Tkinter
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        video_panel.imgtk = imgtk
        video_panel.config(image=imgtk)

        canvas.after(10, loop)

    loop()

# GUI
def iniciar_app():
    ventana = tk.Tk()
    ventana.title("Sistema de Asistencia Facial")
    ventana.geometry("800x600")

    label_estado = ttk.Label(ventana, text="Esperando reconocimiento...", font=("Arial", 12))
    label_estado.pack(pady=5)

    canvas_frame = ttk.Frame(ventana)
    canvas_frame.pack()

    video_panel = tk.Label(canvas_frame)
    video_panel.pack()

    lista_frame = ttk.LabelFrame(ventana, text="Estudiantes Reconocidos")
    lista_frame.pack(pady=10, fill="both", expand=True)

    lista_nombres = tk.Listbox(lista_frame, height=8, font=("Courier", 12))
    lista_nombres.pack(padx=10, pady=5, fill="both", expand=True)

    canvas = tk.Canvas(ventana)
    canvas.pack_forget()

    boton_iniciar = ttk.Button(
        ventana,
        text="Iniciar Reconocimiento",
        command=lambda: threading.Thread(target=procesar_video, args=(label_estado, lista_nombres, canvas, video_panel)).start()
    )
    boton_iniciar.pack(pady=10)

    boton_salir = ttk.Button(ventana, text="Salir", command=ventana.destroy)
    boton_salir.pack(pady=5)

    ventana.mainloop()

if __name__ == "__main__":
    iniciar_app()
