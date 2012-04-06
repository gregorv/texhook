#!/usr/bin/env python

import sys, os, random, shutil, traceback, subprocess, shlex
from ConfigParser import ConfigParser

class LatexException(Exception):
    pass

def upToDate(filepath):
    path,filename = os.path.split(filepath)
    texfile = os.path.splitext(filename)[0]
    pdfpath = os.path.join(path, texfile+".pdf")
    if not os.path.exists(pdfpath):
        return False
    if os.path.getmtime(pdfpath) < os.path.getmtime(filepath):
        return False
    return True

def compileFile(filepath):
    path,filename = os.path.split(filepath)
    texfile = os.path.splitext(filename)[0]
    pdfpath = os.path.join(path, texfile+".pdf")
    command = "cd \"%s\"; pdflatex -halt-on-error \"%s\"" % (path, texfile)
    pdflatex = subprocess.Popen(command,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = pdflatex.communicate()[0]
    retcode = pdflatex.returncode
    if retcode == 1:
        raise LatexException('\n'.join(output.splitlines()[-15:-2]))
    return output

if __name__ == "__main__":
    config = ConfigParser()
    try:
        config.read("gen.cfg")
    except Exception, e:
        print "Cannot read configuration"
        traceback.print_exc()
        sys.exit(1)
    detailed_file_list = {}
    
    cwd = os.getcwd()
    os.chdir(os.path.abspath(config.get("texhook", "repo_dir")))
    # Reset the git repository and make sure it is up to date
    # Ignore leaking of FDs
    subprocess.call(shlex.split("git reset --hard"), stdout=open("/dev/null", "w"))
    subprocess.call(shlex.split("git pull --rebase"), stdout=open("/dev/null", "w"))
    os.chdir(cwd)
    
    
    # first, search for files automatically if possible
    try:
        mapper_mod = __import__(config.get("texhook", "automatic_tex2pdf_mapping_module"))
        detailed_file_list = mapper_mod.mapper(config.get("texhook", "repo_dir"))
    except Exception, e:
        print "Automatically discovering files failed!"
        traceback.print_exc()
    
    if os.path.exists(config.get("texhook", "manual_tex2pdf_mapping")):
        # apply manual mapping
        try:
            mapper = ConfigParser()
            mapper.read(config.get("texhook", "manual_tex2pdf_mapping"))
            detailed_file_list.update(dict(mapper.items("mapping")))
        except Exception, e:
            print "Applying manual config failed"
            traceback.print_exc()
    else:
        print "No manual mapping."
    
    if len(detailed_file_list) == 0:
        print "No tex-files found. Maybe config is invalid?"
        sys.exit(1)

    # Compile latex documents and copy to publish directory
    for path,target in detailed_file_list.iteritems():
        try:
            build_target = os.path.splitext(path)[0]+".pdf"
            publish_target = os.path.join(config.get("texhook", "publish_dir"), target)
            try:
                os.makedirs(os.path.dirname(publish_target))
                print "Created target directory"
            except os.error:
                pass
            if not upToDate(path):
                print "Rebuild", target, "...", 
                sys.stdout.flush()
                output = compileFile(path)
                if "undefined references" in output or "Label(s) may have changed" in output or "Rerun" in output:
                    print "reference re-rebuild ...",
                    sys.stdout.flush()
                    output = compileFile(path)
                print "done"
                sys.stdout.flush()
                if "undefined references" in output:
                    print "WARNING: There were undefined references"
                if not os.path.exists(build_target):
                    print "WARNING: No output created!"
                    continue
                shutil.copy(build_target, publish_target)
                sys.stdout.flush()
            else:
                #print build_target, publish_target
                if not os.path.exists(publish_target):
                    print "Copy file", target, "to publishing directory"
                    shutil.copy(build_target, publish_target)
                elif os.path.getmtime(publish_target) < os.path.getmtime(build_target):
                    print "Copy newer version of", target, "to publishing directory"
                    shutil.copy(build_target, publish_target)
        except LatexException, e:
            print "Failed building", target, "\n", str(e)
        except Exception, e:
            print "Failed building", target
            traceback.print_exc()
