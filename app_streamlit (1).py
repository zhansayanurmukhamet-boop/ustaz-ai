import streamlit as st
import cohere
import time
import json
import re
import random
from datetime import datetime
import hashlib

# ─── Бет конфигурациясы ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ұстаз AI Көмекшісі",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Пайдаланушылар базасы (логин: пароль хэші) ───────────────────────────────
# Жаңа пайдаланушы қосу үшін: hashlib.sha256("пароль".encode()).hexdigest()
USERS = {
    "ustaz": hashlib.sha256("ustaz2025".encode()).hexdigest(),
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "teacher": hashlib.sha256("teacher2025".encode()).hexdigest(),
}

def check_login(username: str, password: str) -> bool:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return USERS.get(username) == hashed

def show_login_page():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgba(255,245,240,1) 0%, rgba(230,245,255,1) 100%);
        }
        .login-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #0F172A, #3B82F6, #10B981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.3rem;
        }
        .login-subtitle {
            text-align: center;
            color: #6B7280;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
        .stButton > button {
            background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
            color: white !important;
            border-radius: 40px !important;
            font-weight: 700 !important;
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='login-title'>🎓 Ұстаз AI</div>", unsafe_allow_html=True)
            st.markdown("<div class='login-subtitle'>Жүйеге кіру үшін логин мен паролді енгізіңіз</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            username = st.text_input("👤 Логин", placeholder="Логинді енгізіңіз", key="login_username")
            password = st.text_input("🔒 Пароль", type="password", placeholder="Паролді енгізіңіз", key="login_password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🚀 Кіру", use_container_width=True, key="login_btn"):
                if not username or not password:
                    st.error("❌ Логин мен паролді енгізіңіз!")
                elif check_login(username.strip(), password.strip()):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username.strip()
                    st.rerun()
                else:
                    st.error("❌ Логин немесе пароль қате!")

            st.markdown("<br><div style='text-align:center; color:#9CA3AF; font-size:0.75rem;'>🔐 Қауіпсіз кіру жүйесі</div>", unsafe_allow_html=True)

# ─── Логин тексеру ────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# ─── Қосымша стильдер (Premium дизайн) ───────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(255,245,240,1) 0%, rgba(230,245,255,1) 100%);
    }

    /* Sidebar - Premium қара көк */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1120 0%, #111827 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] * {
        color: #E5E7EB !important;
    }
    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stSlider label, 
    [data-testid="stSidebar"] .stRadio label {
        color: #9CA3AF !important;
        font-weight: 600;
        letter-spacing: 0.05em;
        font-size: 0.7rem;
        text-transform: uppercase;
    }

    /* Тақырып анимациясы */
    .main-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0F172A, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }
    .glow-text {
        text-shadow: 0 0 10px rgba(59,130,246,0.3);
    }

    /* Карточка 3D эффект */
    .question-card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(2px);
        border-radius: 24px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 20px 35px -15px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .question-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 45px -15px rgba(0,0,0,0.15);
        border-color: #3B82F6;
    }

    /* Статистика визуал */
    .stat-card {
        background: white;
        border-radius: 28px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 10px 20px -5px rgba(0,0,0,0.05);
        border-bottom: 3px solid #3B82F6;
    }

    /* Батырма анимациясы */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        border-radius: 40px;
        padding: 0.6rem 2rem;
        font-weight: 700;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px -5px #3B82F6;
    }
    
    /* Индикатор */
    .badge-fun {
        background: linear-gradient(135deg, #F59E0B, #D97706);
        border-radius: 40px;
        padding: 0.2rem 0.8rem;
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ─── Пәндер мен сыныптар базасы ──────────────────────────────────────────────
SUBJECTS = {
    "📐 Математика": ["5 сынып", "6 сынып", "7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"],
    "🔬 Физика": ["7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"],
    "🧪 Химия": ["8 сынып", "9 сынып", "10 сынып", "11 сынып"],
    "🌍 Биология": ["7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"],
    "📜 Тарих": ["5 сынып", "6 сынып", "7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"],
    "💻 Информатика": ["7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"],
    "📖 Қазақ тілі": ["5 сынып", "6 сынып", "7 сынып", "8 сынып", "9 сынып", "10 сынып", "11 сынып"],
    "🏛️ Құқық": ["9 сынып", "10 сынып", "11 сынып"]
}

# Керемет фактілер базасы
FUN_FACTS = [
    "🧠 AI көмегімен тест жасау уақытты 80% үнемдейді!",
    "📊 Зерттеулер бойынша, оқушылар ойын түріндегі тестілерді 3 есе жақсы қабылдайды.",
    "⚡ Cohere AI 1 секундта 1000 сөзге дейін өңдей алады.",
    "🎓 Қазақстандық мұғалімдердің 75% AI құралдарды қолдануды қалайды.",
    "🌟 Бұл тест генераторы 100% тегін және шексіз қолдануға арналған!"
]

# ─── Функциялар ───────────────────────────────────────────────────────────────
def build_prompt(topic: str, grade: str, num_questions: int, difficulty: str, q_type: str) -> str:
    diff_map = {"Оңай": "easy", "Орта": "medium", "Қиын": "hard"}
    
    if q_type == "Тест (А,В,С,D)":
        fmt = """Multiple choice with A,B,C,D. Return JSON: [{"question": "...", "options": {"A":"...","B":"...","C":"...","D":"..."}, "answer": "A", "explanation": "..."}]"""
    elif q_type == "Ашық сұрақ":
        fmt = """Open-ended questions. Return JSON: [{"question": "...", "answer": "...", "explanation": "..."}]"""
    else:
        fmt = """Mix. For MC: {"type":"mc", "question":"...", "options":{"A":"...","B":"...","C":"...","D":"..."}, "answer":"A", "explanation":"..."}. For Open: {"type":"open", "question":"...", "answer":"...", "explanation":"..."}"""
    
    return f"""Kazakh teacher AI. Topic: {topic}. Grade: {grade}. Difficulty: {diff_map[difficulty]}. Create {num_questions} questions in KAZAKH language. {fmt} Return ONLY valid JSON array."""

def call_cohere_api(api_key: str, prompt: str) -> str:
    client = cohere.ClientV2(api_key=api_key.strip())
    response = client.chat(model="command-a-03-2025", messages=[{"role": "user", "content": prompt}])
    return response.message.content[0].text

def parse_questions(raw_text: str) -> list:
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().strip('`')
    match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    return json.loads(match.group(0) if match else cleaned)

def generate_txt(questions: list, subject: str, grade: str, difficulty: str) -> str:
    lines = [f"ПӘН: {subject}", f"СЫНЫП: {grade}", f"ҚИЫНДЫҚ: {difficulty}", f"СҰРАҚ САНЫ: {len(questions)}", "="*50, ""]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q.get('question', '')}")
        if "options" in q:
            for l, t in q["options"].items():
                lines.append(f"   {l}) {t}" + (" ✓" if l == q.get("answer") else ""))
        lines.append(f"   Жауап: {q.get('answer', '')}")
        if q.get("explanation"): lines.append(f"   Түсіндірме: {q['explanation']}")
        lines.append("")
    return "\n".join(lines)

# ─── Sidebar (Жаңартылған) ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✨ Ұстаз AI")
    st.markdown(f"<div style='background:rgba(255,255,255,0.1); border-radius:12px; padding:0.5rem 0.8rem; font-size:0.8rem; color:#D1D5DB;'>👤 {st.session_state.get('current_user', '')}</div>", unsafe_allow_html=True)
    if st.button("🚪 Шығу", use_container_width=True, key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.questions = []
        st.rerun()
    st.markdown("---")
    
    api_key = st.text_input("🔑 Cohere API кілті", type="password", placeholder="Енгізіңіз...")
    
    st.markdown("---")
    st.markdown("### 📚 Пән және сынып")
    
    subject = st.selectbox("📖 Пән таңдаңыз", list(SUBJECTS.keys()))
    grade = st.selectbox("🎓 Сынып", SUBJECTS[subject])
    
    st.markdown("---")
    st.markdown("### ⚙️ Тест параметрлері")
    
    topic = st.text_input("📌 Нақты тақырып", placeholder="Мысалы: Квадрат теңдеулер, Жасуша құрылымы...")
    num_questions = st.selectbox("🔢 Сұрақ саны", [5,10,15,20,25])
    difficulty = st.select_slider("📊 Қиындық", ["Оңай","Орта","Қиын"], value="Орта")
    question_type = st.radio("📝 Сұрақ түрі", ["Тест (А,В,С,D)","Ашық сұрақ","Аралас"])
    
    # 🎮 Ойын режимі (Қызықты фича!)
    quiz_mode = st.toggle("🎮 Ойын режимі (Quiz Mode)", help="Тестілер ойын түрінде көрсетіледі")
    st.markdown("---")
    
    generate_btn = st.button("🚀 AI Тест жасау", use_container_width=True)
    
    # Керемет факті
    st.markdown("---")
    st.markdown(f"<div style='background:rgba(255,255,255,0.1); border-radius:16px; padding:0.8rem; text-align:center;'><span style='font-size:1.5rem;'>💡</span><br><span style='font-size:0.8rem;'>{random.choice(FUN_FACTS)}</span></div>", unsafe_allow_html=True)

# ─── Негізгі бет ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([3,1])
with col1:
    st.markdown('<h1 class="main-title">🎓 AI Ұстаз Көмекшісі</h1>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#4B5563;'>✨ {subject} | {grade} | {difficulty} деңгейі</p>", unsafe_allow_html=True)
with col2:
    st.markdown("<br><div class='badge-fun'>🤖 v2.0 Premium</div>", unsafe_allow_html=True)

# Бастапқы экран
if "questions" not in st.session_state:
    st.session_state.questions = []

if not st.session_state.questions and not generate_btn:
    cols = st.columns(3)
    features = [
        ("🎯", "Пән және сынып", "Сол жақтан пәніңіз бен сыныбыңызды таңдаңыз"),
        ("🤖", "AI генерация", "Cohere AI 5 секундта кәсіби тест құрастырады"),
        ("🎮", "Ойын режимі", "Quiz Mode қосып, сабақты ойынға айналдырыңыз")
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class='stat-card' style='text-align:center; padding:1.5rem;'>
                <div style='font-size:3rem;'>{icon}</div>
                <h4>{title}</h4>
                <p style='color:#6B7280; font-size:0.8rem;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# Генерация
if generate_btn:
    if not api_key:
        st.error("❌ API кілтін енгізіңіз!")
    elif not topic.strip():
        st.error("❌ Тақырыпты енгізіңіз!")
    else:
        with st.spinner(f"🧠 AI {num_questions} сұрақ дайындауда... Күтіңіз..."):
            try:
                prompt = build_prompt(topic.strip(), grade, num_questions, difficulty, question_type)
                raw = call_cohere_api(api_key.strip(), prompt)
                questions = parse_questions(raw)
                st.session_state.questions = questions
                st.session_state.quiz_mode = quiz_mode
                st.success(f"✅ {len(questions)} сұрақ сәтті жасалды! (Пән: {subject}, {grade})")
                st.balloons()
            except Exception as e:
                st.error(f"Қате: {e}")

# Нәтиже
if st.session_state.questions:
    qs = st.session_state.questions
    mc_count = sum(1 for q in qs if "options" in q)
    
    # Статистика
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f"<div class='stat-card'><div style='font-size:2rem;'>{len(qs)}</div><div>Барлық сұрақ</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='stat-card'><div style='font-size:2rem;'>{mc_count}</div><div>Тест сұрақ</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='stat-card'><div style='font-size:2rem;'>{len(qs)-mc_count}</div><div>Ашық сұрақ</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='stat-card'><div style='font-size:1.8rem;'>⭐</div><div>{difficulty}</div></div>", unsafe_allow_html=True)
    
    st.markdown(f"### 📖 {topic} — {grade} сынып")

    # Ойын режимі немесе қарапайым
    if st.session_state.get("quiz_mode", False):
        # Quiz Mode: прогресс бар
        if "q_index" not in st.session_state: st.session_state.q_index = 0
        if st.session_state.q_index >= len(qs): st.session_state.q_index = 0
        
        q = qs[st.session_state.q_index]
        progress = (st.session_state.q_index + 1) / len(qs)
        st.progress(progress, text=f"Сұрақ {st.session_state.q_index + 1}/{len(qs)}")
        
        with st.container():
            st.markdown(f"<div class='question-card'><h3>❓ {q.get('question')}</h3>", unsafe_allow_html=True)
            if "options" in q:
                answer_key = st.radio("Жауабыңыз:", list(q["options"].values()), key=f"quiz_{st.session_state.q_index}")
                if st.button("✅ Тексеру", key="check"):
                    correct_text = q["options"].get(q.get("answer"), "")
                    if answer_key == correct_text:
                        st.success("🎉 Дұрыс! +1 ұпай")
                        st.balloons()
                    else:
                        st.error(f"❌ Қате! Дұрыс жауап: {correct_text}")
                st.caption(f"💡 {q.get('explanation', '')}")
            else:
                st.text_area("Жауабыңыз:", key="open_answer")
                if st.button("Жіберу"):
                    st.info(f"📌 Модель жауабы: {q.get('answer')}\n\n💡 {q.get('explanation', '')}")
            
            colA, colB = st.columns(2)
            with colA:
                if st.session_state.q_index > 0 and st.button("◀ Артқа"):
                    st.session_state.q_index -= 1
                    st.rerun()
            with colB:
                if st.session_state.q_index < len(qs)-1 and st.button("Келесі ▶"):
                    st.session_state.q_index += 1
                    st.rerun()
    else:
        # Қарапайым көрсету
        for i, q in enumerate(qs, 1):
            with st.expander(f"📌 {i}. {q.get('question', '')[:80]}..."):
                if "options" in q:
                    for l, t in q["options"].items():
                        mark = "✅" if l == q.get("answer") else "🔘"
                        st.markdown(f"{mark} **{l})** {t}")
                    st.info(f"✅ **Жауап:** {q.get('answer')}")
                else:
                    st.info(f"📝 **Жауап:** {q.get('answer')}")
                if q.get("explanation"): st.success(f"💡 {q['explanation']}")
    
    # Жүктеу
    st.markdown("---")
    col1, col2 = st.columns(2)
    txt_data = generate_txt(qs, subject, grade, difficulty)
    json_data = json.dumps(qs, ensure_ascii=False, indent=2)
    with col1:
        st.download_button("📄 TXT жүктеу", txt_data.encode('utf-8'), f"test_{subject}_{grade}.txt", use_container_width=True)
    with col2:
        st.download_button("📊 JSON жүктеу", json_data.encode('utf-8'), f"test_{subject}_{grade}.json", use_container_width=True)
    
    if st.button("🔄 Жаңа тест бастау"):
        st.session_state.questions = []
        st.rerun()

# Footer
st.markdown("<hr><center><span style='color:#9CA3AF;'>Губайдуллаева Нұрайна | Нұрмұхамет Жансая | Смагулова Диана | AI Ұстаз Көмекшісі 2025</span></center>", unsafe_allow_html=True)