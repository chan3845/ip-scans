import ipaddress
import concurrent.futures
from ping3 import ping
import typer
from rich import print

app = typer.Typer()

def is_alive(ip: str) -> str:
    try:
        response = ping(ip, timeout=0.5)
        return ip if response else None
    except Exception:
        return None

def scan_subnet(subnet: str):
    print(f"[cyan]Scanning subnet:[/cyan] {subnet}")
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError:
        print(f"[red]Invalid subnet: {subnet}[/red]")
        return []

    ips = [str(ip) for ip in network.hosts()]
    alive_ips = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(is_alive, ips)
        for ip in results:
            if ip:
                alive_ips.append(ip)

    print(f"[green]Alive IPs in {subnet} ({len(alive_ips)}):[/green]")
    for ip in alive_ips:
        print(f" - {ip}")
    return alive_ips

@app.command()
def scan(subnets: list[str] = typer.Argument(..., help="CIDR subnets to scan (e.g. 192.168.1.0/24 10.0.0.0/24)")):
    """Scan multiple subnets and show alive IPs"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(subnets)) as executor:
        executor.map(scan_subnet, subnets)

if __name__ == "__main__":
    app()


