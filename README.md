# GPTPDF-WebUI

A WebUI for gptpdf.
![image](https://github.com/user-attachments/assets/5c5278f3-2774-4a38-94c8-f62538df7769)

# Local

```
cd ./GPTPDF-WebUI/gptpdf-webui/app
pip install -r requirements
uvicorn main:app --reload
```

# Docker
```
docker run -d -p 8000:8000 zihui998/gptpdf-webui
```
