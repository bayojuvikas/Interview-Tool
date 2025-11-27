from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title = "streamlit", page_icon = ":smiley:")
st.title("Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "messages" not in st.session_state:
    st.session_state.messages = []

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:
    st.subheader('personal information', divider = "rainbow")

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    name = st.text_input(label="Name",value=st.session_state["name"],max_chars=40,placeholder="enter your name")
    experience = st.text_area(label="Experience",value=st.session_state["experience"],max_chars=200,placeholder="enter your experience")
    skills = st.text_area(label="Skills",value=st.session_state["skills"],max_chars=200,placeholder="enter your skills")

    name = st.write(f"**your name**: {name}")
    experience = st.write(f"**your experience**:{experience}")
    skills = st.write(f"**your skills**:{skills}")

    st.subheader('company and position', divider = "rainbow")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state["level"] = st.radio(
            "choose level",
            key="visibility",
            options=["junior", "mid-level", "senior"],
        )

    with col2:
        st.session_state["position"] = st.selectbox(
            "choose a position",
            ("data scientist", "data engineer", "ml engineer", "bi analyst", "financial analyst"),

        )    

    st.session_state["company"] = st.selectbox(
        "select a company",
        ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"),
    )

    st.write(f"{st.session_state["level"]} {st.session_state["position"]} at {st.session_state["company"]}")

    if st.button("start interview", on_click=complete_setup):
        st.write("Setup complete. Starting interview...")


if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    st.info("Start Introducing By Yourself",
     icon = "yep"
     )
     
    client = OpenAI(api_key = st.secrets["openai_api_key"])

    if "opeai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if not st.session_state.messages:
        st.session_state.messages = [{"role": "system", "content": f"You are an HR executive that interviews an interviewee called {st.session_state['name']} "
                            f"with experience {st.session_state['experience']} and skills {st.session_state['skills']}. "
                            f"You should interview him for the position {st.session_state['level']} {st.session_state['position']} "
                            f"at the company {st.session_state['company']}"}]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("your answer.", max_chars=40):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.response.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_message_count += 1

    if st.session_state.user_message_count <= 5: 
        st.session_state.chat_complete = True   

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("get feed back", on_click=show_feedback):
        st.write("fetching_feedback")

if st.session_state.feedback_shown:
    st.subheader("feedback")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback_completion = feedback_client.chat.completions.create(
        model = "gpt-4o",
        messages=[
            {"role": "system", "content": """you are a helpful tool that evaluates the interview very effectively.
            before giving the feedback generate a score of 1 to 10.
            Follow the format as follows:
            Overal Score: //your score
            Feedback: //here you put your feedback
            Give only the feedback do not ask any additional questions. 
            "},
            {"role": "user", "content": f"This is the interview you need to evaluate. You are only a tool. so don't engage in conversation {conversation_history}"""}
        ]
    )
    
    st.write(feedback_completion.choices[0].messages.content)

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")