#!/usr/bin/env python3
"""
MCP Server for Google Image Search
Uses SerpAPI to search for images
"""
import os
import asyncio
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.types as types
import requests
import json

# Initialize MCP server
server = Server("image-search-server")

# SerpAPI configuration (free tier: 100 searches/month)
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_images",
            description="Search for images using Google Image Search. Returns image URLs and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for images (e.g., 'coffee shop marketing campaign')",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of image results to return (default: 3, max: 10)",
                        "default": 3,
                    },
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution"""

    if name != "search_images":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    query = arguments.get("query")
    num_results = arguments.get("num_results", 3)

    if not query:
        raise ValueError("Missing required argument: query")

    # Validate num_results
    num_results = min(max(1, num_results), 10)

    # Search for images
    results = await search_images(query, num_results)

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )
    ]


async def search_images(query: str, num_results: int = 3) -> dict[str, Any]:
    """
    Search for images using SerpAPI

    Args:
        query: Search query string
        num_results: Number of results to return

    Returns:
        Dictionary with search results
    """

    # If no API key, use fallback Unsplash images
    if not SERPAPI_KEY:
        return await search_unsplash_fallback(query, num_results)

    try:
        # Call SerpAPI
        params = {
            "engine": "google_images",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results,
            "safe": "active",  # Safe search
        }

        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract image results
        images = []
        for idx, img in enumerate(data.get("images_results", [])[:num_results]):
            images.append({
                "position": idx + 1,
                "title": img.get("title", ""),
                "thumbnail": img.get("thumbnail", ""),
                "original": img.get("original", ""),
                "source": img.get("source", ""),
                "link": img.get("link", ""),
            })

        return {
            "query": query,
            "num_results": len(images),
            "images": images,
            "source": "serpapi"
        }

    except Exception as e:
        # Fallback to Unsplash if SerpAPI fails
        return await search_unsplash_fallback(query, num_results)


async def search_unsplash_fallback(query: str, num_results: int = 3) -> dict[str, Any]:
    """
    Fallback: Use Unsplash Source API (no key required)
    Returns random relevant images based on query keywords
    """

    # Extract keywords from query
    keywords = query.lower().replace("marketing", "").replace("campaign", "").strip()
    keywords = keywords.replace(" ", ",")

    # Unsplash provides random images by keyword
    images = []
    for i in range(min(num_results, 3)):
        # Different sizes for variety
        width = 800
        height = 600

        images.append({
            "position": i + 1,
            "title": f"Image for: {query}",
            "thumbnail": f"https://source.unsplash.com/400x300/?{keywords}&sig={i}",
            "original": f"https://source.unsplash.com/{width}x{height}/?{keywords}&sig={i}",
            "source": "Unsplash",
            "link": f"https://source.unsplash.com/{width}x{height}/?{keywords}&sig={i}",
        })

    return {
        "query": query,
        "num_results": len(images),
        "images": images,
        "source": "unsplash_fallback",
        "note": "Using Unsplash fallback. Set SERPAPI_KEY for Google Image Search."
    }


async def main():
    """Run the MCP server"""
    import sys

    # Get API key from environment
    global SERPAPI_KEY
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

    if not SERPAPI_KEY:
        # Print to stderr to avoid breaking JSON-RPC on stdout
        print("WARNING: SERPAPI_KEY not set. Using Unsplash fallback images.", file=sys.stderr, flush=True)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="image-search-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
