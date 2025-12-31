"""Cascade Detector - AI-Powered Secret Cascade Detection."""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "Scans repositories for leaked secrets and traces propagation"

from cascade_detector.core.scanner import SecretScanner
from cascade_detector.core.llm import OllamaLLM
from cascade_detector.core.graphs import CascadeGraph
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.agents.propagation import PropagationAgent
from cascade_detector.agents.verifier import VerifierAgent
from cascade_detector.agents.remediator import RemediatorAgent

__all__ = [
    "SecretScanner",
    "OllamaLLM",
    "CascadeGraph",
    "DiscoveryAgent",
    "PropagationAgent",
    "VerifierAgent",
    "RemediatorAgent",
]
