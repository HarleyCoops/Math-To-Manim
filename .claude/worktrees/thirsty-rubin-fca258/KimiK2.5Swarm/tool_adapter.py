"""Tool Adapter for Kimi K2 - Converts tool calls to verbose instructions.

When Kimi K2 doesn't support tools or tools aren't enabled, this module
converts tool definitions and calls into verbose natural language instructions
that can be included in prompts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ToolAdapter:
    """
    Adapter that converts tool calls to verbose instructions.
    
    When tools aren't available, instead of calling functions, we provide
    detailed instructions in the prompt telling the model what to do.
    """

    @staticmethod
    def tool_to_instruction(tool: Dict[str, Any]) -> str:
        """
        Convert a tool definition to a verbose instruction.

        Args:
            tool: Tool definition dict with 'name', 'description', 'parameters'

        Returns:
            Natural language instruction describing what the tool does
        """
        name = tool.get("function", {}).get("name", tool.get("name", "unknown"))
        description = tool.get("function", {}).get("description", tool.get("description", ""))
        parameters = tool.get("function", {}).get("parameters", tool.get("parameters", {}))

        # Build instruction
        instruction = f"**Tool: {name}**\n"
        instruction += f"Description: {description}\n"

        if parameters:
            props = parameters.get("properties", {})
            required = parameters.get("required", [])

            if props:
                instruction += "\nParameters:\n"
                for param_name, param_info in props.items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "")
                    required_mark = " (required)" if param_name in required else " (optional)"
                    instruction += f"  - {param_name} ({param_type}){required_mark}: {param_desc}\n"

        instruction += "\nInstead of calling this tool, please provide the information "
        instruction += "or perform the action described above in your response.\n"

        return instruction

    @staticmethod
    def tools_to_instructions(tools: List[Dict[str, Any]]) -> str:
        """
        Convert multiple tool definitions to verbose instructions.

        Args:
            tools: List of tool definition dicts

        Returns:
            Combined natural language instructions
        """
        if not tools:
            return ""

        instructions = "## Available Actions (Instructions)\n\n"
        instructions += "The following actions are available. Instead of calling functions, "
        instructions += "please follow these instructions in your response:\n\n"

        for i, tool in enumerate(tools, 1):
            instructions += f"{i}. {ToolAdapter.tool_to_instruction(tool)}\n\n"

        return instructions

    @staticmethod
    def create_verbose_prompt(
        base_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_call_context: Optional[str] = None
    ) -> str:
        """
        Create a verbose prompt that includes tool instructions.

        Args:
            base_prompt: Original prompt
            tools: List of tool definitions (optional)
            tool_call_context: Context about what tool was being called (optional)

        Returns:
            Enhanced prompt with tool instructions
        """
        prompt = base_prompt

        if tool_call_context:
            prompt += f"\n\n## Context\n{tool_call_context}\n"

        if tools:
            prompt += "\n\n" + ToolAdapter.tools_to_instructions(tools)

        return prompt

    @staticmethod
    def format_tool_call_as_instruction(tool_call: Dict[str, Any]) -> str:
        """
        Format a tool call as a natural language instruction.

        Args:
            tool_call: Tool call dict with 'function' containing 'name' and 'arguments'

        Returns:
            Natural language instruction
        """
        if "function" in tool_call:
            func = tool_call["function"]
            name = func.get("name", "unknown")
            args = func.get("arguments", "{}")

            # Try to parse arguments
            try:
                import json
                args_dict = json.loads(args) if isinstance(args, str) else args
            except:
                args_dict = {}

            instruction = f"Please perform the action '{name}'"
            if args_dict:
                instruction += " with the following parameters:\n"
                for key, value in args_dict.items():
                    instruction += f"  - {key}: {value}\n"
            else:
                instruction += "."

            return instruction
        else:
            return f"Please perform the action: {tool_call.get('name', 'unknown')}"

    @staticmethod
    def convert_tool_schema_to_openai_format(tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert tool schema to OpenAI function calling format.

        Args:
            tool: Tool definition (may be in various formats)

        Returns:
            Tool in OpenAI function calling format
        """
        # If already in OpenAI format, return as-is
        if "function" in tool:
            return tool

        # Convert from other formats
        result = {
            "type": "function",
            "function": {
                "name": tool.get("name", "unknown"),
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters", {})
            }
        }

        return result

