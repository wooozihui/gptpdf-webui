# GPTPDF-WebUI

A Cyberpunk style WebUI for [gptpdf](https://github.com/CosmosShadow/gptpdf), convert local or url PDF file to markdown. Demo: https://gptpdf-webui.onrender.com (The free service of Render may take ~1 minute to wake up)
![image](https://github.com/user-attachments/assets/5c5278f3-2774-4a38-94c8-f62538df7769)
![image](https://github.com/user-attachments/assets/499203a5-ff9c-4732-9f76-e8e341d2df4b)

# Deploy
## Local

```
cd ./GPTPDF-WebUI/gptpdf-webui/app
pip install -r requirements
uvicorn main:app --reload
```

## Docker
```
docker run -d -p 80:8000 --name gpdpdf-webui zihui998/gptpdf-webui
```

# Setting

Click "Configute Parameters" to set:
- API key 
- model_name (Only support VLLMs like GPT-4o and GPT-4o-mini)
- base_url.
- Temperature
