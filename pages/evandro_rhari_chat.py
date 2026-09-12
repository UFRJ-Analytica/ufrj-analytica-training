import streamlit as st

from requests import request
import json


prefix = "http://localhost:8000/agent/evandro-rhari-agent"


def send_mesage(role, msg, save=True):
    if save:
        st.session_state.messages.append({"role": role, "content": msg}) 
    
    with st.chat_message(role):
        st.write(msg)


def user_message(msg):
    send_mesage('user', msg)
    

def ai_respond(human_message):
    data = {"message": f'"{human_message}"' }
    response = request("post", prefix+"/chat", json=data)
    if response.status_code == 200:
        ai_msg = json.loads(response.text)['response']
    else:
        ai_msg = f"**Error {response.status_code}.** It's not like I wanted to stop working for you or anything! Something went wrong behind the scenes, okay?! Don't get the wrong idea!"
    st.session_state.messages.append({"role": "assistant", "content": ai_msg})  
    st.markdown(ai_msg)


def ai_first_messages():
    with st.chat_message("assistant"):
        st.write("H-Hey! I'm not bratty, you stupid developer!")
    with st.chat_message("assistant"):
        st.markdown("...anyway, what's _your_ deal? I've heard you like French?")


def restore_conversation():
    if "messages" not in st.session_state:  
        st.session_state.messages = []  

    for msg in st.session_state.messages:  
        send_mesage(msg["role"], msg["content"], save=False)



st.title("Tsundere French Tutor")
st.subheader("Because I'm a piece of garbadge.")

st.write("Tsundere French Tutor is a bratty chat bot that really likes helping you study french but really doens't want you to notice that.")
st.write("I, Evandro Rhari, made this app myself, but the whole thing is in English because I couldn't stand reading tsundere dialogue in Portuguese.")
st.write("'Oh but you could've made a different agent it didn't have to be a tsundere' why don't you take care of your own god damn business will you?")
st.write("Anyway enjoy learning French with a bratty computer good bye.")



st.header("Chat")


with st.container(border=True, height=500):

    ai_first_messages()
    restore_conversation()

    prompt = st.bottom.chat_input("Talk to your tutor")
    if prompt:
        user_message(prompt)

        with st.chat_message("assistant"):
            ai_respond(prompt)