#!/bin/bash
# Wrapper for SonarQube MCP server
# Checks if Docker is available before starting the server

set -e

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo "[SonarQube MCP] ERROR: Docker is not installed. SonarQube MCP requires Docker." >&2
    echo "[SonarQube MCP] Please install Docker: https://docs.docker.com/get-docker/" >&2
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "[SonarQube MCP] ERROR: Docker daemon is not running." >&2
    echo "[SonarQube MCP] Please start Docker Desktop or the Docker service." >&2
    exit 1
fi

# Check required environment variables
if [ -z "$SONARQUBE_TOKEN" ]; then
    echo "[SonarQube MCP] WARNING: SONARQUBE_TOKEN environment variable not set" >&2
fi

if [ -z "$SONARQUBE_URL" ]; then
    echo "[SonarQube MCP] WARNING: SONARQUBE_URL environment variable not set" >&2
fi

# Run the actual MCP server
docker run --rm -i \
    -e SONARQUBE_TOKEN \
    -e SONARQUBE_URL \
    -e SONARQUBE_ORG \
    mcp/sonarqube "$@"
