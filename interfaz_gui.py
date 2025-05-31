import cv2
import pandas as pd
from datetime import datetime
from deepface import DeepFace
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Directorios
app_dir = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.join(app_dir, 'base_datos')
registro_path = os.path.join(app_dir, 'asistencia.csv')
fotos_path = os.path.join(app_dir, 'fotos_registro')
haar_path = os.path.join(app_dir, 'haarcascade_frontalface_default.xml')

personas_registradas = set()
y_true = []
y_pred = []

# Crear carpetas si no existen
os.makedirs(base_path, exist_ok=True)
os.makedirs(fotos_path, exist_ok=True)

# Crear archivo de registro si no existe
if not os.path.exists(registro_path):
    pd.DataFrame(columns=["Nombre", "Fecha", "Hora"]).to_csv(registro_path, index=False)

# Evaluar el modelo
def evaluar_modelo():
    if len(y_true) == len(y_pred) and y_true:
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        mensaje = f"Accuracy: {acc:.2f}\nPrecision: {prec:.2f}\nRecall: {rec:.2f}\nF1 Score: {f1:.2f}"
    else:
        mensaje = (
            "Las listas no coinciden o están vacías.\n\n"
            f"y_true ({len(y_true)}): {y_true}\n"
            f"y_pred ({len(y_pred)}): {y_pred}"
        )
    messagebox.showinfo("Evaluación del Modelo", mensaje)

# Procesar video
def procesar_video(label, lista, canvas, video_panel, ventana):
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(haar_path)

    def mostrar_frame():
        if not cap.isOpened():
            label.config(text="No se pudo abrir la cámara.")
            return

        ret, frame = cap.read()
        if not ret or frame is None:
            label.config(text="No se pudo leer de la cámara.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = face_cascade.detectMultiScale(gray, 1.3, 5)
        nombre = ""

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
                    y_pred.append(nombre)
                    lista.insert(tk.END, nombre)
                    label.config(text=f"Asistencia registrada: {nombre}")

                    try:
                        if frame is not None:
                            filename = os.path.join(fotos_path, f"{nombre}_{ahora.strftime('%Y%m%d_%H%M%S')}.jpg")
                            if not os.path.exists(fotos_path):
                                os.makedirs(fotos_path)
                            success = cv2.imwrite(filename, frame)
                            if not success:
                                raise IOError("cv2.imwrite() falló al guardar la imagen.")
                        else:
                            raise ValueError("El frame capturado es None.")
                    except Exception as e:
                        label.config(text=f"Error guardando imagen: {e}")

        except Exception as e:
            label.config(text=f"Error: {e}")

        for (x, y, w, h) in caras:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if nombre:
                cv2.putText(frame, nombre, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_panel.imgtk = imgtk
        video_panel.config(image=imgtk)

        video_panel.after(10, mostrar_frame)

    def detener_video():
        if cap.isOpened():
            cap.release()
        ventana.destroy()

    ventana.protocol("WM_DELETE_WINDOW", detener_video)
    mostrar_frame()

# Interfaz gráfica
def iniciar_app():
    ventana = tk.Tk()
    ventana.title("Sistema de Asistencia Facial")
    ventana.geometry("800x650")

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

    botones_frame = ttk.Frame(ventana)
    botones_frame.pack(pady=10)

    ttk.Button(
        botones_frame, text="Iniciar Reconocimiento",
        command=lambda: threading.Thread(
            target=procesar_video,
            args=(label_estado, lista_nombres, canvas, video_panel, ventana)
        ).start()
    ).pack(side="left", padx=5)

    ttk.Button(botones_frame, text="Evaluar Modelo", command=evaluar_modelo).pack(side="left", padx=5)
    ttk.Button(botones_frame, text="Salir", command=ventana.destroy).pack(side="left", padx=5)

    ventana.mainloop()

# Iniciar aplicación
if __name__ == "__main__":
    try:
        df_true = pd.read_csv(os.path.join(app_dir, "y_true.csv"))
        y_true.extend(df_true["nombre"].tolist())
    except Exception as e:
        print(f"Error al cargar y_true.csv: {e}")

    iniciar_app()
