from PIL import Image, ImageDraw

# Crear un ícono simple con forma de cara y cámara
icon_size = (256, 256)
icon = Image.new('RGBA', icon_size, (255, 255, 255, 0))
draw = ImageDraw.Draw(icon)

# Cara (círculo)
draw.ellipse((56, 56, 200, 200), fill=(100, 149, 237, 255), outline=(0, 0, 0), width=4)

# Cámara (cuadro arriba)
draw.rectangle((90, 30, 170, 70), fill=(70, 70, 70, 255), outline=(0, 0, 0), width=3)

# Guardar como archivo .ico
icon_path = "C:\Users\chris\OneDrive\Documentos\UHE\Examen Final Tesis\asistencia facial/data/asistencia_icono.ico"
icon.save(icon_path, format="ICO")

icon_path
