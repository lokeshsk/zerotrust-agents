import typer
from rich.console import Console
from rich.table import Table
import os
import json
from .client import ZeroTrustAgents

app = typer.Typer(name="zta", help="ZeroTrust Agents Command Line Interface")
console = Console()

CONFIG_FILE = os.path.expanduser("~/.zta/credentials")

def get_client() -> ZeroTrustAgents:
    if not os.path.exists(CONFIG_FILE):
        console.print("[red]Not logged in. Please run `zta login <api-key>` first.[/red]")
        raise typer.Exit(code=1)
        
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        
    api_key = config.get("api_key")
    url = config.get("url", "http://localhost:8001")
    return ZeroTrustAgents(api_key=api_key, base_url=url)

@app.command()
def login(api_key: str, url: str = "http://localhost:8001"):
    """Authenticate the CLI with your ZeroTrust Agents API Key."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key, "url": url}, f)
    console.print(f"[green]Successfully logged in! Connected to {url}[/green]")

@app.command()
def config_set(key: str, value: str):
    """Set a tenant configuration value (e.g. hitl_webhook_url)."""
    client = get_client()
    try:
        client.config.set(**{key: value})
        console.print(f"[green]Successfully set {key} = {value}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to update config: {e}[/red]")

@app.command()
def sync(file: str):
    """Sync a local YAML policy file to the control plane."""
    client = get_client()
    try:
        resp = client.policies.sync(file)
        console.print(f"[green]Successfully synced {resp.get('synced', 0)} policies from {file}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to sync policies: {e}[/red]")

@app.command("audit-trail")
def audit_trail(limit: int = 20):
    """View SOC2 compliance admin audit trails."""
    client = get_client()
    try:
        trails = client.logs.get_audit_trail(limit=limit)
        table = Table("Time", "Admin", "Action", "Target")
        for t in trails:
            table.add_row(t.get("timestamp", ""), t.get("user_id", ""), t.get("action", ""), t.get("target_resource", ""))
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to fetch audit trails: {e}[/red]")

@app.command()
def logs(limit: int = 20):
    """Tail recent audit logs."""
    client = get_client()
    try:
        logs_data = client.logs.list(limit=limit)
        table = Table("Time", "Agent", "Tool", "Action", "Arguments")
        for log in logs_data:
            action = "[green]ALLOWED[/green]" if log.get("allowed") else "[red]BLOCKED[/red]"
            table.add_row(log.get("timestamp", ""), log.get("agent_id", ""), log.get("tool_name", ""), action, log.get("arguments", "")[:50] + "...")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to fetch logs: {e}[/red]")

@app.command()
def approvals():
    """List pending Human-in-the-Loop approvals."""
    client = get_client()
    try:
        apps = client.approvals.list()
        if not apps:
            console.print("[green]No pending approvals![/green]")
            return
            
        table = Table("ID", "Agent", "Tool", "Arguments")
        for app in apps:
            table.add_row(str(app.get("id")), app.get("agent_id", ""), app.get("tool_name", ""), app.get("arguments", "")[:50] + "...")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to fetch approvals: {e}[/red]")

templates_app = typer.Typer(help="Manage policy templates")
app.add_typer(templates_app, name="templates")

@templates_app.command("list")
def list_templates():
    """List available pre-built policy templates."""
    client = get_client()
    try:
        tmps = client.templates.list()
        for t in tmps:
            console.print(f"- [cyan]{t}[/cyan]")
    except Exception as e:
        console.print(f"[red]Failed to list templates: {e}[/red]")

@templates_app.command("apply")
def apply_template(name: str, agent_id: str):
    """Apply a pre-built template to an agent."""
    client = get_client()
    try:
        resp = client.templates.apply(name, agent_id)
        console.print(f"[green]Successfully applied template '{name}' to agent '{agent_id}' ({resp.get('synced', 0)} policies created).[/green]")
    except Exception as e:
        console.print(f"[red]Failed to apply template: {e}[/red]")

agents_app = typer.Typer(help="Manage agents and their configurations")
app.add_typer(agents_app, name="agents")

@agents_app.command("set-budget")
def set_agent_budget(agent_id: str, limit: int):
    """Set a hard budget limit (in cents) for a specific agent."""
    client = get_client()
    try:
        client.config.set_agent_budget(agent_id, limit)
        console.print(f"[green]Successfully set budget limit for agent '{agent_id}' to {limit} cents[/green]")
    except Exception as e:
        console.print(f"[red]Failed to set agent budget: {e}[/red]")

if __name__ == "__main__":
    app()
