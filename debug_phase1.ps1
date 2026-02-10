$ErrorActionPreference = "Continue"

$env:VB6_DIR = "vb6-apps/Biblioteca"
$env:ANALYSIS_DIR = "analysis"

Write-Host "--- DEBUG: Running Analysis Scripts Sequentially ---" -ForegroundColor Yellow

# 1. Comprehensive Scanner
Write-Host "`n1. Running vb6_comprehensive_scanner.py..."
python .agent/scripts/vb6_comprehensive_scanner.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/inventory.json" --pretty
if ($LASTEXITCODE -ne 0) { Write-Error "vb6_comprehensive_scanner.py failed with exit code $LASTEXITCODE" }

# 2. Metrics Analyzer
Write-Host "`n2. Running vb6_metrics_analyzer.py..."
python .agent/scripts/vb6_metrics_analyzer.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/metrics.json" --pretty
if ($LASTEXITCODE -ne 0) { Write-Error "vb6_metrics_analyzer.py failed with exit code $LASTEXITCODE" }

# 3. Dead Code Detector
Write-Host "`n3. Running vb6_dead_code_detector.py..."
python .agent/scripts/vb6_dead_code_detector.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/dead_code.json" --pretty
if ($LASTEXITCODE -ne 0) { Write-Error "vb6_dead_code_detector.py failed with exit code $LASTEXITCODE" }

# 4. Dependency Graph
Write-Host "`n4. Running vb6_dependency_graph.py..."
python .agent/scripts/vb6_dependency_graph.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/deps.json" --html "$env:ANALYSIS_DIR/GRAPH.html"
if ($LASTEXITCODE -ne 0) { Write-Error "vb6_dependency_graph.py failed with exit code $LASTEXITCODE" }

# 5. Schema Extractor
Write-Host "`n5. Running vb6_schema_extractor.py..."
python .agent/scripts/vb6_schema_extractor.py "$env:VB6_DIR" -o "$env:ANALYSIS_DIR/schema.json"
if ($LASTEXITCODE -ne 0) { Write-Error "vb6_schema_extractor.py failed with exit code $LASTEXITCODE" }

Write-Host "`n--- DEBUG COMPLETE ---"
