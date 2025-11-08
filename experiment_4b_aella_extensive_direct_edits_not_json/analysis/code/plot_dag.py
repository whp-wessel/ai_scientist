#!/usr/bin/env python3
"""
Plot the conceptual DAG for the Childhood Resilience Study.

This script is deterministic and uses fixed layout coordinates so regenerated
figures match pixel-for-pixel when the same matplotlib version is used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


NODE_GROUP_COLOR = {
    "exposure": "#1f77b4",
    "outcome": "#d62728",
    "confounder": "#9467bd",
    "mediator": "#ff7f0e",
}


def build_graph() -> Tuple[Dict[str, Tuple[float, float]], Dict[str, str], Iterable[Tuple[str, str]]]:
    """Return node positions, node grouping, and directed edges."""
    positions = {
        "Childhood SES": (-1.3, 0.6),
        "Family Structure": (-1.3, 0.2),
        "Demographics": (-1.3, -0.2),
        "Support Networks": (-0.4, 0.8),
        "Adolescent Coping": (-0.4, -0.4),
        "Childhood Religious Adherence": (0.0, 0.6),
        "Parental Guidance": (0.0, 0.2),
        "Childhood Abuse": (0.0, -0.2),
        "Adult SES": (0.7, 0.6),
        "Adult Depression": (1.2, 0.6),
        "Adult Health": (1.2, 0.2),
        "Adult Self-Love": (1.2, -0.2),
    }

    groups = {
        "Childhood SES": "confounder",
        "Family Structure": "confounder",
        "Demographics": "confounder",
        "Support Networks": "mediator",
        "Adolescent Coping": "mediator",
        "Childhood Religious Adherence": "exposure",
        "Parental Guidance": "exposure",
        "Childhood Abuse": "exposure",
        "Adult SES": "mediator",
        "Adult Depression": "outcome",
        "Adult Health": "outcome",
        "Adult Self-Love": "outcome",
    }

    edges = [
        ("Childhood SES", "Childhood Religious Adherence"),
        ("Childhood SES", "Parental Guidance"),
        ("Childhood SES", "Childhood Abuse"),
        ("Childhood SES", "Adult SES"),
        ("Childhood SES", "Support Networks"),
        ("Family Structure", "Parental Guidance"),
        ("Family Structure", "Childhood Abuse"),
        ("Family Structure", "Support Networks"),
        ("Demographics", "Childhood Religious Adherence"),
        ("Demographics", "Parental Guidance"),
        ("Demographics", "Childhood Abuse"),
        ("Demographics", "Adult Depression"),
        ("Demographics", "Adult Health"),
        ("Demographics", "Adult Self-Love"),
        ("Support Networks", "Adult Depression"),
        ("Support Networks", "Adult Health"),
        ("Support Networks", "Adult Self-Love"),
        ("Adolescent Coping", "Adult Depression"),
        ("Adolescent Coping", "Adult Self-Love"),
        ("Childhood Religious Adherence", "Support Networks"),
        ("Childhood Religious Adherence", "Adolescent Coping"),
        ("Parental Guidance", "Adolescent Coping"),
        ("Childhood Abuse", "Adolescent Coping"),
        ("Childhood Abuse", "Adult Self-Love"),
        ("Adult SES", "Adult Health"),
        ("Adult SES", "Adult Depression"),
        ("Childhood Religious Adherence", "Adult Depression"),
        ("Parental Guidance", "Adult Health"),
        ("Childhood Abuse", "Adult Depression"),
    ]

    return positions, groups, edges


def render(output_png: Path, output_json: Path) -> None:
    positions, groups, edges = build_graph()

    fig, ax = plt.subplots(figsize=(9, 4), dpi=150)
    ax.axis("off")

    for start, end in edges:
        arrow = FancyArrowPatch(
            posA=positions[start],
            posB=positions[end],
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.2,
            color="#4d4d4d",
            alpha=0.85,
        )
        ax.add_patch(arrow)

    for node, (x, y) in positions.items():
        group = groups[node]
        ax.scatter(
            x,
            y,
            s=600,
            color=NODE_GROUP_COLOR[group],
            edgecolor="black",
            linewidth=0.8,
            zorder=5,
        )
        ax.text(x, y, node, ha="center", va="center", fontsize=9, color="white", wrap=True)

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", label="Exposure", markerfacecolor=NODE_GROUP_COLOR["exposure"], markersize=10, markeredgecolor="black"),
        plt.Line2D([0], [0], marker="o", color="w", label="Outcome", markerfacecolor=NODE_GROUP_COLOR["outcome"], markersize=10, markeredgecolor="black"),
        plt.Line2D([0], [0], marker="o", color="w", label="Confounder", markerfacecolor=NODE_GROUP_COLOR["confounder"], markersize=10, markeredgecolor="black"),
        plt.Line2D([0], [0], marker="o", color="w", label="Mediator/Pathway", markerfacecolor=NODE_GROUP_COLOR["mediator"], markersize=10, markeredgecolor="black"),
    ]
    ax.legend(handles=legend_handles, loc="lower center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.1))

    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    dag_spec = {
        "nodes": [{"name": name, "group": groups[name], "x": positions[name][0], "y": positions[name][1]} for name in positions],
        "edges": [{"source": s, "target": t} for s, t in edges],
    }
    output_json.write_text(json.dumps(dag_spec, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render DAG figure for PAP.")
    parser.add_argument("--output-png", default="figures/dag_design.png", type=Path, help="Path to save the PNG figure.")
    parser.add_argument("--output-json", default="figures/dag_design.json", type=Path, help="Path to save the JSON spec.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    render(args.output_png, args.output_json)


if __name__ == "__main__":
    main()
