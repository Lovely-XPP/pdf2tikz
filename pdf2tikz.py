from tikz_export import convert_svg
import os, sys


### -------------- Settings -------------- ###
# inkscape path setting
inkscape_path = "/Applications/Inkscape.app/Contents/MacOS/inkscape"

# process setting
eps_pdf = True
pdf_svg = True
svg_tikz = True

# generate setting
scale = 0.015
linewidth_scale = 0.1

# folder setting
eps_folder = os.path.join(sys.path[0], 'eps')
pdf_folder = os.path.join(sys.path[0], 'pdf')
svg_folder = os.path.join(sys.path[0], 'svg')
tikz_folder = os.path.join(sys.path[0], 'tikz')



### -------------- functions -------------- ###
''' mkdirs '''
def init():
    print("[Info] Start")
    if not os.path.exists(eps_folder):
        os.makedirs(eps_folder)
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    if not os.path.exists(svg_folder):
        os.makedirs(svg_folder)
    if not os.path.exists(tikz_folder):
        os.makedirs(tikz_folder)


''' eps -> pdf'''
def eps2pdf():
    print("\n[Info] EPS -> PDF")
    for info in os.walk(eps_folder):
        path = info[0]
        files = info[2]
        save_path = pdf_folder
        if path != eps_folder:
            subpath = path.split(eps_folder)[1].strip("/").strip("\\")
            save_path = os.path.join(pdf_folder, subpath)
            if not os.path.exists(save_path):
                os.mkdir(save_path)
        for file in files:
            if os.path.splitext(file)[1] != ".eps":
                continue
            file_name = os.path.splitext(file)[0]
            origin_file = os.path.join(path, file)
            save_file = os.path.join(save_path, f"{file_name}.pdf")
            cmd = f"epstopdf {origin_file} -o {save_file}"
            os.system(cmd)
            print(
                f"   {origin_file.split(eps_folder)[1]} \t -> \t {save_file.split(pdf_folder)[1]}")


''' pdf -> svg'''
def pdf2svg():
    print("\n[Info] PDF -> SVG")
    for info in os.walk(pdf_folder):
        path = info[0]
        files = info[2]
        save_path = svg_folder
        if path != pdf_folder:
            subpath = path.split(pdf_folder)[1].strip("/").strip("\\")
            save_path = os.path.join(svg_folder, subpath)
            if not os.path.exists(save_path):
                os.mkdir(save_path)
        for file in files:
            if os.path.splitext(file)[1] != ".pdf":
                continue
            file_name = os.path.splitext(file)[0]
            origin_file = os.path.join(path, file)
            save_file = os.path.join(save_path, f"{file_name}.svg")
            cmd = f'{inkscape_path} {origin_file} -o {save_file} --pdf-poppler --actions="select-all;object-to-path"'
            os.system(cmd)
            print(
                f"   {origin_file.split(pdf_folder)[1]} \t -> \t {save_file.split(svg_folder)[1]}")


''' svg -> tikz'''
def svg2tikz():
    print("\n[Info] SVG -> TIKZ")
    error_svg = []
    for info in os.walk(svg_folder):
        path = info[0]
        files = info[2]
        save_path = tikz_folder
        if path != svg_folder:
            subpath = path.split(svg_folder)[1].strip("/").strip("\\")
            save_path = os.path.join(tikz_folder, subpath)
            if not os.path.exists(save_path):
                os.mkdir(save_path)
        for file in files:
            if os.path.splitext(file)[1] != ".svg":
                continue
            file_name = os.path.splitext(file)[0]
            origin_file = os.path.join(path, file)
            save_file = os.path.join(save_path, f"{file_name}.tex")
            try:
                code = convert_svg(origin_file, crop=True, wrap=True, returnstring=True, scale=scale, latexpathtype=False)
                code = code.split("\globalscale {", 1)
                code_f = code[0]
                code_a = code[1].split("}\n", 1)[1]
                code = code_f + "\globalscale {" + f"{1/linewidth_scale:.4f}" + "}\n" + code_a
            except:
                error_svg.append(origin_file.split(svg_folder)[1])
                print(f"   {origin_file.split(svg_folder)[1]} \t xx")
                continue
            if 'base64' in code:
                error_svg.append(origin_file.split(svg_folder)[1])
                print(f"   {origin_file.split(svg_folder)[1]} \t xx")
                continue
            with open(save_file, 'w') as f:
                f.write(code)
            print(
                f"   {origin_file.split(svg_folder)[1]} \t -> \t {save_file.split(tikz_folder)[1]}")
    if len(error_svg) > 0:
        print("\n[ERROR] Fail Files:")
        for error in error_svg:
            print(f"   {error}")



if __name__ == "__main__":
    init()
    if eps_pdf:
        eps2pdf()
    if pdf_svg:
        pdf2svg()
    if svg_tikz:
        svg2tikz()
