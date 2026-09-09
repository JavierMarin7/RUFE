# Servidor local para el tablero RUFE.
# Usa solo .NET, no requiere Python ni instalar nada.
# Se ejecuta desde INICIAR_TABLERO.bat cuando no hay Python disponible.

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$puerto = 8000

$mime = @{
  ".html"="text/html; charset=utf-8"; ".htm"="text/html; charset=utf-8"
  ".js"="application/javascript; charset=utf-8"; ".css"="text/css; charset=utf-8"
  ".json"="application/json; charset=utf-8"; ".geojson"="application/json; charset=utf-8"
  ".csv"="text/csv; charset=utf-8"; ".txt"="text/plain; charset=utf-8"
  ".md"="text/plain; charset=utf-8"; ".png"="image/png"; ".jpg"="image/jpeg"
  ".svg"="image/svg+xml"; ".ico"="image/x-icon"
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$puerto/")

try { $listener.Start() }
catch {
  Write-Host ""
  Write-Host "  No se pudo abrir el puerto $puerto." -ForegroundColor Red
  Write-Host "  Puede que ya haya otro tablero corriendo. Cierra esa ventana negra"
  Write-Host "  y vuelve a intentar, o abre ABRIR_SIN_SERVIDOR.html con doble clic."
  Write-Host ""
  Read-Host "  Enter para salir"
  exit 1
}

Write-Host ""
Write-Host "  Tablero RUFE - Valle del Cauca" -ForegroundColor Cyan
Write-Host "  Servidor activo en http://localhost:$puerto"
Write-Host "  Deja esta ventana abierta. Ctrl + C para detenerlo."
Write-Host ""

Start-Process "http://localhost:$puerto/index.html"

while ($listener.IsListening) {
  try {
    $ctx = $listener.GetContext()
    $ruta = [System.Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath)
    if ($ruta -eq "/") { $ruta = "/index.html" }

    $rel = $ruta.TrimStart("/") -replace "/", "\"
    $archivo = Join-Path $raiz $rel
    $completo = [System.IO.Path]::GetFullPath($archivo)

    # no servir nada fuera de la carpeta del paquete
    if (-not $completo.StartsWith([System.IO.Path]::GetFullPath($raiz))) {
      $ctx.Response.StatusCode = 403; $ctx.Response.Close(); continue
    }

    if (Test-Path $completo -PathType Leaf) {
      $bytes = [System.IO.File]::ReadAllBytes($completo)
      $ext = [System.IO.Path]::GetExtension($completo).ToLower()
      $tipo = $mime[$ext]; if (-not $tipo) { $tipo = "application/octet-stream" }
      $ctx.Response.ContentType = $tipo
      $ctx.Response.ContentLength64 = $bytes.Length
      $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $ctx.Response.StatusCode = 404
      $m = [System.Text.Encoding]::UTF8.GetBytes("No se encontro: $rel")
      $ctx.Response.OutputStream.Write($m, 0, $m.Length)
    }
    $ctx.Response.Close()
  } catch {
    # una peticion fallida no debe tumbar el servidor
  }
}
