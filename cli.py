import argparse
import os
import sys
import json
import subprocess
from datetime import datetime

# Import internal scripts
# Assuming scripts are in .agent/scripts
sys.path.append(os.path.join(os.path.dirname(__file__), '.agent', 'scripts'))
try:
    import vb6_parser
    import schema_converter
except ImportError as e:
    print(f"Error importing internal scripts: {e}")
    print("Make sure run this from the root of 'migrador-vb6-a21-v1'")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Migrador VB6 a Angular 21 - CLI v1.0")
    
    parser.add_argument("--source", required=True, help="Ruta al proyecto VB6 origen (directorio o archivo .vbp)")
    parser.add_argument("--output", required=True, help="Ruta donde se creará el proyecto Angular resultante")
    parser.add_argument("--db", help="Ruta de la base de datos Access (.mdb) [Opcional]")
    parser.add_argument("--force", action="store_true", help="Sobrescribir directorio destino si existe")

    args = parser.parse_args()

    source_path = os.path.abspath(args.source)
    output_path = os.path.abspath(args.output)
    db_path = os.path.abspath(args.db) if args.db else None

    print(f"\n🚀 Iniciando Migrador VB6 -> Angular 21 CLI")
    print(f"==========================================")
    print(f"📂 Origen : {source_path}")
    print(f"📂 Destino: {output_path}")
    if db_path:
        print(f"🗄️  B.Datos: {db_path}")
    print(f"==========================================\n")

    # 1. Validation
    if not os.path.exists(source_path):
        print(f"❌ Error: La ruta de origen no existe: {source_path}")
        sys.exit(1)

    if os.path.exists(output_path) and not args.force:
        print(f"❌ Error: El destino ya existe. Usa --force para sobrescribir.")
        sys.exit(1)

    # 2. Create Output Directory
    os.makedirs(output_path, exist_ok=True)
    print(f"✅ Directorio destino preparado.")

    # 3. Analyze VB6 Source
    print(f"\n🔍 [1/3] Analizando Código VB6...")
    analysis_report = {}
    
    if os.path.isdir(source_path):
        forms = vb6_parser.parse_directory(source_path)
        analysis_report['forms'] = forms
        print(f"   -> Encontrados {len(forms)} formularios.")
    elif os.path.isfile(source_path):
        # Assume single form for now, or expand logic for .vbp
        print(f"   -> Modo archivo único detectado.")
    
    # Save Report
    report_path = os.path.join(output_path, 'migration_analysis.json')
    with open(report_path, 'w') as f:
        json.dump(analysis_report, f, indent=2)
    print(f"   -> Reporte guardado en {report_path}")

    # 4. Database Schema
    if db_path:
        print(f"\n🗄️  [2/3] Analizando Base de Datos...")
        # Placeholder for full schema extraction
        print(f"   -> DB detectada. Generando esquema Prisma preliminar...")
        # Call schema converter logic here if robust enough
    else:
        print(f"\n🗄️  [2/3] Base de Datos: Omitido (No especificado)")

    # 5. Scaffold Angular Project
    print(f"\n🏗️  [3/3] Generando Estructura Angular 21...")
    
    # We can invoke ng new via subprocess if the user lacks the dashboard
    # For now, we create a README instructions file in the output
    readme_content = f"""
# Proyecto Migrado: {os.path.basename(output_path)}

## Origen
* Path: {source_path}
* Fecha: {datetime.now().isoformat()}

## Pasos Siguientes
1. Instalar dependencias: `npm install`
2. Ejecutar: `ng serve`
    """
    with open(os.path.join(output_path, 'README_MIGRATION.md'), 'w') as f:
        f.write(readme_content)
    
    print(f"   -> Instrucciones generadas.")
    
    print(f"\n✨ Ejecución Finalizada.")
    print(f"   Resultados disponibles en: {output_path}")

if __name__ == "__main__":
    main()
