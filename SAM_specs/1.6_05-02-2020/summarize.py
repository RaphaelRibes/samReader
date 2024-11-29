import subprocess, os, shutil, string


def compile_latex(path, file_name, latex_content):
    with open(os.path.join(path, f"{file_name}.tex"), "w") as file:
        file.write(latex_content)

    # Compile the .tex file to a .pdf file

    # This line is just for debugging, ignore
    # subprocess.run(["latexmk", f"--output-directory={path}/temp", "-pdf", os.path.join(path, f"{file_name}.tex")])

    with open(os.devnull, 'w') as devnull:
        subprocess.run(["latexmk", "-silent", f"--output-directory={path}/temp", "-pdf", os.path.join(path, f"{file_name}.tex")],
                       stdout=devnull, stderr=devnull)

    # Move the .pdf file to the main directory
    shutil.move(os.path.join(path, 'temp', f"{file_name}.pdf"), os.path.join(path, f"{file_name}.pdf"))

def format_metric(value, nb_reads):
    """
    Format the metric value as a percentage string.

    Args:
        value (int): The sum of a specific mutation type.

    Returns:
        str: The formatted percentage string.
    """
    mid = f"{(value / nb_reads) * 100:.2f}"
    return mid + "\\%"


def make_chromosome(file_name, results, path):
    latex_content = open(f"{os.path.dirname(os.path.abspath(__file__))}/chromosome.tex", "r").read()
    latex_content = latex_content.replace("\r\n", "\n")

    nb_reads = sum([results[key] for key in ['M', 'I', 'D', 'S', 'H', 'N', 'P', 'X', '=']])

    data_dict = {
        "M": format_metric(results["M"], nb_reads),
        "I": format_metric(results["I"], nb_reads),
        "D": format_metric(results["D"], nb_reads),
        "S": format_metric(results["S"], nb_reads),
        "H": format_metric(results["H"], nb_reads),
        "N": format_metric(results["N"], nb_reads),
        "P": format_metric(results["P"], nb_reads),
        "X": format_metric(results["X"], nb_reads),
        "E": format_metric(results["="], nb_reads),
        "read_name": file_name,
        "s_partially_mapped": results["s_partially_mapped"],
        "p_partially_mapped": results["p_partially_mapped"],
        "s_unmapped": results["s_unmapped"],
        "p_unmapped": results["p_unmapped"],
        "s_mapped": results["s_mapped"],
        "p_mapped": results["p_mapped"],
        "s_total": results["s_mapped"] + results["s_partially_mapped"] + results["s_unmapped"],
        "p_total": results["p_mapped"] + results["p_partially_mapped"] + results["p_unmapped"]
    }

    latex_content = latex_content.format(**data_dict)

    compile_latex(path, file_name, latex_content)


def make_genome(file_name, results, path):
    latex_content = open(f"{os.path.dirname(os.path.abspath(__file__))}/genome.tex", "r").read()
    latex_content = latex_content.replace("\r\n", "\n")

    # show the parameters to format
    formatter = string.Formatter()
    nb_reads = sum([results[key] for key in ['M', 'I', 'D', 'S', 'H', 'N', 'P', 'X', '=']])

    data_dict = {
        "M": format_metric(results["M"], nb_reads),
        "I": format_metric(results["I"], nb_reads),
        "D": format_metric(results["D"], nb_reads),
        "S": format_metric(results["S"], nb_reads),
        "H": format_metric(results["H"], nb_reads),
        "N": format_metric(results["N"], nb_reads),
        "P": format_metric(results["P"], nb_reads),
        "X": format_metric(results["X"], nb_reads),
        "E": format_metric(results["="], nb_reads),
        "genome": file_name,
    }

    latex_content = latex_content.format(**data_dict)

    compile_latex(path, file_name, latex_content)


def summarize(file_name, results, path, verbose=False, genome=False):
    if genome:
        make_genome('genome', results, path)
        fuze_pdf(file_name, results['chromosomes'], path)

        if verbose:
            print(f'\nThe results are available in the file {path}/{file_name}.pdf')
        file_name = 'genome'
    else:
        make_chromosome(file_name, results, path)

    shutil.rmtree(f"{path}/temp")
    os.remove(f"{path}/{file_name}.tex")

def fuze_pdf(file_name, names, path):
    names = list(names)

    # This line is just for debugging, ignore
    # subprocess.run(["pdfunite", *[f"{path}/{name}.pdf" for name in names], f"{path}/{file_name}.pdf"])

    with open(os.devnull, 'w') as devnull:
        subprocess.run(["pdfunite", f"{path}/genome.pdf", *[f"{path}/{name}.pdf" for name in names], f"{path}/{file_name}.pdf"],
                       stdout=devnull, stderr=devnull)

    # Remove the individual pdf files
    names.append('genome')
    for name in names:
        os.remove(f"{path}/{name}.pdf")

if __name__ == "__main__":
    make_genome("x", "x", "x")
