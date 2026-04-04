#!/usr/bin/env python3
"""
assemble_pdf.py
Generates a full PDF product containing:
- 1000+ AI prompts (programmatically generated)
- Simple vector illustrations and a mind map drawn with ReportLab
- Several design template pages

Usage:
  pip install -r requirements.txt
  python assemble_pdf.py

Output: product_creator_output.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import textwrap
import os

OUT_PDF = "product_creator_output.pdf"
PAGE_WIDTH, PAGE_HEIGHT = A4

# Prompt generator: builds 1000+ prompts by combining categories
categories = [
    "Living Room",
    "Kitchen",
    "Bedroom",
    "Bathroom",
    "Home Office",
    "Outdoor Patio",
    "Accessible Entryway",
    "Staircase",
    "Children's Room",
    "Senior-Friendly Space",
]
styles = [
    "Minimalist",
    "Mid-Century Modern",
    "Scandinavian",
    "Industrial",
    "Bohemian",
    "Contemporary",
    "Traditional",
    "Transitional",
    "Modern Farmhouse",
    "Coastal",
]
focuses = [
    "wheelchair accessibility",
    "universal design",
    "sensory-friendly lighting",
    "contrast color palettes for low vision",
    "non-slip flooring",
    "space planning for mobility aids",
    "noise reduction and acoustics",
    "adjustable countertop heights",
    "clear wayfinding and signage",
    "adaptive storage solutions",
]
actions = [
    "Create a detailed layout",
    "Propose a lighting plan",
    "Specify material and finish options",
    "Sketch furniture and circulation paths",
    "List adaptive hardware suggestions",
    "Provide a phased scaling plan for budget tiers",
    "Create a color palette and contrast guide",
    "Recommend smart-home accessibility features",
    "Design an inclusive furnishing list",
    "Generate a furniture shopping checklist",
]

# Compose prompts
prompts = []
for c_idx, cat in enumerate(categories):
    for s_idx, style in enumerate(styles):
        for f_idx, focus in enumerate(focuses):
            # create a few variations
            for a_idx, act in enumerate(actions[:3]):
                p = f"{act} for a {style} {cat} focusing on {focus}. Include layout notes, measurements in meters, accessibility checklist, and 3 budget tiers (basic, mid, premium)."
                prompts.append(p)
                if len(prompts) >= 1000:
                    break
            if len(prompts) >= 1000:
                break
        if len(prompts) >= 1000:
            break
    if len(prompts) >= 1000:
        break

# Add extra prompt variants to exceed 1000
extra_count = 1050 - len(prompts) if len(prompts) < 1050 else 0
for i in range(extra_count):
    prompts.append(f"Custom adaptive design prompt #{i+1}: Propose an inclusive design solution with measurable outcomes and 3 delivery timelines.")

# Simple helper to draw multi-column prompt pages
def draw_prompts_on_page(c, prompt_list, start_index):
    margin = 20 * mm
    col_gap = 8 * mm
    col_width = (PAGE_WIDTH - 2 * margin - col_gap) / 2
    x_left = margin
    x_right = margin + col_width + col_gap
    y = PAGE_HEIGHT - margin
    line_height = 8 * mm
    cur_x = x_left
    cur_y = y
    col = 0
    index = start_index
    for p in prompt_list:
        wrapped = textwrap.wrap(p, width=60)
        for line in wrapped:
            if cur_y < margin + 40 * mm:
                # new column/page
                if col == 0:
                    col = 1
                    cur_x = x_right
                    cur_y = y
                else:
                    c.showPage()
                    cur_x = x_left
                    cur_y = y
                    col = 0
            c.setFont("Helvetica", 9)
            c.drawString(cur_x, cur_y, f"{index+1}. {line}")
            cur_y -= line_height
        cur_y -= line_height / 2
        index += 1
    return index

# Draw simple vector illustration (decorative) on its own page
def draw_illustration_page(c, title, variant=0):
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 30 * mm, title)
    # draw shapes
    c.setLineWidth(1)
    cx = PAGE_WIDTH / 2
    cy = PAGE_HEIGHT / 2
    radius = 50 * mm
    for i in range(6):
        c.setStrokeColorRGB(0.1 * i, 0.2, 0.3 + 0.05 * i)
        c.circle(cx, cy - i * 6 * mm, radius - i * 6 * mm, stroke=1, fill=0)
    # decorative grid
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    for i in range(20):
        c.line(30 * mm + i * 6 * mm, 40 * mm, 30 * mm + i * 6 * mm, PAGE_HEIGHT - 40 * mm)
    c.showPage()

# Draw simple mind map
def draw_mindmap_page(c):
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 25 * mm, "Mind Map: Accessible Interior Design")
    center_x = PAGE_WIDTH / 2
    center_y = PAGE_HEIGHT / 2
    # central node
    c.setFillColorRGB(0.2, 0.5, 0.8)
    c.circle(center_x, center_y, 22 * mm, stroke=1, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(center_x, center_y - 4, "Accessibility")
    # branches
    branches = ["Layout", "Lighting", "Materials", "Furniture", "Tech", "Wayfinding"]
    angle_step = 360 / len(branches)
    import math
    for i, b in enumerate(branches):
        angle = math.radians(i * angle_step - 90)
        bx = center_x + math.cos(angle) * 80 * mm
        by = center_y + math.sin(angle) * 80 * mm
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(2)
        c.line(center_x, center_y, bx, by)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.circle(bx, by, 14 * mm, stroke=1, fill=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 10)
        c.drawCentredString(bx, by - 4, b)
    c.showPage()

# Create design template pages (simple layout blueprints)
def draw_templates(c):
    templates = ["Template: Compact Accessible Kitchen", "Template: Open Plan Living with Clear Circulation", "Template: Universal Bedroom Layout"]
    for t in templates:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(25 * mm, PAGE_HEIGHT - 25 * mm, t)
        # draw room rectangle
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(25 * mm, 50 * mm, PAGE_WIDTH - 50 * mm, PAGE_HEIGHT - 110 * mm)
        # draw furniture blocks
        c.setFillColorRGB(0.8, 0.9, 0.95)
        c.rect(40 * mm, PAGE_HEIGHT - 80 * mm, 60 * mm, 30 * mm, fill=1)
        c.rect(110 * mm, PAGE_HEIGHT - 140 * mm, 80 * mm, 50 * mm, fill=1)
        c.setFont("Helvetica", 10)
        c.drawString(42 * mm, PAGE_HEIGHT - 74 * mm, "Accessible countertop")
        c.drawString(112 * mm, PAGE_HEIGHT - 134 * mm, "Clear turning area (1500mm)")
        c.showPage()

# Scaling options page
def draw_scaling_options(c):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(25 * mm, PAGE_HEIGHT - 25 * mm, "Scaling & Delivery Options")
    c.setFont("Helvetica-Bold", 12)
    tiers = [
        ("Basic", "Checklist, single layout, basic material recommendations, 1 revision"),
        ("Mid", "Full layout, lighting plan, materials, shopping list, 2 revisions"),
        ("Premium", "Multiple layout options, 3D sketch, contractor spec, project management template, unlimited revisions (30 days)")
    ]
    y = PAGE_HEIGHT - 45 * mm
    for name, desc in tiers:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30 * mm, y, name)
        y -= 8 * mm
        c.setFont("Helvetica", 10)
        wrapped = textwrap.wrap(desc, 90)
        for line in wrapped:
            c.drawString(32 * mm, y, "- " + line)
            y -= 6 * mm
        y -= 6 * mm
    c.showPage()


def main():
    # ensure ReportLab is installed; the user should pip install -r requirements.txt
    c = canvas.Canvas(OUT_PDF, pagesize=A4)
    c.setTitle("Accessible Interior Design — Prompts & Templates")

    # cover
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 50 * mm, "Accessible Interior Design — AI Prompts & Templates")
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 60 * mm, "1000+ Prompts • Illustrations • Mind Map • Scaling Options • Design Templates")
    c.showPage()

    # illustration pages
    draw_illustration_page(c, "Illustration: Spatial Layers")
    draw_illustration_page(c, "Illustration: Circulation Paths")

    # mindmap
    draw_mindmap_page(c)

    # templates
    draw_templates(c)

    # scaling options
    draw_scaling_options(c)

    # prompts list
    # break prompts into chunks per page
    chunk_size = 120  # heuristic
    idx = 0
    total = len(prompts)
    while idx < total:
        chunk = prompts[idx: idx + chunk_size]
        idx = draw_prompts_on_page(c, chunk, idx)
    
    c.save()
    print(f"Generated {OUT_PDF} with {len(prompts)} prompts.")

if __name__ == '__main__':
    main()
