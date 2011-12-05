#!/usr/bin/env python

import sys, os, random, shutil, traceback, subprocess

PUBLISH_PATH = "/var/www/htdocs/prak"

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
	file_list = sys.argv[1:]
	detailed_file_list = []
	for filepath in file_list:
		components = filepath.split("/")
		experiment = components[1]
		type = components[2]
		filename = components[3]
		if "vorbereitung" in type:
			who = ""
			if "gregor" in filename:
				who = "gregor"
			elif "sven" in filename:
				who = "sven"
			else:
				continue
			detailed_file_list.append((filepath, "%s-vorbereitung-%s.pdf"%(experiment, who)))
		else:
			suffix = "auswertung"
			if "aus" not in filename and "kor" not in filename:
				continue
			elif "kor" in filename:
				suffix = "errata"
			detailed_file_list.append((filepath, "%s-%s.pdf"%(experiment, suffix)))


	for path,target in detailed_file_list:
		try:
			build_target = os.path.splitext(path)[0]+".pdf"
			publish_target = os.path.join(PUBLISH_PATH, target)
			if not upToDate(path):
				print "Rebuild", target, "...", 
				sys.stdout.flush()
				output = compileFile(path)
				if "undefined references" in output:
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
