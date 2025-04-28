"""
Simple Math MCP Server Example

This is a basic implementation of a math server that handles basic arithmetic operations.
To use this with the MCP client, run this script and point your MCP tool to it.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Union

import sympy


class MathOperation:
    """A class to handle math operations using sympy."""
    
    def evaluate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            Dict containing the result and steps
        """
        try:
            # Parse and evaluate the expression
            result = sympy.sympify(expression)
            
            # Format the result
            return {
                "result": str(result),
                "steps": f"Evaluated {expression} = {result}"
            }
        except Exception as e:
            return {
                "error": f"Error evaluating expression: {str(e)}"
            }


async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Process an incoming request."""
    content = request.get("content", "")
    
    # If it's a function call, use the tool directly
    if "name" in request and "arguments" in request:
        if request["name"] == "math_evaluate":
            args = json.loads(request["arguments"])
            expression = args.get("expression", "")
            math_op = MathOperation()
            return math_op.evaluate(expression)
    
    # Otherwise, try to extract an expression from the content
    math_op = MathOperation()
    return math_op.evaluate(content)


async def handle_stdin_stdout():
    """Handle stdin/stdout communication."""
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            # Parse the request
            request = json.loads(line)
            
            # Process the request
            response = await handle_request(request)
            
            # Send the response
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)


def register_tools() -> List[Dict[str, Any]]:
    """Register tools for the server."""
    return [{
        "name": "math_evaluate",
        "description": "Evaluates a mathematical expression and returns the result",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }]


async def main():
    """Main entry point for the server."""
    # Print tools registration for MCP discovery
    print(json.dumps({"tools": register_tools()}), flush=True)
    
    # Handle stdin/stdout communication
    await handle_stdin_stdout()


if __name__ == "__main__":
    asyncio.run(main()) 