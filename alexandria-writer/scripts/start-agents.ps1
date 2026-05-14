# Alexandria Writer — Script de Orquestación
# Uso: .\start-agents.ps1 [nombre-del-agente]
# Ejemplos:
#   .\start-agents.ps1 narrative      → Inicia Narrative Architect
#   .\start-agents.ps1 character     → Inicia Character Developer
#   .\start-agents.ps1 all           → Lista todos los agentes disponibles

$base = "C:\Users\crist\OneDrive\Desktop\Claude\TSBN\alexandria-writer"
$agents = @{
    "narrative"    = @{ name="Narrative Architect";    file="agents/narrative-arch/writer-narrative-arch.md";    desc="Estructura, actos, beats, pacing" }
    "character"    = @{ name="Character Developer";    file="agents/character-dev/writer-character-dev.md";    desc="Fichas, arcos, voz, relaciones" }
    "world"        = @{ name="Worldbuilder";           file="agents/worldbuilding/writer-worldbuilding.md";      desc="Lore, reglas, cultura, geografía" }
    "style"        = @{ name="Style & Tone Guardian";  file="agents/style-tone/writer-style-tone.md";           desc="Prosa, ritmo, voz, línea a línea" }
    "dialogue"     = @{ name="Dialogue Master";        file="agents/dialogue/writer-dialogue.md";               desc="Conversaciones, subtexto, poder" }
    "research"     = @{ name="Research Agent";         file="agents/research/writer-research.md";                desc="Investigación, verificación, fuentes" }
    "marketing"    = @{ name="Book Marketing Agent";   file="agents/marketing/writer-marketing.md";             desc="Posicionamiento, copy, lanzamiento" }
    "audio"        = @{ name="Audio Integration Agent"; file="agents/audio/writer-audio.md";                   desc="Dictado, transcripción, integración" }
}

function Show-Agents {
    Write-Host ""
    Write-Host "=== AGENTES DISPONIBLES ===" -ForegroundColor Cyan
    Write-Host ""
    foreach ($key in $agents.Keys | Sort-Object) {
        $a = $agents[$key]
        Write-Host "  $($key.PadRight(12))" -NoNewline -ForegroundColor Yellow
        Write-Host " → $($a.name)" -NoNewline -ForegroundColor White
        Write-Host " ($($a.desc))" -ForegroundColor DarkGray
    }
    Write-Host ""
    Write-Host "Uso: .\start-agents.ps1 [nombre]" -ForegroundColor Green
    Write-Host "Ejemplo: .\start-agents.ps1 narrative" -ForegroundColor Green
    Write-Host ""
}

function Start-Agent {
    param([string]$key)
    if (-not $agents.ContainsKey($key)) {
        Write-Host "Agente '$key' no encontrado." -ForegroundColor Red
        Show-Agents
        return
    }
    $a = $agents[$key]
    $path = Join-Path $base $a.file
    $skill = Join-Path $base "skills/writer-base.md"
    $context = Join-Path $base "skills/tsbn-context.md"

    Write-Host ""
    Write-Host "=== INICIANDO: $($a.name) ===" -ForegroundColor Cyan
    Write-Host "Descripción: $($a.desc)" -ForegroundColor White
    Write-Host ""

    # Verificar que el archivo del agente existe
    if (Test-Path $path) {
        Write-Host "Archivo de agente : $path" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No se encuentra $path" -ForegroundColor Red
        return
    }

    # Verificar skill base y contexto
    if (Test-Path $skill) {
        Write-Host "Skill base         : $skill" -ForegroundColor Green
    } else {
        Write-Host "ADVERTENCIA: Skill base no encontrada" -ForegroundColor Yellow
    }

    if (Test-Path $context) {
        Write-Host "Contexto TSBN      : $context" -ForegroundColor Green
    } else {
        Write-Host "ADVERTENCIA: Contexto TSBN no completado" -ForegroundColor Yellow
        Write-Host "             Completa skills/tsbn-context.md para mejores resultados" -ForegroundColor DarkYellow
    }

    Write-Host ""
    Write-Host "Instrucciones:" -ForegroundColor Cyan
    Write-Host "1. Copia el contenido de:" -ForegroundColor White
    Write-Host "   $path" -ForegroundColor Yellow
    Write-Host "2. Asegúrate de que el skill base esté cargado:" -ForegroundColor White
    Write-Host "   $skill" -ForegroundColor Yellow
    Write-Host "3. Si el contexto TSBN está completo, inclúyelo:" -ForegroundColor White
    Write-Host "   $context" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Sugerencia: Pega el prompt del agente en tu sesión de Claude/Cursor" -ForegroundColor Green
    Write-Host "            y comienza la conversación con tu solicitud." -ForegroundColor Green
    Write-Host ""
}

# Main
if ($args.Count -eq 0 -or $args[0] -eq "all" -or $args[0] -eq "list") {
    Show-Agents
} else {
    Start-Agent -key $args[0].ToLower()
}
