import typer
import requests
from rich.console import Console
from rich.table import Table
import os
import json

app = typer.Typer(help="ZeroTrust Agents CLI Tool")
console = Console()

API_URL = os.getenv("ZTA_API_URL", "http://localhost:8001")
API_KEY = os.getenv("ZTA_API_KEY", "sk-default")
TENANT_ID = os.getenv("ZTA_TENANT_ID", "default")

def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "x-tenant-id": TENANT_ID
    }

@app.command()
def logs(limit: int = typer.Option(50, help="Number of logs to fetch")):
    """Tail recent audit logs from the firewall."""
    with console.status("Fetching logs..."):
        try:
            resp = requests.get(f"{API_URL}/logs/?limit={limit}", headers=get_headers())
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            console.print(f"[red]Error fetching logs: {e}[/red]")
            raise typer.Exit(1)
            
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Time", style="dim", width=20)
    table.add_column("Agent ID")
    table.add_column("Tool Name")
    table.add_column("Status")
    
    for log in data:
        status = "[green]Allowed[/green]" if log.get("allowed") else "[red]Denied[/red]"
        table.add_row(
            log.get("timestamp", "")[:19].replace("T", " "),
            log.get("agent_id", "Unknown"),
            log.get("tool_name", "Unknown"),
            status
        )
        
    console.print(table)

@app.command()
def sync(file: str = typer.Argument(..., help="Path to YAML policy file")):
    """Sync policies from a YAML file to the control plane."""
    if not os.path.exists(file):
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
        
    with console.status(f"Syncing policies from {file}..."):
        try:
            with open(file, 'rb') as f:
                files = {'file': (os.path.basename(file), f, 'application/x-yaml')}
                resp = requests.post(f"{API_URL}/policies/sync-yaml", headers=get_headers(), files=files)
            resp.raise_for_status()
            data = resp.json()
            console.print(f"[green]Successfully synced {data.get('synced', 0)} policies![/green]")
        except requests.RequestException as e:
            console.print(f"[red]Error syncing policies: {e}[/red]")
            if e.response:
                console.print(e.response.text)
            raise typer.Exit(1)

if __name__ == "__main__":
    app()
