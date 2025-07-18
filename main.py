import streamlit as st
from database import init_db, get_user, add_book, get_books, delete_book, add_word, get_words, update_memorized, delete_word
from auth import signup, login
from dictionary_api import get_suggestions, get_meaning_and_pos, get_example_sentence

# Streamlit 설정
st.set_page_config(page_title="나만의 영어 암기장", layout="wide")
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_db()
if "user" not in st.session_state:
    st.session_state["user"] = None
if "selected_suggestion" not in st.session_state:
    st.session_state["selected_suggestion"] = ""

st.title("나만의 영어 암기장 ✏️")

menu = ["로그인", "회원가입"]
if st.session_state["user"]:
    menu = ["단어장"]

choice = st.sidebar.selectbox("메뉴", menu)

# 로그아웃 기능
if st.session_state["user"]:
    if st.sidebar.button("로그아웃"):
        st.session_state["user"] = None
        st.session_state["selected_suggestion"] = ""
        st.rerun()

# OpenAI API키 미리 입력(로그인 후)
if st.session_state["user"]:
    openai_key = st.sidebar.text_input("OpenAI API Key (예문 생성용)", type="password", key="openai_api_key")
    st.session_state["openai_key"] = openai_key

# 로그인/회원가입
if choice == "회원가입":
    st.subheader("회원가입")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.button("가입하기"):
        if signup(username, password):
            st.success("회원가입 성공! 로그인 해주세요.")
        else:
            st.error("이미 존재하는 아이디입니다.")

if choice == "로그인":
    st.subheader("로그인")
    username = st.text_input("아이디", key="login_id")
    password = st.text_input("비밀번호", type="password", key="login_pw")
    if st.button("로그인"):
        user = login(username, password)
        if user:
            st.session_state["user"] = user
            st.session_state["selected_suggestion"] = ""
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

# 단어장 메인
if st.session_state["user"]:
    user = st.session_state["user"]
    st.sidebar.write(f"환영합니다, {user[1]}님!")
    st.sidebar.markdown("---")

    # 단어장 관리
    books = get_books(user[0])
    book_names = [b[2] for b in books]
    book_dict = {b[2]: b[0] for b in books}

    st.sidebar.subheader("📚 단어장 선택/생성")
    selected_book = None
    book_name = ""
    if books:
        book_name = st.sidebar.selectbox("단어장 선택", book_names)
        selected_book = book_dict[book_name]

        if st.sidebar.button("단어장 삭제"):
            delete_book(selected_book)
            st.session_state["selected_suggestion"] = ""
            st.rerun()
    new_book = st.sidebar.text_input("새 단어장 이름")
    if st.sidebar.button("단어장 만들기"):
        if new_book.strip():
            if new_book.strip() not in book_names:
                add_book(user[0], new_book.strip())
                st.rerun()
            else:
                st.sidebar.error("이미 존재하는 단어장 이름입니다.")

    st.markdown("---")

    # 본 프로그램 화면
    if selected_book:
        st.subheader(f"📖 '{book_name}' 단어장")

        st.markdown("#### 영단어 추가")
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            # 실시간 추천, 버튼 클릭 시 자동완성!
            word = st.text_input("영단어 입력", key="add_word", value=st.session_state.get("selected_suggestion", ""))
            suggestions = []
            if word:
                suggestions = get_suggestions(word)
                if suggestions:
                    st.markdown("**자동완성 추천:**")
                    for idx, sug in enumerate(suggestions):
                        if st.button(sug, key=f"sugbtn_{idx}"):
                            st.session_state["selected_suggestion"] = sug
                            st.rerun()
            else:
                st.session_state["selected_suggestion"] = ""

        with col2:
            meaning, pos = ("", "")
            if word:
                meaning, pos = get_meaning_and_pos(word)
            meaning = st.text_input("한국어 뜻", value=meaning, key="add_meaning")

        with col3:
            pos_map = {"n": "명사(n)", "v": "동사(v)", "adj": "형용사(adj)", "adv": "부사(adv)"}
            st.markdown(f"**품사:** {pos_map.get(pos, pos)}")

        # 단어 중복 방지
        words_text = [w[2] for w in get_words(selected_book)]
        if st.button("추가"):
            if word and meaning:
                if word not in words_text:
                    add_word(selected_book, word, meaning, pos)
                    st.success("단어가 추가되었습니다.")
                    st.session_state["selected_suggestion"] = ""
                    st.rerun()
                else:
                    st.error("이미 존재하는 단어입니다.")
            else:
                st.error("단어와 뜻을 입력해주세요.")

        st.markdown("---")
        st.markdown("### 📜 단어 리스트")

        # 품사 컬러링
        pos_colors = {"n": "noun", "v": "verb", "adj": "adj", "adv": "adv"}
        words = get_words(selected_book)
        blind_on = st.checkbox("블라인드 모드 (뜻/단어 가리기)", value=False)
        pos_on = st.checkbox("품사 컬러 표시", value=True)

        for w in words:
            word_id, _, word, meaning, pos, memorized = w
            color_class = pos_colors.get(pos, "noun") if pos_on else ""
            st.write(
                f'<div class="word-card">'
                f'<b class="{color_class}">{"■" if pos_on else ""} {word if not blind_on else f"<span class=blind>{word}</span>"}</b> '
                f'- {meaning if not blind_on else f"<span class=blind>{meaning}</span>"} '
                f'<span style="font-size:13px;">({pos})</span> '
                f'{"<b>[외움]</b>" if memorized else "[미암기]"} '
                f'</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns([1, 2, 1])
            # (2) 예문 생성 버튼 → 클릭 시 바로 예문 출력
            with c1:
                if st.button("예문 생성", key=f"ex{word_id}"):
                    api_key = st.session_state.get("openai_key", None)
                    if api_key:
                        ex = get_example_sentence(word, api_key)
                        st.info(ex)
                    else:
                        st.warning("OpenAI API Key를 먼저 입력해 주세요.")
            with c2:
                if st.button("단어 삭제", key=f"del{word_id}"):
                    delete_word(word_id)
                    st.rerun()
            with c3:
                mem_btn = "암기해제" if memorized else "암기하기"
                if st.button(mem_btn, key=f"mem{word_id}"):
                    update_memorized(word_id, 0 if memorized else 1)
                    st.rerun()


