# GPTPDF-WebUI

A WebUI for gptpdf. Demo: https://gptpdf-webui.onrender.com
![image](https://github.com/user-attachments/assets/5c5278f3-2774-4a38-94c8-f62538df7769)

# deploy
## Local

```
cd ./GPTPDF-WebUI/gptpdf-webui/app
pip install -r requirements
uvicorn main:app --reload
```

## Docker
```
docker run -d -p 8000:8000 zihui998/gptpdf-webui
```

# Setting

Click "Configute Parameters", set with your API key, model_name (Only support VLLMs like GPT-4o and GPT-4o-mini), base_url.
