# morse2svg.py

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))                    # tools/

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
import sys

def morse_to_svg(morse_code):
    elements = []
    for char in morse_code:
        if char in ['.', '-']:
            elements.append(char)
        elif char == ' ':
            elements.append(' ')  # Space between letters

    spacing = 0.6
    x_positions = []
    current_x = 0
    for element in elements:
        x_positions.append(current_x)
        if element == ' ':
            current_x += spacing * 2
        else:
            current_x += spacing

    x_vals = np.array(x_positions)
    y_vals = np.sin(x_vals / 3) * 0.8

    fig, ax = plt.subplots(figsize=(24, 6), facecolor='white')
    ax.set_facecolor('white')
    green = '#00FF41'

    for i, element in enumerate(elements):
        x, y = x_vals[i], y_vals[i]
        if element == '.':
            circle = patches.Circle((x, y), radius=0.1, color=green)
            ax.add_patch(circle)
        elif element == '-':
            rect = patches.FancyBboxPatch((x - 0.15, y - 0.05), 0.3, 0.1,
                                          boxstyle="round,pad=0.02", color=green)
            ax.add_patch(rect)

    ax.plot(x_vals, y_vals, color=green, linewidth=0.5, alpha=0.15)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(x_vals.min() - 1, x_vals.max() + 1)
    ax.set_ylim(y_vals.min() - 1, y_vals.max() + 1)

    svg_path = "./morse_output.svg"
    fig.savefig(svg_path, format='svg', bbox_inches='tight', transparent=True)
    plt.close(fig)
    return svg_path

def run_morse2svg_gui():
    app = QApplication(sys.argv)
    text, ok = QInputDialog.getText(None, "Enter Morse Code", "Morse Code:")
    if ok and text:
        output_path = morse_to_svg(text)
        QMessageBox.information(None, "SVG Created", f"Saved to:\n{output_path}")
