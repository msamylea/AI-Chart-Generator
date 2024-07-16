from io import BytesIO

def render_mermaid(mermaid_code: str) -> str:
    """
    Returns the Mermaid code without modification.

    Args:
        mermaid_code (str): The Mermaid code to be rendered.

    Returns:
        str: The original Mermaid code.
    """
    return mermaid_code

def export_svg(chart: str, name: str) -> BytesIO:
    # In a real-world scenario, you'd convert the Mermaid syntax to SVG here
    # For now, we'll just return the chart string as bytes
    return BytesIO(chart.encode())

def copy_mermaid_code(chart: str) -> str:
    return chart