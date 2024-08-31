from fastapi import FastAPI, File, UploadFile, Form, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse
import os
import shutil
from gptpdf import parse_pdf
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者指定特定的允许访问的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/result", StaticFiles(directory="result"), name="static_result")

# 创建请求会话，并应用重试策略
def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    return session

def add_url_prefix(file_path, url_prefix):
    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    new_content = pattern.sub(lambda m: f"![{m.group(1)}]({url_prefix}{m.group(2)})", content)
    with open(file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(new_content)

def generate_slug(url):
    url = re.sub(r'^https?://', '', url)
    return re.sub(r'[^\w\-]', '_', url)

def create_directory(file_name, overwrite=False):
    dir_name = file_name
    if os.path.exists(dir_name):
        if overwrite:
            shutil.rmtree(dir_name)
        else:
            return 0
    os.makedirs(dir_name)
    print(f"文件夹 '{dir_name}' 创建成功")
    return 1

def is_url(path_or_url):
    try:
        result = urlparse(path_or_url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def save_uploaded_file(uploaded_file: UploadFile, destination: str):
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

@app.post("/convert/")
async def convert(
    url: str = Form(None), 
    web_url: str = Form(...),
    file: UploadFile = File(None), 
    using_cn: bool = Form(False),
    overwrite: bool = Form(False),
    model_name: str = Form('gpt-4o'),  
    api_key: str = Form(...),  
    base_url: str = Form('https://api.openai-proxy.org/v1'),  
    temperature: float = Form(0.2)  
):
    root_path = 'result/'
    session = create_session()  
    if file.filename != '':
        file_name = generate_slug(file.filename)
        if using_cn:
            file_name = "CN_doc_" + file_name
        FILE_DIR = root_path + file_name
        e_flag = create_directory(FILE_DIR, overwrite=overwrite)
        pdf_filename = os.path.join(FILE_DIR, file_name + ".pdf")
        save_uploaded_file(file, pdf_filename)
    elif url:
        file_name = generate_slug(url)
        if using_cn:
            file_name = "CN_doc_" + file_name
        FILE_DIR = root_path + file_name
        e_flag = create_directory(FILE_DIR, overwrite=overwrite)
        pdf_filename = os.path.join(FILE_DIR, file_name + ".pdf")
        
        try:
            response = session.get(url)
            response.raise_for_status()
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to download PDF: {e}"}
    else:
        return {"error": "No valid file or URL provided"}

    output_filename = os.path.join(FILE_DIR, 'output.md')

    # 定义 prompt
    if not using_cn:
        DEFAULT_PROMPT = """Use markdown syntax to convert the text recognized in the PDF into markdown format output. You must:
        1. Output the content in the same language as recognized in the PDF. For example, if you recognize an English field, the output content must be in English.
        2. Do not explain or output irrelevant text. Directly output the contents from the PDF. For example, do not output statements like ‘Below is the markdown text generated based on the PDF content:’ Instead, output the markdown directly.
        3. Content should not be enclosed in markdown, use for block formulas, use for inline formulas, ignore long horizontal lines, and ignore page numbers.
        To emphasize again, do not explain or output irrelevant text. Directly output markdown from the PDF.
        4. Don't use the markdown code block (''' ''').
        5. Set the heading levels according to the structure of the original text.
        6. Please output the text without any strikethrough formatting (no lines through the middle of the text). Avoid using the ~~ syntax for strikethrough.
        7. For the detected LaTeX formulas, do not use `\(`, `\)` and `\[` , `\]` to wrap these formulas. Instead, use `$` and `$$` for easier Markdown rendering."""
        
        DEFAULT_RECT_PROMPT = """The areas in the PDF are marked with a red box and a name (%s). If the area contains tables or illustrations, you MUST (important!) insert them into the output content using the ![]() format, because I want to see them in the markdown preview! For illustration contains texts, do not OCR them to text but save the illustration using the ![]() format! Additionally, do not include the links to the illustrations within the Markdown code block (''' '''), as this would prevent them from being rendered."""
        
        DEFAULT_ROLE_PROMPT = """You are a PDF document parser. Use markdown and LaTeX syntax to output the content of the PDF."""
    else:
        DEFAULT_PROMPT = """使用 Markdown 语法将从 PDF 中识别的文本转换为 Markdown 格式，并翻译为中文。请严格遵循以下指南：
        1. 必须提供完整且逐字逐句的中文翻译，不要遗漏任何单词或短语。**不得对内容进行总结或概括。**
        2. 直接翻译 PDF 内容，不要包含解释或无关的文本。避免类似“以下是根据 PDF 内容生成的 Markdown 文本”的表述，直接输出 Markdown 内容即可。
        3. 不要将内容放入 Markdown 代码块内，使用进行块状公式，使用进行行内公式，忽略长水平线和页码。
        4. 不要使用 Markdown 代码块（''' '''）。
        5. 保持标题级别的原有结构。
        6. 确保文本中不包含任何删除线格式，避免使用 ~~ 语法。
        7. 对于检测到的latex公式，不要用'\(', '\)' 和 '\[','\]'来包裹这些公式，而应该使用'$'以及'$$', 便于markdown渲染."""
        
        DEFAULT_RECT_PROMPT = """PDF 中的区域用红框和名称（%s）标记。**必须（重要！）**使用 ![]() 格式将表格或插图插入输出内容，以确保它们在 Markdown 预览中可见。对于包含文本的插图，不要将文本转换为 OCR，而是用 ![]() 格式保存插图。此外，不要在 Markdown 代码块（''' '''）内包含插图链接，因为这会阻止它们的渲染。"""
        
        DEFAULT_ROLE_PROMPT = """您是一个 PDF 文档解析器和翻译器。使用 Markdown 和 LaTeX 语法翻译并输出 PDF 内容。**不要进行总结或概括，确保完整输出内容。**"""

    prompt = {
        "prompt": DEFAULT_PROMPT,
        "rect_prompt": DEFAULT_RECT_PROMPT,
        "role_prompt": DEFAULT_ROLE_PROMPT
    }

    # 调用 parse_pdf 进行 PDF 解析
    if e_flag:
        content, image_paths = parse_pdf(
            pdf_filename, 
            output_dir=FILE_DIR, 
            model=model_name, 
            api_key=api_key, 
            base_url=base_url, 
            prompt=prompt, 
            gpt_worker=15, 
            temperature=temperature
        )
        
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(content)
        add_url_prefix(output_filename, os.path.join(web_url, FILE_DIR) + '/')
    else:
        with open(output_filename, "r", encoding="utf-8") as file:
            content = file.read()

    return Response(content=content, media_type="text/markdown")

@app.get("/download/")
def download_markdown(url: str, using_cn: bool = False):
    file_name = generate_slug(url)
    if using_cn:
        file_name = "CN_doc_" + file_name
    output_filename = f'result/{file_name}/output.md'
    if not os.path.exists(output_filename):
        return {"error": "文件不存在"}
    
    return FileResponse(output_filename, media_type='text/markdown', filename=f'{file_name}.md')

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
