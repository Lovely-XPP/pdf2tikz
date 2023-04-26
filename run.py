### -------------- Settings -------------- ###
from pdf2tikz import pdf2tikz

# inkscape path setting
inkscape_path = "/Applications/Inkscape.app/Contents/MacOS/inkscape"

# Thread Setting
thread = 16

# process setting
eps_pdf = True
pdf_svg = True
svg_tikz = True
text2path = True

# generate setting
scale = 0.015
linewidth_scale = 0.2

if __name__ == "__main__":
    run = pdf2tikz(
        inkscape_path = inkscape_path,
        eps_pdf = eps_pdf,
        pdf_svg = pdf_svg,
        svg_tikz = svg_tikz,
        text2path = text2path,
        scale = scale,
        linewidth_scale = linewidth_scale,
        thread = thread
    )
    run.run()
