# MCP Server Troubleshooting Guide

## Overview

This guide documents the issues encountered with Model Context Protocol (MCP) servers in Cline/Claude and the steps taken to resolve them. The primary problem was that MCP servers were failing to connect, showing errors like "spawn npx ENOENT" in the MCP Servers panel.

## Initial Problems

There were several issues that needed to be addressed:

1. **JSON Syntax Errors**: The MCP configuration files had syntax errors that prevented proper parsing.
2. **PATH Environment Variable**: The `npx` command wasn't accessible from the PATH when the MCP server tried to run it.
3. **NPX Module Resolution**: There was an issue with how `npx` was trying to find the firecrawl-mcp package.

## Step-by-Step Troubleshooting Process

### 1. Fixing JSON Syntax Errors

The first issue was with the JSON syntax in the configuration files:

**Original Cline MCP settings file** (with errors):
```json
mcpServers": {
    "github.com/mendableai/firecrawl-mcp-server": {
      "command": "npx"
      "args": ["-y" "firecrawl-mcp"]
      "env": {
        "FIRECRAWL_API_KEY": "YOUR_API_KEY_HERE"
      }
      "disabled": false
      "autoApprove": []
    }
  }
}
```

Problems:
- Missing opening curly brace
- Missing commas after each property
- Missing comma in the args array

**Fixed Cline MCP settings file**:
```json
{
  "mcpServers": {
    "github.com/mendableai/firecrawl-mcp-server": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "YOUR_API_KEY_HERE"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Original Claude desktop config file** (with errors):
```json
mcpServers": {}
}
```

Problems:
- Missing opening curly brace

**Fixed Claude desktop config file**:
```json
{
  "mcpServers": {}
}
```

### 2. Addressing PATH Issues

After fixing the JSON syntax, we encountered a "spawn npx ENOENT" error, indicating that the system couldn't find the `npx` command. We verified that Node.js and npm were installed:

```
node -v  # Output: v20.18.0
npx -v   # Output: 10.8.2
```

We found the location of the `npx` command:
```
dir "C:\Users\chris\AppData\Roaming\npm\npx*"
```

This showed that `npx` was located at `C:\Users\chris\AppData\Roaming\npm\npx.cmd`.

We updated the MCP settings to use the full path to `npx.cmd`:
```json
{
  "mcpServers": {
    "github.com/mendableai/firecrawl-mcp-server": {
      "command": "C:\\Users\\chris\\AppData\\Roaming\\npm\\npx.cmd",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "YOUR_API_KEY_HERE"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 3. Resolving NPX Module Resolution Issues

After updating to use the full path to `npx.cmd`, we encountered a new error:
```
Error: Cannot find module 'C:\Users\chris\AppData\Roaming\npm\node_modules\npm\bin\npx-cli.js'
```

This indicated an issue with how `npx` was trying to find the firecrawl-mcp package. We verified that the firecrawl-mcp package was installed globally:
```
npm list -g firecrawl-mcp  # Output: firecrawl-mcp@1.3.3
```

We found the main entry point for the firecrawl-mcp package by examining its package.json:
```
dir "C:\Users\chris\AppData\Roaming\npm\node_modules\firecrawl-mcp"
type "C:\Users\chris\AppData\Roaming\npm\node_modules\firecrawl-mcp\package.json"
```

We confirmed that the script could run directly with Node.js:
```
node "C:\Users\chris\AppData\Roaming\npm\node_modules\firecrawl-mcp\dist\index.js"
```

This gave an expected error about the missing FIRECRAWL_API_KEY environment variable, confirming that the script itself worked.

## Final Solution

The ultimate solution was to bypass `npx` entirely and run the firecrawl-mcp script directly with Node.js:

```json
{
  "mcpServers": {
    "github.com/mendableai/firecrawl-mcp-server": {
      "command": "node",
      "args": ["C:\\Users\\chris\\AppData\\Roaming\\npm\\node_modules\\firecrawl-mcp\\dist\\index.js"],
      "env": {
        "FIRECRAWL_API_KEY": "YOUR_API_KEY_HERE"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## How to Apply the Fix

1. Edit the MCP settings file:
   - For Cline (VSCode extension): `c:\Users\chris\AppData\Roaming\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
   - For Claude Desktop app: `C:\Users\chris\AppData\Roaming\Claude\claude_desktop_config.json`

2. Update the configuration to use the direct Node.js approach as shown above.

3. Reload the application:
   - For Cline (VSCode extension): Press Ctrl+Shift+P, type "Developer: Reload Window" and press Enter
   - For Claude Desktop app: Close and reopen the application

4. Click "Retry Connection" in the MCP Servers panel.

## Lessons Learned

1. **JSON Syntax is Critical**: Even small syntax errors in JSON configuration files can cause the entire configuration to fail.

2. **PATH Environment Variables**: MCP servers may not have access to the same PATH environment variables as your terminal. Using absolute paths to executables is more reliable.

3. **Direct Execution**: When troubleshooting complex command chains (like using `npx` to run a package), try running the target script directly to isolate issues.

4. **Verify Each Component**: Test each part of the system independently to identify where the failure is occurring.

## Troubleshooting Tips for Future MCP Issues

1. Check the JSON syntax in your configuration files.
2. Use absolute paths to executables rather than relying on PATH.
3. Test running the MCP server script directly to see if it works.
4. Check if all required environment variables are properly set.
5. Look for error messages in the MCP Servers panel for clues about what's going wrong.

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.github.io/docs/)
- [FireCrawl MCP Server GitHub Repository](https://github.com/mendableai/firecrawl-mcp-server)
