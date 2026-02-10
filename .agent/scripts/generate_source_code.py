import os
import json
from pathlib import Path

def load_inventory(analysis_dir):
    with open(f"{analysis_dir}/inventory.json", "r", encoding="utf-8") as f:
        return json.load(f)

def create_angular_structure(output_dir):
    """Creates the basic file structure for a Standalone Angular 18/19+ App"""
    dirs = [
        "src/app/components",
        "src/app/services",
        "src/app/models",
        "src/app/shared",
        "src/assets"
    ]
    for d in dirs:
        os.makedirs(f"{output_dir}/{d}", exist_ok=True)
        
    # Create package.json
    package_json = {
        "name": "migrated-angular-app",
        "version": "0.0.1",
        "scripts": {
            "ng": "ng",
            "start": "ng serve",
            "build": "ng build",
            "test": "ng test"
        },
        "dependencies": {
            "@angular/animations": "^19.0.0",
            "@angular/common": "^19.0.0",
            "@angular/compiler": "^19.0.0",
            "@angular/core": "^19.0.0",
            "@angular/forms": "^19.0.0",
            "@angular/platform-browser": "^19.0.0",
            "@angular/platform-browser-dynamic": "^19.0.0",
            "@angular/router": "^19.0.0",
            "rxjs": "~7.8.0",
            "tslib": "^2.3.0",
            "zone.js": "~0.14.0" 
        },
        "devDependencies": {
            "@angular-devkit/build-angular": "^19.0.0",
            "@angular/cli": "^19.0.0",
            "@angular/compiler-cli": "^19.0.0",
            "@types/jasmine": "~4.3.0",
            "typescript": "~5.2.0"
        }
    }
    
    with open(f"{output_dir}/package.json", "w") as f:
        json.dump(package_json, f, indent=2)

    # Create angular.json (Minimal)
    angular_json = {
      "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
      "version": 1,
      "newProjectRoot": "projects",
      "projects": {
        "migrated-app": {
          "projectType": "application",
          "schematics": {
            "@angular/component": {
              "style": "css",
              "standalone": True
            }
          },
          "root": "",
          "sourceRoot": "src",
          "prefix": "app",
          "architect": {
            "build": {
              "builder": "@angular-devkit/build-angular:application",
              "options": {
                "outputPath": "dist/migrated-app",
                "index": "src/index.html",
                "browser": "src/main.ts",
                "polyfills": ["zone.js"],
                "tsConfig": "tsconfig.app.json",
                "assets": ["src/favicon.ico", "src/assets"],
                "styles": ["src/styles.css"],
                "scripts": []
              }
            }
          }
        }
      }
    }
    with open(f"{output_dir}/angular.json", "w") as f:
        json.dump(angular_json, f, indent=2)
        
    # Create main.ts (Bootstrap)
    main_ts = """import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
"""
    with open(f"{output_dir}/src/main.ts", "w") as f:
        f.write(main_ts)
        
    # Create app.config.ts (Zoneless Provider)
    app_config_ts = """import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes)
  ]
};
"""
    with open(f"{output_dir}/src/app/app.config.ts", "w") as f:
        f.write(app_config_ts)
        
    # Create index.html
    index_html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>MigratedApp</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
  <app-root></app-root>
</body>
</html>"""
    with open(f"{output_dir}/src/index.html", "w") as f:
        f.write(index_html)
        
    # Create app.component.ts
    app_comp_ts = """import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  template: `
    <div class="container">
      <nav>
        <h1>Migrated Application</h1>
        <ul>
          <!-- LINKS_PLACEHOLDER -->
        </ul>
      </nav>
      <main>
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .container { font-family: sans-serif; padding: 20px; }
    nav { background: #f0f0f0; padding: 10px; margin-bottom: 20px; }
    ul { list-style: none; display: flex; gap: 15px; padding: 0; }
    a { text-decoration: none; color: #333; font-weight: bold; }
    a:hover { color: blue; }
  `]
})
export class AppComponent {
  title = 'migrated-app';
}
"""
    with open(f"{output_dir}/src/app/app.component.ts", "w") as f:
        f.write(app_comp_ts)


def generate_components(output_dir, inventory):
    """Generates Angular components for each VB6 form"""
    
    routes = []
    nav_links = []
    
    if "forms" in inventory and "files" in inventory["forms"]:
        for form in inventory["forms"]["files"]:
            # Clean name (remove extension, handle special chars)
            base_name = os.path.splitext(form["name"])[0]
            comp_name = base_name.replace(" ", "")
            file_name = comp_name.lower()
            
            # Generate Component PATH
            comp_dir = f"{output_dir}/src/app/components/{file_name}"
            os.makedirs(comp_dir, exist_ok=True)
            
            # 1. Component TS
            ts_content = f"""import {{ Component, ChangeDetectionStrategy, signal }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';
import {{ FormsModule }} from '@angular/forms';

@Component({{
  selector: 'app-{file_name}',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './{file_name}.component.html',
  styleUrls: ['./{file_name}.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
}})
export class {comp_name}Component {{
  // State Signals
  title = signal('{base_name}');
  
  constructor() {{
    console.log('{comp_name} initialized');
  }}
  
  // Methods
  onSubmit() {{
    console.log('Form submitted');
  }}
}}
"""
            with open(f"{comp_dir}/{file_name}.component.ts", "w") as f:
                f.write(ts_content)
                
            # 2. Component HTML
            html_content = f"""<div class="form-container">
  <h2>{{{{ title() }}}}</h2>
  <div class="form-content">
    <p>Migrated content for {base_name}</p>
    <!-- TODO: Implement controls from VB6 -->
    
    <div class="actions">
       <button (click)="onSubmit()">Submit</button>
    </div>
  </div>
</div>
"""
            with open(f"{comp_dir}/{file_name}.component.html", "w") as f:
                f.write(html_content)
                
            # 3. Component CSS
            css_content = """.form-container {
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  max-width: 800px;
  margin: 0 auto;
}
h2 { color: #2c3e50; }
.actions { margin-top: 20px; }
button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover { background-color: #0056b3; }
"""
            with open(f"{comp_dir}/{file_name}.component.css", "w") as f:
                f.write(css_content)
                
            # Add to Routes
            routes.append(f"{{ path: '{file_name}', loadComponent: () => import('./components/{file_name}/{file_name}.component').then(m => m.{comp_name}Component) }}")
            nav_links.append(f"""<li><a routerLink="/{file_name}">{base_name}</a></li>""")

    # Update app.routes.ts
    routes_content = "import { Routes } from '@angular/router';\n\nexport const routes: Routes = [\n  " + ",\n  ".join(routes) + ",\n  { path: '', redirectTo: '" + (routes[0].split("'")[1] if routes else "") + "', pathMatch: 'full' }\n];"
    
    with open(f"{output_dir}/src/app/app.routes.ts", "w") as f:
        f.write(routes_content)
        
    # Update App Component Links
    with open(f"{output_dir}/src/app/app.component.ts", "r") as f:
        content = f.read()
    
    new_content = content.replace("<!-- LINKS_PLACEHOLDER -->", "\n          ".join(nav_links))
    with open(f"{output_dir}/src/app/app.component.ts", "w") as f:
        f.write(new_content)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    print(f"🚀 Generating Real Code from {args.analysis} to {args.output}")
    inventory = load_inventory(args.analysis)
    
    create_angular_structure(args.output)
    generate_components(args.output, inventory)
    
    print("✅ Angular App Scaffolding Complete")

if __name__ == "__main__":
    main()
