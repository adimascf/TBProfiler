import pathogenprofiler as pp
import time

def dict_list2tex(l,columns = None, mappings = {}):
    headings = list(l[0].keys()) if not columns else columns
    rows = []
    header = " & ".join([mappings[x].title() if x in mappings else x.title() for x in headings])+"\\tabularnewline"
    for row in l:
        r = " & ".join(["%.3f" % row[x] if isinstance(row[x],float) else str(row[x]).replace("_", " ") for x in headings])
        rows.append(r)
    column_def = "".join(["l" for _ in headings])
    str_rows = "\\tabularnewline\n".join(rows)+"\\tabularnewline"
    return "\\begin{tabular}{%s}\n%s\n\\hline\n%s\n\\hline\n\end{tabular}" % (column_def,header,str_rows)


def load_tex(tex_strings):
	return r"""
%%%% LyX 2.3.0 created this file.  For more info, see http://www.lyx.org/.
\documentclass[english]{report}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[T1]{fontenc}
\usepackage[latin9]{inputenc}
\usepackage[a4paper]{geometry}
\geometry{verbose,tmargin=2cm,bmargin=2cm,lmargin=2cm,rmargin=2cm}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}
\usepackage{graphicx}

\makeatletter

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% LyX specific LaTeX commands.
%% Because html converters don't know tabularnewline
\providecommand{\tabularnewline}{\\}

\makeatother

\usepackage{babel}
\begin{document}

\chapter*{TBProfiler report}

The following report has been generated by TBProfiler.
\section*{Summary}
\begin{description}
\item [{ID:}] %(id)s
\item [{Date:}] %(date)s
\item [{Strain:}] %(strain)s
\item [{Drug-resistance:}] %(drtype)s
\end{description}

\section*{Lineage report}

%(lineage_report)s

\section*{Resistance report}

%(dr_report)s

\section*{Other variants report}

%(other_var_report)s

\section*{Analysis pipeline specifications}

\begin{description}
\item [{Version:}] %(version)s
\end{description}

%(pipeline)s

\section*{Disclaimer}

This tool is for \textbf{Research Use Only} and is offered free for
use. The London School of Hygiene and Tropical Medicine shall have
no liability for any loss or damages of any kind, however sustained
relating to the use of this tool.

\section*{Citation}

Coll, F. \textit{et al}. Rapid determination of anti-tuberculosis
drug resistance from whole-genome sequences. \textit{Genome Medicine}
7, 51. 2015

\end{document} """ % tex_strings

def write_tex(json_results,conf,outfile,columns = []):
	drugs = set()
	for l in open(conf["bed"]):
		arr = l.rstrip().split()
		for d in arr[5].split(","):
			drugs.add(d)
	drug_table = []
	results = {}
	annotation = {}
	for key in columns:
		if key not in json_results["dr_variants"][0]: pp.log("%s not found in variant annotation, is this a valid column in the database CSV file? Exiting!" % key,True)
	for x in json_results["dr_variants"]:
		d = x["drug"]
		if d not in results: results[d] = list()
		results[d].append("\\textit{%s} %s (%.2f)" % (x["gene"],x["change"],x["freq"]))
		if d not in annotation: annotation[d] = {key:[] for key in columns}
		for key in columns:
			annotation[d][key].append(x[key])
	for d in drugs:
		if d in results:
			results[d] = ", ".join(results[d]) if len(results[d])>0 else ""
			r = "R" if len(results[d])>0 else ""
			for key in columns:
				annotation[d][key] = ", ".join(annotation[d][key]) if len(annotation[d][key])>0 else ""
		else:
			results[d] = ""
			r = ""
		dictline = {"Drug":d,"Genotypic Resistance":r,"Mutations":results[d]}
		for key in columns:
			dictline[key] = annotation[d][key] if d in annotation else ""
		drug_table.append(dictline)
	pipeline_tbl = [{"Analysis":"Mapping","Program":json_results["pipeline"]["mapper"]},{"Analysis":"Variant Calling","Program":json_results["pipeline"]["variant_caller"]}]

	tex_strings = {}
	tex_strings["id"] = json_results["id"].replace("_","\_")
	tex_strings["date"] = time.ctime()
	tex_strings["strain"] = json_results["sublin"].replace("_","\_")
	tex_strings["drtype"] = json_results["drtype"]
	tex_strings["dr_report"] = dict_list2tex(drug_table,["Drug","Genotypic Resistance","Mutations"]+columns)
	tex_strings["lineage_report"] = dict_list2tex(json_results["lineage"],["lin","frac","family","spoligotype","rd"],{"lin":"Lineage","frac":"Estimated fraction"})
	tex_strings["other_var_report"] = dict_list2tex(json_results["other_variants"],["genome_pos","locus_tag","change","freq"],{"genome_pos":"Genome Position","locus_tag":"Locus Tag","freq":"Estimated fraction"})
	tex_strings["pipeline"] = dict_list2tex(pipeline_tbl,["Analysis","Program"])
	tex_strings["version"] = json_results["tbprofiler_version"]
	o = open(outfile,"w")
	o.write(load_tex(tex_strings))
	o.close()
