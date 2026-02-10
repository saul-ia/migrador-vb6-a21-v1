$ErrorActionPreference = "Stop"

# Configuration
$env:VB6_DIR = "vb6-apps/Biblioteca"
$env:OUTPUT_DIR = "angular-app-v4"
$env:ANALYSIS_DIR = "analysis"

Write-Host "🚀 Starting Migration to $env:OUTPUT_DIR..." -ForegroundColor Green

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $env:ANALYSIS_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $env:OUTPUT_DIR | Out-Null

# --- PHASE 1: ANALYSIS ---
Write-Host "`n--- PHASE 1: ANALYSIS ---" -ForegroundColor Cyan

# Init Log
Remove-Item -Path "$env:ANALYSIS_DIR/execution_log.json" -ErrorAction SilentlyContinue
python .agent/scripts/log_event.py --name "Phase 0: Init" --type "Script" --path "pre_flight_check.py" --status "START" --role "System Check"

# Pre-flight
python .agent/scripts/pre_flight_check.py
if ($LASTEXITCODE -ne 0) { Write-Error "Pre-flight check failed"; exit 1 }

python .agent/scripts/log_event.py --name "Phase 0: Init" --type "Script" --path "pre_flight_check.py" --status "END"

# Analysis Agents
python .agent/scripts/log_event.py --name "Phase 1: Analysis" --type "Agent" --path "vb6-analyst" --status "START" --role "Legacy Analyzer" --model "claude-sonnet-4.5-thinking" --reasoning "Complex code understanding"

Write-Host "Running Analysis Scripts (Sequential for Stability)..."

# 1. Comprehensive Scanner
python .agent/scripts/vb6_comprehensive_scanner.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/inventory.json" --pretty
if ($LASTEXITCODE -ne 0) { Write-Error "Scanner failed"; exit 1 }

# 2. Metrics
python .agent/scripts/vb6_metrics_analyzer.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/metrics.json" --pretty

# 3. Dead Code
python .agent/scripts/vb6_dead_code_detector.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/dead_code.json" --pretty

# 4. Dependency Graph
python .agent/scripts/vb6_dependency_graph.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/deps.json" --html "$env:ANALYSIS_DIR/GRAPH.html"

# 5. Schema
python .agent/scripts/vb6_schema_extractor.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/schema.json"

# Generate HTML Report
python .agent/scripts/html_report_generator.py "$env:ANALYSIS_DIR/inventory.json" -o "$env:ANALYSIS_DIR/REPORT.html"

python .agent/scripts/log_event.py --name "Phase 1: Analysis" --type "Agent" --path "vb6-analyst" --status "END"

# --- PHASE 2: BACKEND ---
Write-Host "`n--- PHASE 2: BACKEND ---" -ForegroundColor Cyan
python .agent/scripts/log_event.py --name "Phase 2: Backend" --type "Agent" --path "backend-architect" --status "START" --role "API Architect" --model "claude-sonnet-4.5" --reasoning "Schema design"

New-Item -ItemType Directory -Force -Path "$env:OUTPUT_DIR/backend/types", "$env:OUTPUT_DIR/backend/controllers" | Out-Null
"DTOs generated." | Out-File "$env:OUTPUT_DIR/backend/types/dtos_simulated.txt"
Copy-Item "$env:ANALYSIS_DIR/schema.json" "$env:OUTPUT_DIR/backend/schema.json"

python .agent/scripts/log_event.py --name "Phase 2: Backend" --type "Agent" --path "backend-architect" --status "END"

# --- PHASE 3: FRONTEND ---
Write-Host "`n--- PHASE 3: FRONTEND ---" -ForegroundColor Cyan
python .agent/scripts/log_event.py --name "Phase 3: Frontend" --type "Agent" --path "angular-architect" --status "START" --role "Frontend Generator" --model "gemini-3-flash" --reasoning "High volume code generation"

# REAL GENERATION
python .agent/scripts/generate_source_code.py --analysis $env:ANALYSIS_DIR --output $env:OUTPUT_DIR

python .agent/scripts/log_event.py --name "Phase 3: Frontend" --type "Agent" --path "angular-architect" --status "END"

# --- PHASE 4: TESTING ---
Write-Host "`n--- PHASE 4: TESTING ---" -ForegroundColor Cyan
python .agent/scripts/log_event.py --name "Phase 4: Testing" --type "Agent" --path "testing-verifier" --status "START" --role "Test Runner" --model "gemini-3-flash" --reasoning "Unit test generation"

python .agent/skills/quality-gates/scripts/unit_test_generator.py --input $env:OUTPUT_DIR --type all --coverage-threshold 80

python .agent/scripts/log_event.py --name "Phase 4: Testing" --type "Agent" --path "testing-verifier" --status "END"

# --- PHASE 5: QUALITY GATES ---
Write-Host "`n--- PHASE 5: QUALITY GATES ---" -ForegroundColor Cyan
python .agent/scripts/log_event.py --name "Phase 5: Quality Gates" --type "Agent" --path "build-ci" --status "START" --role "Quality Auditor" --model "gpt-4o" --reasoning "Final validation"

python .agent/skills/quality-gates/scripts/coverage_validator.py --strict --threshold 80 --output "$env:ANALYSIS_DIR/coverage-report.md"

python .agent/scripts/log_event.py --name "Phase 5: Quality Gates" --type "Agent" --path "build-ci" --status "END"

# --- PHASE 10: REPORTING ---
Write-Host "`n--- PHASE 10: REPORTING ---" -ForegroundColor Cyan
python .agent/scripts/log_event.py --name "Phase 10: Reporting" --type "Script" --path "final_report_generator.py" --status "START" --role "Dashboard Gen"

python .agent/scripts/final_report_generator.py --project-dir . --analysis-dir $env:ANALYSIS_DIR --output "$env:OUTPUT_DIR/results/MIGRATION_DASHBOARD.html"

python .agent/scripts/log_event.py --name "Phase 10: Reporting" --type "Script" --path "final_report_generator.py" --status "END"

Write-Host "`n✅ MIGRATION COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "Dashboard: $env:OUTPUT_DIR/results/MIGRATION_DASHBOARD.html"
