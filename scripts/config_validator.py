#!/usr/bin/env python3
"""
Config Validator
Validates _system/config.json against schema to prevent invalid configurations
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from logger_setup import get_logger


class ConfigValidator:
    """Validate config.json structure and values"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / "_system" / "config.json"
        self.logger = get_logger(__name__, str(vault_path))

        # Define schema
        self.schema = {
            "version": {"type": str, "required": True},
            "system_name": {"type": str, "required": True},
            "created": {"type": str, "required": True},

            "brain_space_calculation": {
                "type": dict,
                "required": True,
                "fields": {
                    "mode": {
                        "type": str,
                        "required": True,
                        "allowed_values": ["daily", "file_count"]
                    },
                    "threshold": {
                        "type": int,
                        "required": True,
                        "min": 1,
                        "max": 100
                    }
                }
            },

            "batch_processing": {
                "type": dict,
                "required": True,
                "fields": {
                    "min_file_count": {
                        "type": int,
                        "required": True,
                        "min": 1,
                        "max": 50
                    },
                    "large_file_threshold_chars": {
                        "type": int,
                        "required": True,
                        "min": 1000
                    },
                    "total_batch_threshold_chars": {
                        "type": int,
                        "required": True,
                        "min": 10000
                    }
                }
            },

            "time_tracking": {
                "type": dict,
                "required": True,
                "fields": {
                    "idle_gap_minutes": {
                        "type": int,
                        "required": True,
                        "min": 1,
                        "max": 120
                    },
                    "default_session_minutes": {
                        "type": int,
                        "required": True,
                        "min": 1,
                        "max": 30
                    }
                }
            },

            "file_watcher": {
                "type": dict,
                "required": True,
                "fields": {
                    "check_interval_seconds": {
                        "type": int,
                        "required": True,
                        "min": 1,
                        "max": 300
                    },
                    "watch_path": {
                        "type": str,
                        "required": True
                    },
                    "enabled": {
                        "type": bool,
                        "required": True
                    }
                }
            },

            "taxonomy": {
                "type": dict,
                "required": True,
                "fields": {
                    "max_depth": {
                        "type": int,
                        "required": True,
                        "min": 2,
                        "max": 15
                    },
                    "flexible_depth": {
                        "type": bool,
                        "required": True
                    },
                    "discovery_mode": {
                        "type": str,
                        "required": True,
                        "allowed_values": ["data_driven", "predefined", "hybrid"]
                    }
                }
            },

            "knowledge_scoring": {
                "type": dict,
                "required": True,
                "fields": {
                    "graph_percentage_weight": {
                        "type": float,
                        "required": True,
                        "min": 0.0,
                        "max": 1.0
                    },
                    "connection_density_weight": {
                        "type": float,
                        "required": True,
                        "min": 0.0,
                        "max": 1.0
                    },
                    "time_invested_weight": {
                        "type": float,
                        "required": True,
                        "min": 0.0,
                        "max": 1.0
                    }
                }
            },

            "neo4j": {
                "type": dict,
                "required": True,
                "fields": {
                    "uri": {
                        "type": str,
                        "required": True
                    },
                    "database": {
                        "type": str,
                        "required": True
                    }
                }
            },

            "agents": {
                "type": dict,
                "required": True,
                "fields": {
                    "memory_update_agent": {
                        "type": dict,
                        "required": True,
                        "fields": {
                            "name": {"type": str, "required": True},
                            "protocol_file": {"type": str, "required": True},
                            "tools": {"type": list, "required": True}
                        }
                    },
                    "processing_pipeline_agent": {
                        "type": dict,
                        "required": True,
                        "fields": {
                            "name": {"type": str, "required": True},
                            "protocol_file": {"type": str, "required": True},
                            "tools": {"type": list, "required": True},
                            "mcp_servers": {"type": list, "required": True}
                        }
                    }
                }
            }
        }

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate config file against schema"""
        self.logger.info(f"Validating config: {self.config_path}")

        errors = []

        # Check file exists
        if not self.config_path.exists():
            errors.append(f"Config file not found: {self.config_path}")
            return False, errors

        # Load JSON
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return False, errors

        # Validate structure
        errors.extend(self._validate_structure(config, self.schema, path="root"))

        # Additional cross-field validation
        if not errors:
            errors.extend(self._validate_cross_fields(config))

        if errors:
            self.logger.error(f"Validation failed with {len(errors)} error(s)")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False, errors
        else:
            self.logger.info("Validation successful")
            return True, []

    def _validate_structure(self, config: Dict, schema: Dict, path: str) -> List[str]:
        """Recursively validate config structure"""
        errors = []

        for key, rules in schema.items():
            current_path = f"{path}.{key}"

            # Check required field
            if rules.get("required", False) and key not in config:
                errors.append(f"Missing required field: {current_path}")
                continue

            if key not in config:
                continue

            value = config[key]

            # Check type
            expected_type = rules["type"]
            if not isinstance(value, expected_type):
                errors.append(f"{current_path}: Expected {expected_type.__name__}, got {type(value).__name__}")
                continue

            # Type-specific validation
            if expected_type == int:
                if "min" in rules and value < rules["min"]:
                    errors.append(f"{current_path}: Value {value} is less than minimum {rules['min']}")
                if "max" in rules and value > rules["max"]:
                    errors.append(f"{current_path}: Value {value} exceeds maximum {rules['max']}")

            elif expected_type == float:
                if "min" in rules and value < rules["min"]:
                    errors.append(f"{current_path}: Value {value} is less than minimum {rules['min']}")
                if "max" in rules and value > rules["max"]:
                    errors.append(f"{current_path}: Value {value} exceeds maximum {rules['max']}")

            elif expected_type == str:
                if "allowed_values" in rules and value not in rules["allowed_values"]:
                    errors.append(f"{current_path}: Value '{value}' not in allowed values {rules['allowed_values']}")

            elif expected_type == dict:
                if "fields" in rules:
                    errors.extend(self._validate_structure(value, rules["fields"], current_path))

            elif expected_type == list:
                if "min_length" in rules and len(value) < rules["min_length"]:
                    errors.append(f"{current_path}: List length {len(value)} is less than minimum {rules['min_length']}")

        return errors

    def _validate_cross_fields(self, config: Dict) -> List[str]:
        """Validate cross-field constraints"""
        errors = []

        # Knowledge scoring weights must sum to 1.0
        scoring = config.get("knowledge_scoring", {})
        if scoring:
            total_weight = (
                scoring.get("graph_percentage_weight", 0) +
                scoring.get("connection_density_weight", 0) +
                scoring.get("time_invested_weight", 0)
            )

            if abs(total_weight - 1.0) > 0.001:  # Allow for float precision
                errors.append(f"knowledge_scoring weights must sum to 1.0, got {total_weight}")

        # Batch processing thresholds should be logical
        batch = config.get("batch_processing", {})
        if batch:
            large_file = batch.get("large_file_threshold_chars", 0)
            total_batch = batch.get("total_batch_threshold_chars", 0)

            if large_file > total_batch:
                errors.append(f"large_file_threshold_chars ({large_file}) should not exceed total_batch_threshold_chars ({total_batch})")

        # File watcher path should exist
        watcher = config.get("file_watcher", {})
        if watcher:
            watch_path = Path(watcher.get("watch_path", ""))
            if not watch_path.exists():
                errors.append(f"file_watcher.watch_path does not exist: {watch_path}")

        # Protocol files should exist
        agents = config.get("agents", {})
        for agent_name, agent_config in agents.items():
            protocol_file = agent_config.get("protocol_file", "")
            protocol_path = self.vault_path / protocol_file
            if not protocol_path.exists():
                errors.append(f"agents.{agent_name}.protocol_file does not exist: {protocol_path}")

        return errors

    def validate_and_fix(self) -> Tuple[bool, Dict, List[str]]:
        """Validate config and suggest fixes"""
        is_valid, errors = self.validate()

        fixes = {}
        if not is_valid:
            # Load current config
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Suggest fixes for common issues
            scoring = config.get("knowledge_scoring", {})
            if scoring:
                total_weight = (
                    scoring.get("graph_percentage_weight", 0) +
                    scoring.get("connection_density_weight", 0) +
                    scoring.get("time_invested_weight", 0)
                )

                if abs(total_weight - 1.0) > 0.001:
                    # Normalize weights
                    fixes["knowledge_scoring"] = {
                        "graph_percentage_weight": round(scoring.get("graph_percentage_weight", 0) / total_weight, 2),
                        "connection_density_weight": round(scoring.get("connection_density_weight", 0) / total_weight, 2),
                        "time_invested_weight": round(scoring.get("time_invested_weight", 0) / total_weight, 2)
                    }

        return is_valid, fixes, errors


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate config.json")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--fix", action="store_true",
                       help="Show suggested fixes for errors")

    args = parser.parse_args()

    validator = ConfigValidator(Path(args.vault))

    if args.fix:
        is_valid, fixes, errors = validator.validate_and_fix()

        print(f"\n[{'OK' if is_valid else 'ERROR'}] Config Validation")

        if not is_valid:
            print(f"\n   Found {len(errors)} error(s):")
            for error in errors:
                print(f"      - {error}")

            if fixes:
                print(f"\n   Suggested fixes:")
                print(json.dumps(fixes, indent=2))
        else:
            print("   All checks passed")

    else:
        is_valid, errors = validator.validate()

        print(f"\n[{'OK' if is_valid else 'ERROR'}] Config Validation")

        if not is_valid:
            print(f"\n   Found {len(errors)} error(s):")
            for error in errors:
                print(f"      - {error}")
            print(f"\n   Run with --fix to see suggested fixes")
        else:
            print("   All checks passed")

    print(f"\n   Config: {validator.config_path}\n")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
