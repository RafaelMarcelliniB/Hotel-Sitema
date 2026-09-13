# Build de la aplicación Windows

## 1. Compilar el frontend

Desde `hotel-venecia-frontend` instala las dependencias y genera el build de Vite:

```powershell
npm ci
npm run build
```

Vite crea `dist`. Cópialo a `frontend_build` en la raíz del repositorio:

```powershell
Remove-Item ..\frontend_build -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item dist ..\frontend_build -Recurse
```

El backend también acepta `frontend/build` como ruta alternativa. Si el proyecto cambia su carpeta de salida, revisa el TODO de `run_backend.py`.

## 2. Entorno Python y PyInstaller

Desde la raíz del repositorio:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pyinstaller --name run_backend --noconfirm --clean --onefile `
  --add-data "frontend_build;frontend_build" run_backend.py
pyinstaller --name main --noconfirm --clean --onefile --windowed main.py
```

Los ejecutables quedan en `dist\main.exe` y `dist\run_backend.exe`. En desarrollo el launcher ejecuta `run_backend.py` mediante `sys.executable`; en la versión congelada usa el ejecutable hermano `run_backend.exe`. El backend busca los archivos incluidos bajo `frontend_build`.

## 3. Base de datos local

La primera ejecución crea `hotel.db` en `%LOCALAPPDATA%\HotelSistema`. Si `%LOCALAPPDATA%` no está disponible, usa `~/.hotel_sistema`. La base no se instala en `Program Files`, por lo que los datos sobreviven a actualizaciones y no requieren permisos de administrador.

## 4. Instalador Inno Setup

Instala Inno Setup y abre `installer.iss`. Asegúrate de haber ejecutado PyInstaller antes, porque el script toma `dist\main.exe`:

```powershell
iscc installer.iss
```

El instalador genera `installer_output\HotelSistemaSetup.exe`, instala la aplicación y crea accesos directos en el escritorio y el menú Inicio. También crea `%LOCALAPPDATA%\HotelSistema` si todavía no existe.

> TODO: Si se integra el entrypoint Django existente, confirmar sus dependencias y migraciones SQLite antes de distribuir la aplicación.