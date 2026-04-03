# Knowledge Graph JSON Schema

This document describes the complete JSON schema for the Knowledge Graph file.

## File Location

```
docs/specs/[ID-feature]/knowledge-graph.json
```

## Complete Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Knowledge Graph",
  "description": "Persistent storage for codebase analysis discoveries",
  "type": "object",
  "required": ["metadata"],
  "properties": {
    "metadata": {
      "type": "object",
      "description": "Metadata about the knowledge graph",
      "required": ["spec_id", "created_at", "updated_at", "version"],
      "properties": {
        "spec_id": {
          "type": "string",
          "description": "Specification identifier (e.g., '001-hotel-search-aggregation')"
        },
        "feature_name": {
          "type": "string",
          "description": "Feature name in kebab-case"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when KG was created"
        },
        "updated_at": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when KG was last updated"
        },
        "version": {
          "type": "string",
          "description": "Semantic version of the KG format (e.g., '1.0.0')"
        },
        "analysis_sources": {
          "type": "array",
          "description": "List of agents/sources that contributed to this KG",
          "items": {
            "type": "object",
            "properties": {
              "agent": {
                "type": "string",
                "description": "Agent name (e.g., 'general-code-explorer')"
              },
              "timestamp": {
                "type": "string",
                "format": "date-time"
              },
              "focus": {
                "type": "string",
                "description": "What the agent analyzed (e.g., 'similar features')"
              }
            }
          }
        }
      }
    },

    "codebase_context": {
      "type": "object",
      "description": "High-level context about the codebase",
      "properties": {
        "project_structure": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["layered", "modular", "hexagonal", "clean"],
              "description": "Architecture type"
            },
            "root_directories": {
              "type": "array",
              "items": { "type": "string" }
            },
            "build_system": {
              "type": "string",
              "enum": ["maven", "gradle", "npm", "pip", "composer"]
            },
            "test_framework": {
              "type": "string"
            }
          }
        },
        "technology_stack": {
          "type": "object",
          "properties": {
            "language": {
              "type": "string",
              "enum": ["java", "typescript", "python", "php", "javascript"]
            },
            "framework": {
              "type": "string"
            },
            "version": {
              "type": "string"
            },
            "dependencies": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": { "type": "string" },
                  "version": { "type": "string" }
                }
              }
            }
          }
        }
      }
    },

    "patterns": {
      "type": "object",
      "properties": {
        "architectural": {
          "type": "array",
          "description": "Architectural patterns found in codebase",
          "items": {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
              "id": {
                "type": "string",
                "description": "Unique pattern identifier (e.g., 'pat-001')"
              },
              "name": {
                "type": "string",
                "description": "Pattern name (e.g., 'Repository Pattern')"
              },
              "description": {
                "type": "string"
              },
              "files": {
                "type": "array",
                "items": { "type": "string" },
                "description": "Glob patterns for files using this pattern"
              },
              "convention": {
                "type": "string",
                "description": "How the pattern is implemented in this codebase"
              },
              "examples": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "file": { "type": "string" },
                    "line": { "type": "integer" },
                    "snippet": { "type": "string" }
                  }
                }
              }
            }
          }
        },
        "conventions": {
          "type": "array",
          "description": "Coding conventions and standards",
          "items": {
            "type": "object",
            "required": ["id", "category", "rule"],
            "properties": {
              "id": {
                "type": "string"
              },
              "category": {
                "type": "string",
                "enum": ["naming", "testing", "documentation", "error-handling"]
              },
              "rule": {
                "type": "string",
                "description": "The convention rule"
              },
              "examples": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    },

    "components": {
      "type": "object",
      "properties": {
        "controllers": {
          "type": "array",
          "items": { "$ref": "#/definitions/component" }
        },
        "services": {
          "type": "array",
          "items": { "$ref": "#/definitions/component" }
        },
        "repositories": {
          "type": "array",
          "items": { "$ref": "#/definitions/component" }
        },
        "entities": {
          "type": "array",
          "items": { "$ref": "#/definitions/component" }
        },
        "dtos": {
          "type": "array",
          "items": { "$ref": "#/definitions/component" }
        }
      }
    },

    "provides": {
      "type": "array",
      "description": "What tasks provide after implementation (for contract validation)",
      "items": {
        "type": "object",
        "required": ["task_id", "file", "symbols", "type"],
        "properties": {
          "task_id": {
            "type": "string",
            "description": "Task identifier (e.g., 'TASK-001')"
          },
          "file": {
            "type": "string",
            "description": "Full file path relative to project root"
          },
          "symbols": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Symbols (classes, interfaces, functions) provided by this file"
          },
          "type": {
            "type": "string",
            "enum": ["entity", "value-object", "service", "repository", "controller", "function", "module", "class", "interface", "dto"],
            "description": "Type of component"
          },
          "implemented_at": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp when this was implemented"
          }
        }
      }
    },

    "apis": {
      "type": "object",
      "properties": {
        "internal": {
          "type": "array",
          "description": "Internal REST/API endpoints",
          "items": {
            "type": "object",
            "required": ["id", "path", "method"],
            "properties": {
              "id": { "type": "string" },
              "name": { "type": "string" },
              "type": { "type": "string", "enum": ["rest", "graphql", "grpc"] },
              "path": { "type": "string" },
              "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
              },
              "controller": { "type": "string" },
              "line": { "type": "integer" },
              "parameters": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "name": { "type": "string" },
                    "type": { "type": "string" },
                    "required": { "type": "boolean" }
                  }
                }
              },
              "response": { "type": "string" },
              "errors": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "status": { "type": "integer" },
                    "condition": { "type": "string" }
                  }
                }
              }
            }
          }
        },
        "external": {
          "type": "array",
          "description": "External APIs/integrations",
          "items": {
            "type": "object",
            "required": ["id", "base_url"],
            "properties": {
              "id": { "type": "string" },
              "name": { "type": "string" },
              "type": { "type": "string", "enum": ["rest", "soap", "graphql"] },
              "base_url": { "type": "string" },
              "authentication": { "type": "string" },
              "endpoints": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "id": { "type": "string" },
                    "method": { "type": "string" },
                    "path": { "type": "string" },
                    "purpose": { "type": "string" },
                    "used_by": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    },

    "integration_points": {
      "type": "array",
      "description": "Integration points with external systems",
      "items": {
        "type": "object",
        "required": ["id", "name", "type"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "type": {
            "type": "string",
            "enum": ["database", "cache", "message-queue", "external-api"]
          },
          "technology": { "type": "string" },
          "purpose": { "type": "string" },
          "configuration": { "type": "string" },
          "used_by_components": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },

    "testing": {
      "type": "object",
      "properties": {
        "framework": { "type": "string" },
        "structure": { "type": "string" },
        "conventions": {
          "type": "array",
          "items": { "type": "string" }
        },
        "examples": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "file": { "type": "string" },
              "tests": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    },

    "architecture_decisions": {
      "type": "object",
      "description": "Key architectural decisions with rationale",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "decision": { "type": "string" },
          "rationale": { "type": "string" },
          "alternatives_considered": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },

    "validation_rules": {
      "type": "array",
      "description": "Custom validation rules for this codebase",
      "items": {
        "type": "object",
        "required": ["id", "rule", "severity"],
        "properties": {
          "id": { "type": "string" },
          "rule": { "type": "string" },
          "checker": { "type": "string" },
          "severity": {
            "type": "string",
            "enum": ["error", "warning", "info"]
          }
        }
      }
    },

    "quality_metrics": {
      "type": "object",
      "properties": {
        "code_coverage": { "type": "string" },
        "test_count": { "type": "integer" },
        "component_count": { "type": "integer" },
        "last_analysis": {
          "type": "string",
          "format": "date-time"
        }
      }
    }
  },

  "definitions": {
    "component": {
      "type": "object",
      "required": ["id", "name", "location", "type"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique component identifier (e.g., 'comp-ctrl-001')"
        },
        "name": {
          "type": "string",
          "description": "Component class/file name"
        },
        "location": {
          "type": "string",
          "description": "Full file path relative to project root"
        },
        "type": {
          "type": "string",
          "enum": ["controller", "service", "repository", "entity", "dto", "config"]
        },
        "responsibilities": {
          "type": "array",
          "items": { "type": "string" }
        },
        "endpoints": {
          "type": "array",
          "description": "For controllers: list of endpoints",
          "items": {
            "type": "object",
            "properties": {
              "method": { "type": "string" },
              "path": { "type": "string" },
              "line": { "type": "integer" },
              "description": { "type": "string" }
            }
          }
        },
        "methods": {
          "type": "array",
          "description": "For services: list of key methods",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "line": { "type": "integer" },
              "description": { "type": "string" },
              "returns": { "type": "string" }
            }
          }
        },
        "dependencies": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Component names this component depends on"
        },
        "uses_components": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Component IDs this component uses"
        }
      }
    }
  }
}
```

## Example: Complete Knowledge Graph

See the complete example in the architect's output (available in the command history). Here's a minimal example:

```json
{
  "metadata": {
    "spec_id": "001-hotel-search-aggregation",
    "feature_name": "hotel-search-aggregation",
    "created_at": "2026-03-14T10:30:00Z",
    "updated_at": "2026-03-14T15:45:00Z",
    "version": "1.0.0",
    "analysis_sources": [
      {
        "agent": "general-code-explorer",
        "timestamp": "2026-03-14T10:30:00Z",
        "focus": "similar features analysis"
      }
    ]
  },
  "patterns": {
    "architectural": [
      {
        "id": "pat-001",
        "name": "Repository Pattern",
        "convention": "All repositories extend JpaRepository",
        "files": ["src/main/java/**/repository/*Repository.java"]
      }
    ],
    "conventions": [
      {
        "id": "conv-001",
        "category": "naming",
        "rule": "Controller classes end with 'Controller'"
      }
    ]
  },
  "components": {
    "controllers": [
      {
        "id": "comp-ctrl-001",
        "name": "HotelController",
        "location": "src/main/java/com/example/hotel/controller/HotelController.java",
        "type": "controller"
      }
    ],
    "services": [],
    "repositories": [],
    "entities": [],
    "dtos": []
  },
  "apis": {
    "internal": [],
    "external": []
  }
}
```

## Schema Evolution

This schema may evolve over time. The `version` field in metadata tracks the format version.

**Versioning rules:**
- **MAJOR**: Breaking changes to schema structure
- **MINOR**: New optional fields added
- **PATCH**: Bug fixes to documentation

When evolving the schema:
1. Update the `version` field
2. Document changes in CHANGELOG
3. Provide migration path for existing KGs
4. Maintain backwards compatibility when possible
