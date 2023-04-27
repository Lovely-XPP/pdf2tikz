from tikz_export import convert_svg
import multiprocessing
import threading
import os, sys

TEMPLATE = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{tikz}
\usepackage{capt-of}

\begin{document}
"""

class pdf2tikz():
    def __init__(self, 
                 inkscape_path: str, 
                 eps_pdf: bool = True, 
                 pdf_svg: bool = True,
                 svg_tikz: bool = True,
                 text2path: bool = True,
                 scale: float = 1,
                 linewidth_scale: float = 1,
                 codeoutput: str = "standalone",
                 combine_setting: dict = {},
                 thread: int = 1):
        # init var
        self.inkscape_path = inkscape_path
        self.eps_pdf = eps_pdf
        self.pdf_svg = pdf_svg
        self.svg_tikz = svg_tikz
        self.text2path = text2path
        self.scale = scale
        self.linewidth_scale = linewidth_scale
        self.codeoutput = codeoutput
        self.thread = thread
        self.eps_folder = os.path.join(sys.path[0], 'eps')
        self.pdf_folder = os.path.join(sys.path[0], 'pdf')
        self.svg_folder = os.path.join(sys.path[0], 'svg')
        self.tikz_folder = os.path.join(sys.path[0], 'tikz')
        self.outfiles = []
        self.error_svg = []
        self.combine_setting = {
            "enable": False,
            "fig_env": False
        }
        keys = self.combine_setting.keys()
        for key in combine_setting.keys():
            if key in keys:
                self.combine_setting[key] = combine_setting[key]


        print("[Info] Start")
        # mkdir
        if not os.path.exists(self.eps_folder):
            os.makedirs(self.eps_folder)
        if not os.path.exists(self.pdf_folder):
            os.makedirs(self.pdf_folder)
        if not os.path.exists(self.svg_folder):
            os.makedirs(self.svg_folder)
        if not os.path.exists(self.tikz_folder):
            os.makedirs(self.tikz_folder)


    ''' eps -> pdf'''
    def eps2pdf(self):
        print("\n[Info] EPS -> PDF")
        origin_files = []
        save_files = []
        for info in os.walk(self.eps_folder):
            path = info[0]
            files = info[2]
            save_path = self.pdf_folder
            if path != self.eps_folder:
                subpath = path.split(self.eps_folder)[1].strip("/").strip("\\")
                save_path = os.path.join(self.pdf_folder, subpath)
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
            for file in files:
                if os.path.splitext(file)[1] != ".eps":
                    continue
                file_name = os.path.splitext(file)[0]
                origin_files.append(os.path.join(path, file))
                save_files.append(os.path.join(save_path, f"{file_name}.pdf"))
        for i in range(self.thread):
            exec(f"thread{i} = multiprocessing.Process(target=self.thread_eps2pdf, args=(origin_files, save_files, i, self.thread))")
        for i in range(self.thread):
            exec(f"thread{i}.start()")
        for i in range(self.thread):
            exec(f"thread{i}.join()")


    ''' pdf -> svg'''
    def pdf2svg(self):
        print("\n[Info] PDF -> SVG")
        origin_files = []
        save_files = []
        for info in os.walk(self.pdf_folder):
            path = info[0]
            files = info[2]
            save_path = self.svg_folder
            if path != self.pdf_folder:
                subpath = path.split(self.pdf_folder)[1].strip("/").strip("\\")
                save_path = os.path.join(self.svg_folder, subpath)
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
            for file in files:
                if os.path.splitext(file)[1] != ".pdf":
                    continue
                file_name = os.path.splitext(file)[0]
                origin_files.append(os.path.join(path, file))
                save_files.append(os.path.join(save_path, f"{file_name}.svg"))
        for i in range(self.thread):
            exec(
                f"thread{i} = multiprocessing.Process(target=self.thread_pdf2svg, args=(origin_files, save_files, i, self.thread))")
        for i in range(self.thread):
            exec(f"thread{i}.start()")
        for i in range(self.thread):
            exec(f"thread{i}.join()")


    ''' svg -> tikz'''
    def svg2tikz(self):
        origin_files = []
        save_files = []
        print("\n[Info] SVG -> TIKZ")
        for info in os.walk(self.svg_folder):
            path = info[0]
            files = info[2]
            save_path = self.tikz_folder
            if path != self.svg_folder:
                subpath = path.split(self.svg_folder)[1].strip("/").strip("\\")
                save_path = os.path.join(self.tikz_folder, subpath)
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
            for file in files:
                if os.path.splitext(file)[1] != ".svg":
                    continue
                file_name = os.path.splitext(file)[0]
                origin_files.append(os.path.join(path, file))
                save_files.append(os.path.join(save_path, f"{file_name}.tex"))
        for i in range(self.thread):
            exec(
                f"thread{i} = threading.Thread(target=self.thread_svg2tikz, args=(origin_files, save_files, i, self.thread))")
        for i in range(self.thread):
            exec(f"thread{i}.start()")
        for i in range(self.thread):
            exec(f"thread{i}.join()")
        if len(self.error_svg) > 0:
            print("\n[ERROR] Fail Files:")
            for error in self.error_svg:
                print(f"   {error}")

    
    ''' Generate main.tex to visualize all tikz code '''
    def combine_tikz(self):
        print("\n[Info] Generate main.tex")
        main_code = TEMPLATE
        self.outfiles.sort()
        if self.combine_setting['fig_env']:
            for idx, tikz_code in enumerate(self.outfiles):
                if idx > 0 and idx % 2 == 0:
                    main_code = main_code + r"\clearpage" + "\n\n"
                filename = os.path.split(tikz_code)[1]
                filename = os.path.splitext(filename)[0]
                main_code = main_code + "\n" + r"\begin{figure}[!htb]" + "\n"
                main_code = main_code + "\t" + r"\centering" + "\n"
                main_code = main_code + "\t" + r"\input{" + tikz_code.strip("/") + r"}" + "\n"
                main_code = main_code + "\t" + r"\captionof{figure}{" + filename.replace("_", "\_") + r"}" + "\n"
                main_code = main_code + r"\end{figure}" + "\n\n"
        else:
            for idx, tikz_code in enumerate(self.outfiles):
                filename = os.path.split(tikz_code)[1]
                filename = os.path.splitext(filename)[0]
                main_code = main_code + "\n" + r"\centerline{" + r"\input{" + tikz_code.strip("/") + r"}}" + "\n"
                main_code = main_code + r"\captionof{figure}{" + filename.replace("_", "\_") + r"}" + "\n"
                main_code = main_code + r"\vspace{5mm}" + "\n\n"
        main_code = main_code + "\n" + r"\end{document}"
        main_file = os.path.join(self.tikz_folder, "main.tex")
        with open(main_file, 'w') as f:
            f.write(main_code)


    def thread_eps2pdf(self, ori: list, dest: list, id: int, thread: int = 1) -> None:
        for idx in range(id, len(ori), thread):
            origin_file = ori[idx]
            save_file = dest[idx]
            cmd = f'epstopdf "{origin_file}" -o "{save_file}"'
            os.system(cmd)
            print(f"   {origin_file.split(self.eps_folder)[1]} \t -> \t {save_file.split(self.pdf_folder)[1]}")


    def thread_pdf2svg(self, ori: list, dest: list, id: int, thread: int = 1) -> None:
        for idx in range(id, len(ori), thread):
            origin_file = ori[idx]
            save_file = dest[idx]
            if self.text2path:
                cmd = f'{self.inkscape_path} {origin_file} -o {save_file} --pdf-poppler --actions="select-all;object-to-path"'
            else:
                cmd = f'{self.inkscape_path} {origin_file} -o {save_file} --actions="select-all;object-to-path"'
            os.system(cmd)
            print(f"   {origin_file.split(self.pdf_folder)[1]} \t -> \t {save_file.split(self.svg_folder)[1]}")


    def thread_svg2tikz(self, ori: list, dest: list, id: int, thread: int = 1) -> None:
        for idx in range(id, len(ori), thread):
            origin_file = ori[idx]
            save_file = dest[idx]
            try:
                code = convert_svg(origin_file, crop=True, wrap=True, codeoutput=self.codeoutput,
                                    returnstring=True, scale=self.scale, latexpathtype=False)
                if self.codeoutput != "codeonly":
                    code = code.split("\globalscale {", 1)
                    code_f = code[0]
                    code_a = code[1].split("}\n", 1)[1]
                    code = code_f + "\globalscale {" f"{1/self.linewidth_scale:.4f}" + "}\n" + code_a
            except:
                self.error_svg.append(origin_file.split(self.svg_folder)[1])
                print(f"   {origin_file.split(self.svg_folder)[1]} \t xx")
                continue
            if 'base64' in code:
                self.error_svg.append(origin_file.split(self.svg_folder)[1])
                print(f"   {origin_file.split(self.svg_folder)[1]} \t xx")
                continue
            with open(save_file, 'w') as f:
                f.write(code)
            self.outfiles.append(save_file.split(self.tikz_folder)[1])
            print(f"   {origin_file.split(self.svg_folder)[1]} \t -> \t {save_file.split(self.tikz_folder)[1]}")


    def run(self):
        if self.eps_pdf:
            self.eps2pdf()
        if self.pdf_svg:
            self.pdf2svg()
        if self.svg_tikz:
            self.svg2tikz()
        if self.combine_setting['enable']:
            self.combine_tikz()