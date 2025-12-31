"""CLI interface for Cascade Detector."""

import click
import json
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from cascade_detector.cli.config import get_config
from cascade_detector.core.scanner import SecretScanner
from cascade_detector.core.llm import OllamaLLM
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.agents.propagation import PropagationAgent
from cascade_detector.agents.verifier import VerifierAgent
from cascade_detector.agents.remediator import RemediatorAgent


console = Console()


@click.group()
@click.version_option()
def cli():
    """Cascade Detector - AI-Powered Secret Cascade Detection.
    
    Scans repositories for leaked secrets and traces their propagation
    through dependencies, forks, and git history.
    """
    pass


@cli.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option(
    "--config",
    type=click.Path(),
    help="Path to configuration file",
)
@click.option(
    "--depth",
    type=int,
    default=5,
    help="Maximum depth for dependency/fork traversal",
)
@click.option(
    "--entropy-threshold",
    type=float,
    default=7.5,
    help="Entropy threshold for secret flagging",
)
@click.option(
    "--output",
    type=click.Path(),
    default="./reports",
    help="Output directory for reports",
)
@click.option(
    "--format",
    multiple=True,
    default=["json", "html"],
    help="Output formats (json, html, mermaid)",
)
@click.option(
    "--no-llm",
    is_flag=True,
    help="Disable LLM-based analysis",
)
def scan(
    repo_path: str,
    config: Optional[str],
    depth: int,
    entropy_threshold: float,
    output: str,
    format: tuple,
    no_llm: bool,
):
    """Scan a repository for secrets.
    
    Example:
        cascade-detector scan /path/to/repo --depth 5
        cascade-detector scan https://github.com/user/repo
    """
    # Load configuration
    cfg = get_config(config)
    
    console.print("[bold cyan]🔍 Cascade Detector - Repository Scanner[/]")
    console.print(f"Repository: {repo_path}")
    console.print(f"Output: {output}")
    
    # Create output directory
    Path(output).mkdir(parents=True, exist_ok=True)
    
    # Initialize LLM
    use_llm = not no_llm and cfg.get("agents.discovery.llm_analysis", True)
    llm = None
    if use_llm:
        try:
            llm = OllamaLLM(
                model=cfg.get("llm.model", "mistral"),
                base_url=cfg.get("llm.base_url", "http://localhost:11434"),
            )
            if llm.check_liveness():
                console.print("[green]✓ LLM online[/]")
            else:
                console.print("[yellow]⚠ LLM offline - using pattern matching only[/]")
                llm = None
        except Exception as e:
            console.print(f"[yellow]⚠ LLM initialization failed: {e}[/]")
            llm = None
    
    # Initialize Discovery Agent
    scanner = SecretScanner(entropy_threshold=entropy_threshold)
    discovery = DiscoveryAgent(
        scanner=scanner,
        llm=llm,
        entropy_threshold=entropy_threshold,
        use_llm_analysis=llm is not None,
    )
    
    console.print("\n[bold]Scanning repository...[/]")
    
    # Read repository files
    findings = []
    try:
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common non-essential paths
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '.git', '__pycache__']]
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) < 10_000_000:  # Skip very large files
                        result = discovery.scan_blob(
                            content,
                            blob_hash=file_path,
                            file_path=file_path,
                        )
                        findings.extend(result["findings"])
                except Exception as e:
                    pass  # Skip files that can't be read
    except Exception as e:
        console.print(f"[red]Error scanning repository: {e}[/]")
        return
    
    # Generate report
    report = discovery.generate_report([{"findings": findings}])
    
    # Display summary
    table = Table(title="Scan Results Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta")
    
    table.add_row("Total Findings", str(report["summary"]["total_findings"]))
    table.add_row("High Confidence", str(report["summary"]["high_confidence"]))
    table.add_row("Medium Confidence", str(report["summary"]["medium_confidence"]))
    table.add_row("Low Confidence", str(report["summary"]["low_confidence"]))
    
    console.print(table)
    
    # Save reports
    if "json" in format:
        json_path = Path(output) / "report.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        console.print(f"\n[green]✓ JSON report saved to {json_path}[/]")
    
    console.print("[bold green]✓ Scan complete![/]")


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["json", "html", "yaml"]),
    default="json",
    help="Output format",
)
def config(format: str):
    """Display current configuration."""
    cfg = get_config()
    config_dict = cfg.to_dict()
    
    if format == "json":
        console.print(json.dumps(config_dict, indent=2))
    elif format == "yaml":
        import yaml
        console.print(yaml.dump(config_dict, default_flow_style=False))
    else:
        # HTML format
        console.print(json.dumps(config_dict, indent=2))


@cli.command()
@click.option(
    "--key",
    required=True,
    help="Configuration key (e.g., 'scanner.entropy_threshold')",
)
@click.option(
    "--value",
    required=True,
    help="Configuration value",
)
@click.option(
    "--type",
    type=click.Choice(["string", "int", "float", "bool"]),
    default="string",
    help="Value type",
)
def set_config(key: str, value: str, type: str):
    """Set configuration value."""
    cfg = get_config()
    
    # Convert value based on type
    if type == "int":
        value = int(value)
    elif type == "float":
        value = float(value)
    elif type == "bool":
        value = value.lower() in ["true", "yes", "1"]
    
    cfg.set(key, value)
    cfg.save()
    
    console.print(f"[green]✓ Configuration updated: {key}={value}[/]")


@cli.command()
def verify():
    """Verify Cascade Detector installation and dependencies."""
    console.print("[bold]Verifying Cascade Detector Installation[/]\n")
    
    checks = []
    
    # Check Python version
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append(("Python version", py_version, py_version >= "3.11"))
    
    # Check key dependencies
    deps = {
        "git": "GitPython",
        "networkx": "NetworkX",
        "langchain": "LangChain",
        "ollama": "Ollama",
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            checks.append((name, "installed", True))
        except ImportError:
            checks.append((name, "not installed", False))
    
    # Check Ollama
    try:
        llm = OllamaLLM()
        is_alive = llm.check_liveness()
        checks.append(("Ollama Server", "online" if is_alive else "offline", is_alive))
    except Exception:
        checks.append(("Ollama Server", "unavailable", False))
    
    # Display results
    table = Table(title="System Requirements")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("OK", style="green")
    
    for name, status, ok in checks:
        table.add_row(name, status, "✓" if ok else "✗")
    
    console.print(table)
    
    # Summary
    all_ok = all(ok for _, _, ok in checks)
    if all_ok:
        console.print("\n[green bold]✓ All checks passed![/]")
    else:
        console.print("\n[yellow]⚠ Some checks failed. Please review the status above.[/]")


if __name__ == "__main__":
    cli()
