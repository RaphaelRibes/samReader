import subprocess, os, shutil

def make_chromosome(file_name, results, path):
    latex_content = open(f"{os.path.dirname(os.path.abspath(__file__))}/chromosome.tex", "r").read()
    latex_content = latex_content.replace("\r\n", "\n")

    data_dict = {
        "M": results["M"],
        "I": results["I"],
        "D": results["D"],
        "S": results["S"],
        "H": results["H"],
        "N": results["N"],
        "P": results["P"],
        "X": results["X"],
        "E": results["="],
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

    print(os.path.join(path, f"{file_name}.tex"))
    with open(os.path.join(path, f"{file_name}.tex"), "w") as file:
        file.write(latex_content)

    # Compile the .tex file to a .pdf file

    with open(os.devnull, 'w') as devnull:
        subprocess.run(["latexmk", "-silent", f"--output-directory={path}/temp", "-pdf", os.path.join(path, f"{file_name}.tex")],
                       stdout=devnull, stderr=devnull)

    # Move the .pdf file to the main directory
    shutil.move(os.path.join(path, 'temp', f"{file_name}.pdf"), os.path.join(path, f"{file_name}.pdf"))


def summarize(fileName, results, path, verbose=False, ask_to_open=False):
    make_chromosome(fileName, results, path)
    # Remove the temp folder
    os.remove(f"{path}/{fileName}.tex")
    shutil.rmtree(f"{path}/temp")

    if verbose:
        print(f'\nThe results are available in the file {path}/{fileName}.pdf')

    if ask_to_open:
        yn = input("Do you want to open the file ? (y/n) ")
        if yn == "y":
            subprocess.run(["xdg-open", f"{path}/{fileName}.pdf"])
        else:
            pass
