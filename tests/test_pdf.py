"""Exercise Ghostscript PDF generation and rendering as the Moodle runtime user."""
import os
import subprocess

image = os.environ.get("TEST_IMAGE", "ghcr.io/innovatics-lab/moodle:5.3.1-r2")
script = r"""
set -eu
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
printf '%s\n' '%!PS' '/Helvetica findfont 18 scalefont setfont' \
  '72 720 moveto (Moodle PDF annotation smoke test) show' 'showpage' > "$work/input.ps"
gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
  -sOutputFile="$work/output.pdf" "$work/input.ps"
gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r72 \
  -sOutputFile="$work/page-%d.png" "$work/output.pdf"
test -s "$work/output.pdf"
test -s "$work/page-1.png"
printf 'PASS: PDF generation and rendering as www-data; Ghostscript '
gs --version
"""
subprocess.run([
    "docker", "run", "--rm", "--network", "none", "--user", "www-data",
    "--entrypoint", "sh", image, "-ec", script,
], check=True, timeout=120)
