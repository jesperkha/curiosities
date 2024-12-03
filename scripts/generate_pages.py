import os
import re
from datetime import datetime
import markdown_code_blocks

def template(source: str, name: str, insert: str) -> str:
    return source.replace("{"+name+"}", insert) 

def filename_to_title(filename: str) -> str:
    return " ".join(filename.removesuffix(".md").capitalize().split("-"))

def replace_image_template(html):
    pattern = r"<p>\{IMAGE ([^}]+)\}</p>"
    replaced_html = re.sub(pattern, r'<img src="../.github/\1">', html)
    return replaced_html

def page_md_to_html(filename: str, out_dir: str, template_file: str):
    with open(f"pages/{filename}", "r") as f:
        md = f.read()
        if filename == "index.md":
            entries = ""
            for file in os.listdir("pages"):
                if file == "index.md":
                    continue

                file_link = f"[{filename_to_title(file)}](src/{file})"
                mod_unix_time = os.path.getmtime(f"pages/{file}")
                dt_object = datetime.fromtimestamp(mod_unix_time)
                modified = dt_object.strftime('%d.%m.%y')
                entries += f"- ({modified}) {file_link}\n"

            md = template(md, "ENTRIES", entries)

        html = markdown_code_blocks.highlight(md)
        html = html.replace(".md", ".html")
        html = replace_image_template(html)
        with open(f"{out_dir}/{filename.strip('.md')}.html", "w+") as wf:
            page = template_file
            page = template(page, "NAME", filename_to_title(filename))
            page = template(page, "BODY", html)
            wf.write(page)

def create_pages(source_dir: str, out_dir: str):
    files = os.listdir(source_dir)
    template_file = open("templates/page.html", "r")
    template_str = template_file.read()
    for page in files:
        page_md_to_html(page, out_dir, template_str)
    
    template_file.close()

def create_index():
    with open("templates/index.html", "r") as templ:
        page_md_to_html("index.md", ".", templ.read())

if __name__ == "__main__":
    create_pages("pages", "src")
    create_index()