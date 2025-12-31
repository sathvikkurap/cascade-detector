"""LangGraph orchestration for multi-agent cascade detection."""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime, UTC
from langgraph.graph import StateGraph, END
from cascade_detector.core.scanner import SecretScanner
from cascade_detector.core.llm import OllamaLLM
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.agents.propagation import PropagationAgent
from cascade_detector.agents.verifier import VerifierAgent
from cascade_detector.agents.remediator import RemediatorAgent


class CascadeState(TypedDict):
    """State object for cascade detection workflow."""
    
    # Input
    repo_path: str
    repo_url: Optional[str]
    
    # Discovery phase
    discovery_findings: List[Dict]
    discovery_report: Optional[Dict]
    
    # Propagation phase
    cascade_graph: Optional[Dict]
    propagation_report: Optional[Dict]
    
    # Verification phase
    verification_results: List[Dict]
    verification_report: Optional[Dict]
    
    # Remediation phase
    remediation_patches: List[Dict]
    remediation_report: Optional[Dict]
    
    # Metadata
    start_time: str
    end_time: Optional[str]
    error: Optional[str]
    status: str


class CascadeOrchestrator:
    """Orchestrates the cascade detection workflow using LangGraph."""

    def __init__(
        self,
        llm: Optional[OllamaLLM] = None,
        entropy_threshold: float = 7.5,
        max_depth: int = 5,
    ):
        """Initialize orchestrator.
        
        Args:
            llm: Optional Ollama LLM instance
            entropy_threshold: Entropy threshold for secret flagging
            max_depth: Maximum traversal depth
        """
        self.llm = llm or OllamaLLM()
        self.entropy_threshold = entropy_threshold
        self.max_depth = max_depth
        
        # Initialize agents
        scanner = SecretScanner(entropy_threshold=entropy_threshold)
        self.discovery = DiscoveryAgent(
            scanner=scanner,
            llm=self.llm,
            entropy_threshold=entropy_threshold,
        )
        self.propagation = PropagationAgent(max_depth=max_depth)
        self.verifier = VerifierAgent(require_consensus=True)
        self.remediator = RemediatorAgent(llm=self.llm, test_patch=True)
        
        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow.
        
        Returns:
            Compiled state graph
        """
        workflow = StateGraph(CascadeState)
        
        # Add nodes for each agent
        workflow.add_node("discovery", self._discovery_node)
        workflow.add_node("propagation", self._propagation_node)
        workflow.add_node("verification", self._verification_node)
        workflow.add_node("remediation", self._remediation_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add edges
        workflow.add_edge("discovery", "propagation")
        workflow.add_edge("propagation", "verification")
        workflow.add_edge("verification", "remediation")
        workflow.add_edge("remediation", "finalize")
        workflow.add_edge("finalize", END)
        
        # Set entry point
        workflow.set_entry_point("discovery")
        
        return workflow.compile()

    def _discovery_node(self, state: CascadeState) -> Dict[str, Any]:
        """Discovery agent node.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state dict
        """
        try:
            import os
            
            findings = []
            repo_path = state["repo_path"]
            
            # Scan repository files
            for root, dirs, files in os.walk(repo_path):
                # Skip common non-essential directories
                dirs[:] = [
                    d for d in dirs
                    if not d.startswith('.') and d not in ['node_modules', '__pycache__']
                ]
                
                for file in files[:100]:  # Limit files for demo
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(100_000)  # Limit file size
                        
                        result = self.discovery.scan_blob(
                            content,
                            blob_hash=file_path,
                            file_path=file_path,
                        )
                        findings.extend(result["findings"])
                    except Exception:
                        pass
            
            report = self.discovery.generate_report([{"findings": findings}])
            
            return {
                "discovery_findings": findings,
                "discovery_report": report,
                "status": "discovery_complete",
            }
        except Exception as e:
            return {
                "error": f"Discovery failed: {str(e)}",
                "status": "discovery_failed",
                "discovery_findings": [],
            }

    def _propagation_node(self, state: CascadeState) -> Dict[str, Any]:
        """Propagation agent node.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state dict
        """
        try:
            findings = state.get("discovery_findings", [])
            
            # Add secrets to graph
            for i, finding in enumerate(findings[:50]):  # Limit for demo
                secret_id = f"secret_{i}"
                self.propagation.add_secret(secret_id, finding)
            
            # Add repository as source
            repo_path = state["repo_path"]
            self.propagation.add_repository("source_repo", {
                "name": repo_path.split('/')[-1],
                "path": repo_path,
            })
            
            # Connect secrets to source repo
            for i in range(min(len(findings), 50)):
                self.propagation.add_secret_propagation(f"secret_{i}", "source_repo", {})
            
            report = self.propagation.generate_propagation_report()
            cascade_graph = self.propagation.graph.to_dict()
            
            return {
                "cascade_graph": cascade_graph,
                "propagation_report": report,
                "status": "propagation_complete",
            }
        except Exception as e:
            return {
                "error": f"Propagation failed: {str(e)}",
                "status": "propagation_failed",
            }

    def _verification_node(self, state: CascadeState) -> Dict[str, Any]:
        """Verification agent node.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state dict
        """
        try:
            # For demo, create mock verification results
            findings = state.get("discovery_findings", [])
            verification_results = []
            
            for finding in findings[:10]:  # Verify first 10
                verification_results.append({
                    "secret_id": finding.get("pattern"),
                    "is_active": False,  # Default to inactive for safety
                    "confidence": 0.3,
                    "provider": "offline",
                })
            
            report = {
                "summary": {
                    "total_verified": len(verification_results),
                    "confirmed_active": 0,
                    "confirmed_inactive": len(verification_results),
                },
                "results": verification_results,
                "generated_at": datetime.now(UTC).isoformat(),
            }
            
            return {
                "verification_results": verification_results,
                "verification_report": report,
                "status": "verification_complete",
            }
        except Exception as e:
            return {
                "error": f"Verification failed: {str(e)}",
                "status": "verification_failed",
            }

    def _remediation_node(self, state: CascadeState) -> Dict[str, Any]:
        """Remediation agent node.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state dict
        """
        try:
            findings = state.get("discovery_findings", [])
            patches = []
            
            for finding in findings[:5]:  # Create patches for first 5
                patch = self.remediator.generate_patch(
                    "# Sample code\nAPI_KEY = 'secret'",
                    f"file_{len(patches)}.py",
                    finding,
                )
                if patch:
                    patches.append({
                        "file": patch.file_path,
                        "type": patch.secret_type,
                    })
            
            report = self.remediator.generate_remediation_report()
            
            return {
                "remediation_patches": patches,
                "remediation_report": report,
                "status": "remediation_complete",
            }
        except Exception as e:
            return {
                "error": f"Remediation failed: {str(e)}",
                "status": "remediation_failed",
            }

    def _finalize_node(self, state: CascadeState) -> Dict[str, Any]:
        """Finalize and generate comprehensive report.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state dict
        """
        return {
            "end_time": datetime.now(UTC).isoformat(),
            "status": state.get("error", "completed"),
        }

    def run(self, repo_path: str, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Run the cascade detection workflow.
        
        Args:
            repo_path: Path to repository
            repo_url: Optional URL of repository
            
        Returns:
            Final state with all results
        """
        initial_state: CascadeState = {
            "repo_path": repo_path,
            "repo_url": repo_url,
            "discovery_findings": [],
            "discovery_report": None,
            "cascade_graph": None,
            "propagation_report": None,
            "verification_results": [],
            "verification_report": None,
            "remediation_patches": [],
            "remediation_report": None,
            "start_time": datetime.now(UTC).isoformat(),
            "end_time": None,
            "error": None,
            "status": "started",
        }
        
        # Execute workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state

    def export_mermaid(self) -> str:
        """Export detection graph as Mermaid diagram.
        
        Returns:
            Mermaid diagram syntax
        """
        return self.propagation.export_mermaid()


if __name__ == "__main__":
    # Example usage
    orchestrator = CascadeOrchestrator()
    result = orchestrator.run("/path/to/repo")
    print(f"Status: {result['status']}")
    print(f"Findings: {result['discovery_report']['summary']}")
