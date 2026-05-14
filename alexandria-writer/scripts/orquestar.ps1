# Alexandria Writer - Orquestador de Flujos
# Uso: .\orquestar.ps1 [fase]
# Fases: ideacion, outline, draft, edicion, marketing, publicacion, all

$base = "C:\Users\crist\OneDrive\Desktop\Claude\TSBN\alexandria-writer"

function Show-Help {
    Write-Host ""
    Write-Host "=== ALEXANDRIA WRITER - ORQUESTADOR ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso: .\orquestar.ps1 [fase]" -ForegroundColor White
    Write-Host ""
    Write-Host "Fases disponibles:" -ForegroundColor Yellow
    Write-Host "  ideacion    - Brainstorming y generacion de ideas"
    Write-Host "  outline     - Estructura narrativa y beats"
    Write-Host "  draft       - Escritura de borradores"
    Write-Host "  edicion     - Revision y pulido"
    Write-Host "  marketing   - Posicionamiento y copy"
    Write-Host "  publicacion - Preparacion para lanzamiento"
    Write-Host "  all         - Muestra todas las fases"
    Write-Host ""
    Write-Host "Ejemplo: .\orquestar.ps1 ideacion" -ForegroundColor Green
    Write-Host ""
}

function Show-Fase {
    param(
        [string]$nombre,
        [string]$descripcion,
        [string[]]$agentes,
        [string[]]$entregables,
        [string]$siguiente
    )
    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor Cyan
    Write-Host "  FASE: $nombre" -ForegroundColor Cyan
    Write-Host "=============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Descripcion: $descripcion" -ForegroundColor White
    Write-Host ""
    Write-Host "Agentes involucrados:" -ForegroundColor Yellow
    foreach ($a in $agentes) {
        Write-Host "  * $a" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Entregables:" -ForegroundColor Yellow
    foreach ($e in $entregables) {
        Write-Host "  -> $e" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Proxima fase: $siguiente" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para iniciar esta fase, ejecuta los agentes en orden:" -ForegroundColor DarkGray
    Write-Host "  1. Copia el prompt del primer agente (ver .\start-agents.ps1)" -ForegroundColor DarkGray
    Write-Host "  2. Pegalo en tu sesion de Claude/Cursor con tu solicitud" -ForegroundColor DarkGray
    Write-Host "  3. Avanza al siguiente agente cuando el primero termine" -ForegroundColor DarkGray
    Write-Host ""
}

function Run-FaseIdeacion {
    Show-Fase `
        -nombre "IDEACION" `
        -descripcion "Explorar temas, conceptos y la propuesta central del libro. Definir que historia se quiere contar y por que importa." `
        -agentes @(
            "Narrative Architect - brainstorming de conceptos y temas centrales",
            "Research Agent - investigacion de mercado y comp titles",
            "Character Developer - boceto del protagonista y su viaje"
        ) `
        -entregables @(
            "Concepto central de TSBN (1 parrafo)",
            "3-5 temas principales definidos",
            "Boceto del protagonista (nombre, motivacion, conflicto)",
            "Lista de comp titles verificados",
            "Decision: genero, formato, extension objetivo"
        ) `
        -siguiente ".\orquestar.ps1 outline"
}

function Run-FaseOutline {
    Show-Fase `
        -nombre "OUTLINE" `
        -descripcion "Construir la estructura completa: actos, capitulos, beats, arcos de personaje y puntos de inflexion." `
        -agentes @(
            "Narrative Architect - act map y chapter beat sheet",
            "Character Developer - fichas completas de personajes",
            "Worldbuilder - bible del mundo (si aplica)",
            "Style & Tone Guardian - definicion de voz y registro"
        ) `
        -entregables @(
            "Act Map completo (3-5 actos con word counts)",
            "Chapter Beat Sheet (todos los capitulos)",
            "Fichas de personajes principales",
            "Voice Profile del narrador",
            "Decision: punto de vista, estructura temporal, tono"
        ) `
        -siguiente ".\orquestar.ps1 draft"
}

function Run-FaseDraft {
    Show-Fase `
        -nombre "DRAFT (Borrador)" `
        -descripcion "Escribir los capitulos uno a uno, manteniendo coherencia de voz, ritmo y arco narrativo." `
        -agentes @(
            "Narrative Architect - validacion estructural por capitulo",
            "Style & Tone Guardian - revision de prosa en cada capitulo",
            "Dialogue Master - pulido de conversaciones",
            "Character Developer - verificacion de arcos",
            "Research Agent - verificacion de hechos cuando aplica"
        ) `
        -entregables @(
            "Borrador completo del manuscrito",
            "Versionado: Capitulo N - v1 - draft",
            "Notas de integridad estructural",
            "Auditoria de voz y tono"
        ) `
        -siguiente ".\orquestar.ps1 edicion"
}

function Run-FaseEdicion {
    Show-Fase `
        -nombre "EDICION" `
        -descripcion "Revision profunda: estructura, personajes, prosa, dialogo y consistencia." `
        -agentes @(
            "Narrative Architect - diagnostico estructural global",
            "Character Developer - auditoria de arcos y consistencia",
            "Style & Tone Guardian - line edit completo",
            "Dialogue Master - revision de todas las conversaciones",
            "Worldbuilder - consistencia audit (si aplica)"
        ) `
        -entregables @(
            "Manuscrito editado (version 2)",
            "Informe de cambios estructurales",
            "Informe de edicion de linea",
            "Lista de decisiones pendientes del autor"
        ) `
        -siguiente ".\orquestar.ps1 marketing"
}

function Run-FaseMarketing {
    Show-Fase `
        -nombre "MARKETING" `
        -descripcion "Preparar el libro para encontrar a sus lectores: posicionamiento, copy y estrategia." `
        -agentes @(
            "Book Marketing Agent - posicionamiento y copy",
            "Research Agent - analisis de mercado y audiencia",
            "Style & Tone Guardian - pulido de sinopsis y blurbs"
        ) `
        -entregables @(
            "Positioning Statement",
            "Copy Package (hook, blurb, taglines)",
            "Audience Map",
            "Launch Timeline",
            "Decision: plataforma de publicacion y precio"
        ) `
        -siguiente ".\orquestar.ps1 publicacion"
}

function Run-FasePublicacion {
    Show-Fase `
        -nombre "PUBLICACION" `
        -descripcion "Ejecutar el lanzamiento: pre-orders, promocion y distribucion." `
        -agentes @(
            "Book Marketing Agent - ejecucion del launch timeline",
            "Audio Integration Agent - audiobook (opcional)"
        ) `
        -entregables @(
            "Libro publicado en plataforma(s) elegida(s)",
            "Campana de lanzamiento activa",
            "Audiobook producido (opcional)"
        ) `
        -siguiente "Celebrar y empezar el siguiente libro"
}

# Main
if ($args.Count -eq 0) {
    Show-Help
    exit
}

switch ($args[0].ToLower()) {
    "ideacion"    { Run-FaseIdeacion }
    "outline"     { Run-FaseOutline }
    "draft"       { Run-FaseDraft }
    "edicion"     { Run-FaseEdicion }
    "marketing"   { Run-FaseMarketing }
    "publicacion" { Run-FasePublicacion }
    "all" {
        Run-FaseIdeacion
        Run-FaseOutline
        Run-FaseDraft
        Run-FaseEdicion
        Run-FaseMarketing
        Run-FasePublicacion
    }
    default {
        Write-Host "Fase desconocida: $($args[0])" -ForegroundColor Red
        Show-Help
    }
}
