import os

def mapper(repo_path):
    file_list = []
    for abs_dirpath, dirnames, filenames in os.walk(repo_path):
        if ".git" in dirnames:
            del dirnames[dirnames.index(".git")]
        path = os.path.relpath(abs_dirpath, repo_path)
        if path.count("/") != 2:
            continue
        for f in filenames:
            if os.path.splitext(f)[1] == ".tex":
                file_list.append(os.path.join(abs_dirpath, f))
    
    detailed_file_list = {}
    for filepath in file_list:
        relpath = os.path.relpath(filepath, repo_path)
        components = relpath.split("/")
        experiment = components[1]
        type = components[2]
        filename = components[3]
        if "vorbereitung" in type:
            who = ""
            suffix = ""
            if "gregor" in filename:
                who = "gregor"
            elif "sven" in filename:
                who = "sven"
            else:
                continue
            if "korre" in filename or "err" in filename:
                suffix="-errata"
            detailed_file_list[filepath] = os.path.join(components[0], "%s-vorbereitung-%s%s.pdf"%(experiment, who, suffix))
        else:
            suffix = "auswertung"
            if "aus" not in filename and "kor" not in filename:
                continue
            elif "kor" in filename:
                suffix = "errata"
            detailed_file_list[filepath] = os.path.join(components[0], "%s-%s.pdf"%(experiment, suffix))
    return detailed_file_list