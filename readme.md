# Satya - Verify Before You Trust

**Satya** is a simple, fast, and reliable AI-powered tool that empowers users to instantly verify the authenticity of text and images they encounter online. By leveraging the power of Google's Gemini AI, Satya provides a quick verdict and supporting evidence to help combat misinformation.

---

## ✨ Core Features

- **AI-Powered Analysis**: Utilizes Google's Gemini API to analyze content for authenticity.  
- **Multi-Format Support**: Verify content from plain text and images.  
- **Web Application**: An intuitive web interface for direct text input and image uploads.  
- **Browser Extension**: A handy Chrome extension to check content directly from any webpage with a simple right-click.  
- **Evidence-Based Reports**: Each analysis provides a clear verdict (Scam/Genuine), a confidence score, a detailed explanation, and reference URLs from the web.  
- **Anonymous Reporting**: Allows users to report scam content, which is compiled into a daily email digest for administrators.  

---

## ⚙️ How It Works

Users can interact with Satya in two primary ways:

1. **Via the Web App**  
   Visit the Satya website, choose the content type (text or image), paste or upload the content, and click **"Check with Satya"**.

2. **Via the Browser Extension**  
   On any webpage, select a piece of text or right-click an image and choose the **"Verify with Satya"** option from the context menu.

In both cases, the content is sent to our central **Flask backend**, which communicates with the **Gemini AI** to perform the analysis.  
A clear, easy-to-understand report is then displayed back to the user.

---

## 🛠️ Tech Stack

This project is built with a modern, serverless-first approach.

| Component            | Technology                                      |
|----------------------|------------------------------------------------|
| **Backend**          | Python, Flask, Google Gemini API, Supabase (PostgreSQL) |
| **Frontend**         | HTML5, CSS3, JavaScript (Vanilla)              |
| **Browser Extension**| Chrome WebExtensions APIs (HTML, CSS, JS)      |
| **Deployment**       | Vercel                                         |

---

## 📂 Project Structure

<div style="background-color:#1e1e1e; color:#d4d4d4; padding:15px; border-radius:10px; font-family: monospace; font-size:14px; line-height:1.5;">

📂 Project  
├── 📄 app.py                # Main Flask application logic and API routes  
├── 📄 email_utils.py        # Handles fetching reports and sending email digests  
├── 📄 supabase_client.py    # Manages connection and data insertion to Supabase  
│  
├── 📂 static/               # Contains all frontend CSS and JavaScript files  
│   ├── 🎨 styles.css  
│   └── ⚙️ script.js  
│  
├── 📂 templates/            # Contains all frontend HTML files  
│   ├── 🖼️ index.html  
│   └── 🖼️ report.html  
│  
├── 📂 extension/            # All files for the Chrome browser extension  
│   ├── 📄 manifest.json  
│   ├── 🖼️ popup.html  
│   ├── 🎨 popup.css  
│   ├── ⚙️ popup.js  
│   └── ⚙️ background.js  
│  
├── 📄 vercel.json           # Vercel deployment configuration (including Cron Job)  
├── 📄 requirements.txt      # Python dependencies  

</div>



## ✨ Designed & Developed by [**KODOVERS**](https://kodovers.vercel.app/)  