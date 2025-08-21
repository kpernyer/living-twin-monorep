#!/usr/bin/env python3
"""
Script to generate and export OpenAPI specification for client generation.
"""
import json
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

def generate_openapi_spec():
    """Generate OpenAPI specification and save to file."""
    
    # Generate OpenAPI specification
    openapi_spec = app.openapi()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs"
    output_dir.mkdir(exist_ok=True)
    
    # Save OpenAPI spec as JSON
    json_path = output_dir / "openapi.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
    
    # Save OpenAPI spec as YAML (optional)
    try:
        import yaml
        yaml_path = output_dir / "openapi.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ OpenAPI spec saved to {json_path} and {yaml_path}")
    except ImportError:
        print(f"✅ OpenAPI spec saved to {json_path}")
        print("💡 Install PyYAML to also generate YAML format: pip install PyYAML")
    
    # Print some statistics
    print(f"📊 API Statistics:")
    print(f"   - Paths: {len(openapi_spec.get('paths', {}))}")
    print(f"   - Schemas: {len(openapi_spec.get('components', {}).get('schemas', {}))}")
    print(f"   - Tags: {len(openapi_spec.get('tags', []))}")
    
    # Print available endpoints
    print(f"\n🔗 Available Endpoints:")
    paths = openapi_spec.get('paths', {})
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                summary = details.get('summary', 'No summary')
                print(f"   {method.upper():6} {path:30} - {summary}")
    
    return json_path

if __name__ == "__main__":
    spec_path = generate_openapi_spec()
    print(f"\n🎉 OpenAPI specification generated successfully!")
    print(f"📄 Location: {spec_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. View interactive docs: http://localhost:8000/docs")
    print(f"   2. Generate TypeScript client: npx @openapitools/openapi-generator-cli generate -i {spec_path} -g typescript-fetch -o ./generated-client")
    print(f"   3. Import into Postman for API testing")
