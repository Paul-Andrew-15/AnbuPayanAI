# 🌍 AnbuPayanAI

**AnbuPayanAI** is an AI-powered personalized trip planner that helps travelers generate custom itineraries, plan budgets, and interact with a multilingual travel assistant chatbot. The system is powered by **Google Gemini AI** and built with a simple, interactive **Streamlit UI**.  

---

## ✨ Features  

- 🗺️ **Personalized Itinerary Generator** – Creates tailored itineraries based on budget, trip duration, and interests.  
- 💰 **Budget Recommendation System** – Provides optimized cost breakdowns for travel plans.  
- 💬 **Trip Planning Chatbot** – Multilingual chatbot support for major Indian languages.  
- 🔄 **AI-Powered Regeneration** – Modify itineraries or budgets on-demand with instant updates.  
- 📄 **PDF Export** – Download itineraries and budgets as neatly formatted PDFs (powered by ReportLab).  

---

## 🛠️ Tech Stack  

- **AI & NLP**: Google Gemini AI  
- **Frontend**: Streamlit  
- **PDF Generation**: ReportLab  
- **Multilingual Support**: Gemini AI’s language capabilities  

---
 
## ⚙️ Installation & Local Setup  

### 1. Clone the Repository  
```bash
git clone https://github.com/Paul-Andrew-15/AnbuPayanAI.git
cd AnbuPayanAI
````

### 2. Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate 
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

### 5. Run the App

```bash
streamlit run app.py
```

🔗 The app will open in your browser at:
`http://localhost:8501`

---

## 📂 Project Structure

```
AnbuPayanAI/
│── Home.py               # Home page and Itinerary generator  
│── Budget.py             # Budget recommendation page
│── Chatbot.py            # Chatbot page
│── /fonts                # Fonts required for storing in pdfs
│── requirements.txt      # Dependencies  
│── README.md             # Project documentation  
```

---

## 📸 Screenshots

### 💬 Chatbot Page

![](./screenshots/FA1.PNG)
![](./screenshots/FA2.PNG)
![](./screenshots/FA3.PNG)

### 📊 Quiz Page

![](./screenshots/FB1.PNG)
![](./screenshots/FB2.PNG)

---

## 🎥 Demo Video

👉 [Watch the demo here]()

---

## 📂 Presentation
👉 [View the presentation here](https://github.com/Paul-Andrew-15/AnbuPayanAI/blob/main/AnbuPayanAI_presentation.pptx)

---

## 🎯 USP of AnbuPayanAI

🌐 Inclusive Multilinguality – Supports India’s most spoken languages.
🔄 Adaptive & Regenerative – Dynamic itineraries and budgets that adapt in real time.
🛠️ All-in-One Companion – From itinerary planning to budget breakdowns and PDF exports.

---

## 🔮 Future Enhancements

* 🗺️ Map Integration – Add interactive maps linked with itineraries for better navigation.
* 🎟️ Easy Booking System – Integrate direct booking for hotels, transport, and activities.
* 🎙️ Voice Assistant – Provide hands-free travel planning and assistance through voice commands.

---

## 📜 License

This project is licensed under the MIT License.
Use, modify, and share freely with proper attribution.

---

