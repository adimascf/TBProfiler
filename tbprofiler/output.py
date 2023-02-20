from .text import write_text
from .pdf import write_pdf
from .docx import write_docx
from datetime import datetime
from pathogenprofiler import infolog, debug
import json
import tbprofiler as tbp

def write_outputs(args,results,template_file = None):
    infolog("\nWriting outputs")
    infolog("---------------")

    json_output = args.dir+"/results/"+args.prefix+".results.json"
    text_output = args.dir+"/results/"+args.prefix+".results.txt"
    csv_output = args.dir+"/results/"+args.prefix+".results.csv"
    pdf_output = args.dir+"/results/"+args.prefix+".results.pdf"
    docx_output = args.dir+"/results/"+args.prefix+".results.docx"
    tree_output = args.dir+"/results/"+args.prefix+".results.nwk"
    if "reporting_af" not in vars(args):
        args.reporting_af = 0.1
    if "add_columns" not in vars(args):
        args.add_columns = None
    extra_columns = [x.lower() for x in args.add_columns.split(",")] if args.add_columns else []
    results["timestamp"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    infolog(f"Writing json file: {json_output}")
    json.dump(results,open(json_output,"w"))

    
    
    if "pdf" in vars(args) and args.pdf:
        infolog(f"Writing pdf file: {pdf_output}")
        write_pdf(results,args.conf,pdf_output)
    if args.txt:
        infolog(f"Writing text file: {text_output}")
        write_text(results,args.conf,text_output,extra_columns,reporting_af=args.reporting_af,sep="\t",template_file=template_file,use_suspect=args.suspect)
    if args.csv:
        infolog(f"Writing csv file: {csv_output}")
        write_text(results,args.conf,csv_output,extra_columns,reporting_af=args.reporting_af,sep=",",template_file = template_file,use_suspect=args.suspect)
    if args.docx:
        infolog(f"Writing docx file: {docx_output}")
        write_docx(results,args.conf,docx_output,args.docx,reporting_af=args.reporting_af)