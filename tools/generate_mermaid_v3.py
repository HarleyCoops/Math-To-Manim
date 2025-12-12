
import base64

mermaid_code = """flowchart TD
    A("User Request: Explain Cosmology") --> B{"Reverse Query:<br/>What comes BEFORE?"}
    B --> C["Layer 1:<br/>General Relativity, Redshift, CMB"]
    
    C --> D{"Reverse Query:<br/>What comes BEFORE?"}
    D --> E["Layer 2:<br/>Special Relativity, Diff Geometry"]
    
    E --> F{"Reverse Query:<br/>What comes BEFORE?"}
    F --> G["Layer 3:<br/>Galilean Relativity, Speed of Light"]
    
    G -.-> H(("Foundation Reached"))
    H ==> I["Build Animation:<br/>Foundation to Target"]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style B fill:#fff3e0,stroke:#ff9800
    style D fill:#fff3e0,stroke:#ff9800
    style F fill:#fff3e0,stroke:#ff9800
    style I fill:#e8f5e9,stroke:#2e7d32,stroke-width:4px
    style H fill:#f3e5f5,stroke:#7b1fa2
"""

# Use urlsafe base64 encoding
encoded_bytes = base64.urlsafe_b64encode(mermaid_code.encode("utf-8"))
encoded_string = encoded_bytes.decode("utf-8")

# Remove any padding characters '=' if present (Mermaid ink handles this better usually, but standard rule is optional)
# url = f"https://mermaid.ink/img/{encoded_string}"
print(f"https://mermaid.ink/img/{encoded_string}")
