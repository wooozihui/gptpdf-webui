# 🌐 GPTPDF-WebUI

A Cyberpunk-style WebUI for [gptpdf](https://github.com/CosmosShadow/gptpdf) that converts local or URL PDF files to markdown. 📝 Check out the [Demo](https://gptpdf-webui.onrender.com) (Note: The free service of Render may take ~1 minute to wake up). ⏳

![image](https://github.com/user-attachments/assets/5c5278f3-2774-4a38-94c8-f62538df7769)
![image](https://github.com/user-attachments/assets/499203a5-ff9c-4732-9f76-e8e341d2df4b)

## 🚀 Deploy

### 🖥️ Local Deployment

```bash
cd ./GPTPDF-WebUI/gptpdf-webui/app
pip install -r requirements.txt
uvicorn main:app --reload
```

### 🐳 Docker Deployment

```bash
docker run -d -p 8000:8000 --name gpdpdf-webui ghcr.io/wooozihui/gptpdf-webui:latest
```

## ⚙️ Settings

Click "🛠️ Configure Parameters" to set:

- 🔑 API key
- 🧠 model_name (Only supports VLLMs like GPT-4o and GPT-4o-mini)
- 🌐 base_url
- 🔥 Temperature
