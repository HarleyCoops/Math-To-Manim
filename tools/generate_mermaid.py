
import base64

mermaid_code = """
graph TD
    A[User Request: 'Explain Cosmology'] --> B{Reverse Query:<br/>What comes BEFORE?}
    B --> C[Layer 1:<br/>General Relativity, Redshift, CMB]
    
    C --> D{Reverse Query:<br/>What comes BEFORE?}
    D --> E[Layer 2:<br/>Special Relativity, Diff Geometry]
    
    E --> F{Reverse Query:<br/>What comes BEFORE?}
    F --> G[Layer 3:<br/>Galilean Relativity, Speed of Light]
    
    G -.-> H((Foundation Reached))
    H ==> I[Build Animation:<br/>Foundation -> Target]

    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style B fill:#fff3e0,stroke:#ff9800
    style D fill:#fff3e0,stroke:#ff9800
    style F fill:#fff3e0,stroke:#ff9800
    style I fill:#e8f5e9,stroke:#2e7d32,stroke-width:4px
    style H fill:#f3e5f5,stroke:#7b1fa2
"""

# Mermaid.ink expects base64 encoded string of the diagram
encoded_string = base64.b64encode(mermaid_code.encode("utf-8")).decode("utf-8")
url = f"https://mermaid.ink/img/{encoded_string}"

print(url)
