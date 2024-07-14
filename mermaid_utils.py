import base64
from io import BytesIO

def render_mermaid(chart: str) -> str:
    # In a real-world scenario, you'd use a server-side Mermaid renderer here
    # For now, we'll just return the chart string
    return chart

def export_svg(chart: str, name: str) -> BytesIO:
    # In a real-world scenario, you'd convert the Mermaid syntax to SVG here
    # For now, we'll just return the chart string as bytes
    return BytesIO(chart.encode())

def copy_mermaid_code(chart: str) -> str:
    return chart