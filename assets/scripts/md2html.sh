#!/bin/bash
# ================================================================
# File: md2html.sh
# Author: Xi Hu
# Description:
#   Convert Markdown (.md) to HTML with custom CSS and JS.
#   This script uses pandoc to generate a styled HTML file for
#   documentation or tutorials.
# ================================================================

# ----------------------------
# Function: show_help
# ----------------------------
show_help() {
    echo ""
    echo "📘 Usage:"
    echo "  bash md2html.sh <prefix> <title>"
    echo ""
    echo "📄 Description:"
    echo "  Converts '<prefix>.md' to '<prefix>.html' with the specified title."
    echo "  The output HTML will include custom CSS and a copy-button script."
    echo ""
    echo "🧩 Example:"
    echo "  bash build_html.sh tutorial 'ROC Curve Analysis Tutorial'"
    echo ""
    echo "⚙️ Required files:"
    echo "  ../../css/github-plus.css" # relative path
    echo "  ../../css/code-theme.css"
    echo "  ../../js/copy.js"
    echo ""
    echo "💡 Tips:"
    echo "  • Make sure pandoc is installed (check with 'pandoc -v')."
    echo "  • The title can include spaces — enclose it in quotes."
    echo ""
    exit 0
}

# ----------------------------
# Check arguments
# ----------------------------
if [[ "$1" == "-h" || "$1" == "--help" || "$#" -lt 2 ]]; then
    show_help
fi

# ----------------------------
# Assign parameters
# ----------------------------
prefix="$1"
title="$2"

# ----------------------------
# Check if input file exists
# ----------------------------
input="${prefix}.md"
output="${prefix}.html"

if [[ ! -f "$input" ]]; then
    echo "❌ Error: Input file '${input}' not found."
    echo "Run 'bash build_html.sh --help' for usage."
    exit 1
fi

# ----------------------------
# Run Pandoc Conversion
# ----------------------------
echo "🚀 Converting '${input}' → '${output}' ..."
pandoc "$input" \
    --metadata title="$title" \
    --include-in-header=../../../_layouts/base.html \
    -s --mathjax -f markdown+fenced_code_blocks+pipe_tables+backtick_code_blocks \
    -c ../../css/github-plus.css \
    -c ../../css/code-theme.css \
    -c ../../css/github-markdown.css \
    --include-after-body ../../js/copy.js \
    -o "$output"

# ----------------------------
# Check success
# ----------------------------
if [[ $? -eq 0 ]]; then
    echo "✅ Successfully generated: ${output}"
else
    echo "❌ Conversion failed."
    exit 1
fi