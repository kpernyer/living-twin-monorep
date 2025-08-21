#!/usr/bin/env python3
"""
Script to generate API documentation in Markdown format from OpenAPI specification.
"""
import json
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

def generate_markdown_docs():
    """Generate API documentation in Markdown format."""
    
    # Generate OpenAPI specification
    openapi_spec = app.openapi()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs"
    output_dir.mkdir(exist_ok=True)
    
    # Generate Markdown documentation
    md_content = []
    
    # Title and description
    info = openapi_spec.get('info', {})
    md_content.append(f"# {info.get('title', 'API Documentation')}")
    md_content.append(f"**Version:** {info.get('version', '1.0.0')}")
    md_content.append("")
    md_content.append(info.get('description', '').strip())
    md_content.append("")
    
    # Contact and license
    if 'contact' in info:
        contact = info['contact']
        md_content.append("## Contact")
        if 'name' in contact:
            md_content.append(f"**Name:** {contact['name']}")
        if 'email' in contact:
            md_content.append(f"**Email:** {contact['email']}")
        if 'url' in contact:
            md_content.append(f"**URL:** {contact['url']}")
        md_content.append("")
    
    # Servers
    servers = openapi_spec.get('servers', [])
    if servers:
        md_content.append("## Servers")
        for server in servers:
            md_content.append(f"- **{server.get('description', 'Server')}**: `{server.get('url', '')}`")
        md_content.append("")
    
    # Authentication
    md_content.append("## Authentication")
    md_content.append("All endpoints require Firebase JWT authentication via the `Authorization` header:")
    md_content.append("```")
    md_content.append("Authorization: Bearer <firebase-jwt-token>")
    md_content.append("```")
    md_content.append("")
    
    # Group endpoints by tags
    paths = openapi_spec.get('paths', {})
    tags = openapi_spec.get('tags', [])
    
    # Create tag mapping
    tag_info = {tag['name']: tag.get('description', '') for tag in tags}
    
    # Group paths by tags
    endpoints_by_tag = {}
    for path, path_info in paths.items():
        for method, method_info in path_info.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                endpoint_tags = method_info.get('tags', ['Untagged'])
                for tag in endpoint_tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append({
                        'path': path,
                        'method': method.upper(),
                        'info': method_info
                    })
    
    # Generate documentation for each tag
    for tag, description in tag_info.items():
        if tag in endpoints_by_tag:
            md_content.append(f"## {tag}")
            if description:
                md_content.append(description)
                md_content.append("")
            
            for endpoint in endpoints_by_tag[tag]:
                path = endpoint['path']
                method = endpoint['method']
                info = endpoint['info']
                
                # Endpoint header
                summary = info.get('summary', f"{method} {path}")
                md_content.append(f"### {summary}")
                md_content.append(f"`{method} {path}`")
                md_content.append("")
                
                # Description
                if 'description' in info:
                    md_content.append(info['description'])
                    md_content.append("")
                
                # Parameters
                parameters = info.get('parameters', [])
                if parameters:
                    md_content.append("**Parameters:**")
                    md_content.append("")
                    for param in parameters:
                        param_name = param.get('name', '')
                        param_type = param.get('schema', {}).get('type', 'string')
                        param_desc = param.get('description', '')
                        required = " *(required)*" if param.get('required', False) else ""
                        md_content.append(f"- `{param_name}` ({param_type}){required}: {param_desc}")
                    md_content.append("")
                
                # Request body
                if 'requestBody' in info:
                    md_content.append("**Request Body:**")
                    request_body = info['requestBody']
                    if 'description' in request_body:
                        md_content.append(request_body['description'])
                    
                    content = request_body.get('content', {})
                    if 'application/json' in content:
                        schema_ref = content['application/json'].get('schema', {}).get('$ref', '')
                        if schema_ref:
                            schema_name = schema_ref.split('/')[-1]
                            md_content.append(f"Schema: `{schema_name}`")
                    md_content.append("")
                
                # Responses
                responses = info.get('responses', {})
                if responses:
                    md_content.append("**Responses:**")
                    md_content.append("")
                    for status_code, response_info in responses.items():
                        description = response_info.get('description', '')
                        md_content.append(f"- `{status_code}`: {description}")
                    md_content.append("")
                
                md_content.append("---")
                md_content.append("")
    
    # Add schemas section
    components = openapi_spec.get('components', {})
    schemas = components.get('schemas', {})
    
    if schemas:
        md_content.append("## Data Models")
        md_content.append("")
        
        for schema_name, schema_info in schemas.items():
            md_content.append(f"### {schema_name}")
            
            if 'description' in schema_info:
                md_content.append(schema_info['description'])
            
            schema_type = schema_info.get('type', 'object')
            md_content.append(f"**Type:** `{schema_type}`")
            md_content.append("")
            
            # Properties
            properties = schema_info.get('properties', {})
            if properties:
                md_content.append("**Properties:**")
                md_content.append("")
                required_fields = schema_info.get('required', [])
                
                for prop_name, prop_info in properties.items():
                    prop_type = prop_info.get('type', 'string')
                    prop_desc = prop_info.get('description', '')
                    required = " *(required)*" if prop_name in required_fields else ""
                    example = prop_info.get('example', '')
                    example_text = f" - Example: `{example}`" if example else ""
                    
                    md_content.append(f"- `{prop_name}` ({prop_type}){required}: {prop_desc}{example_text}")
                
                md_content.append("")
            
            md_content.append("---")
            md_content.append("")
    
    # Write to file
    md_path = output_dir / "API_DOCUMENTATION.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
    
    return md_path

if __name__ == "__main__":
    md_path = generate_markdown_docs()
    print(f"✅ API documentation generated in Markdown format")
    print(f"📄 Location: {md_path}")
    print(f"\n📊 Documentation includes:")
    print(f"   - Complete endpoint documentation")
    print(f"   - Request/response schemas")
    print(f"   - Parameter descriptions")
    print(f"   - Authentication information")
    print(f"   - Data model definitions")
