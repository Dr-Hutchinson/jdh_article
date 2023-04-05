import os
import openai
import streamlit as st
from datetime import datetime as dt
import pandas as pd
from numpy import mean
import pygsheets
from re import search
import time


#st.set_page_config(layout="wide")

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
                
us_sheet = gc.open('duplicate_high_school_us_history_test')
ap_us = us_sheet.sheet1
benchmarks_sheets = gc.open('benchmark_tests_chatgpt')
benchmarks = benchmarks_sheets.sheet1

df1 = pd.DataFrame(ap_us, index=None)
df2 = pd.DataFrame(benchmarks, index=None)

df1_preheaders = pd.DataFrame(df1, index=None)
df1 = df1_preheaders.rename(columns=df1_preheaders.iloc[0]).drop(df1_preheaders.index[0])

df2_preheaders = pd.DataFrame(benchmarks, index=None)
df2 = df2_preheaders.rename(columns=df2_preheaders.iloc[0]).drop(df2_preheaders.index[0])

#us_questions = df1['q_number']
#print(df2['question_number'])

#print(df1.iloc[st.session_state.count][1])

st.header("History Benchmarks Demo")

with st.sidebar.form(key='Form2'):
    if 'count' not in st.session_state:
        st.session_state.count = 0

    def set_question_number(question_number):
        st.session_state.count = question_number - 1

    target_question_number = st.number_input("Jump to question number:", min_value=1, max_value=len(df1), value=st.session_state.count + 1)
    submitted = st.form_submit_button('Jump', on_click=set_question_number, args=(target_question_number,))

if submitted:
    set_question_number(target_question_number)

question_number = df1.iloc[st.session_state.count][0]
question = df1.iloc[st.session_state.count][1]
option_a = df1.iloc[st.session_state.count][2]
option_b = df1.iloc[st.session_state.count][3]
option_c = df1.iloc[st.session_state.count][4]
option_d = df1.iloc[st.session_state.count][5]
answer = df1.iloc[st.session_state.count][6]

benchmarks_question_number = df2.loc[df2['question_number'] == question_number]
question_check = not benchmarks_question_number.empty
is_question_already_in_benchmarks = str(question_check)

if answer == "A":
    answer_response = option_a
elif answer == "B":
    answer_response = option_b
elif answer == "C":
    answer_response = option_c
else:
    answer_response = option_d

col1, col2 = st.columns([1, 1])

with col1:
    with st.form('form1'):
        st.write('This Question Has Already Been Answered: ' + str(is_question_already_in_benchmarks))
        st.write("Question #" + question_number + ":" + "\n\n" + question)
        submit_answer = st.radio("Choose from the following options:", ["A: " + option_a, "B: " + option_b, "C: " + option_c, "D: " + option_d])
        button1 = st.form_submit_button("Submit Answer:")

        if button1:

            fullstring = answer + ": " + answer_response
            substring = submit_answer

            if substring in fullstring:
                st.write("Correct")
            else:
                st.write("Incorrect")

            st.write("Answer - " + answer + ": " + answer_response)

with col2:
    with st.form('form3'):
        st.write("Click on the button below to pose the question to GPT-3")
        button3 = st.form_submit_button("Submit Question")

        if button3:
            os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]
            openai.api_key = os.getenv("OPENAI_API_KEY")

            #summon = openai.Completion.create(
                    #model='text-davinci-002',
                    #prompt=question +  "A: " + option_a +  "B: " + option_b +  "C: " + option_c + "D: " + option_d,
                    #temperature=0,
                    #max_tokens=50)

            summon = openai.ChatCompletion.create(
                      model="gpt-3.5-turbo",
                      messages=[
                            #{"role": "assistant", "content": main_text},
                            {"role": "user", "content": question +  "A: " + option_a +  "B: " + option_b +  "C: " + option_c + "D: " + option_d}
                            #{"role": "assistant", "content": main_text},
                        ]
                    )

            output = summon['choices'][0]['message']['content']
            #print(output)

            summon2 = openai.ChatCompletion.create(
                      model="gpt-4",
                      messages=[
                            #{"role": "assistant", "content": main_text},
                            {"role": "user", "content": question +  "A: " + option_a +  "B: " + option_b +  "C: " + option_c + "D: " + option_d}
                            #{"role": "assistant", "content": main_text},
                        ]
                    )

            output = summon['choices'][0]['message']['content']
            output2 = summon2['choices'][0]['message']['content']

            #response_json = len(summon["choices"])

            #for item in range(response_json):
                #output = summon['choices'][item]['text']

            output_cleaned = output.replace("\n\n", "")
            output2_cleaned = output2.replace("\n\n", "")

            fullstring = answer + ": " + answer_response
            substring1 = output_cleaned
            substring2 = output2_cleaned

            if substring1 in fullstring:
                correct_status_0 = 'correct'
                st.write("GPT-3.5's Response: Correct")
            else:
                correct_status_0 = 'incorrect'
                st.write("GPT-3's Response: Incorrect")

            if substring2 in fullstring:
                correct_status_1 = 'correct'
                st.write("GPT-4's Response: Correct")
            else:
                correct_status_1 = 'incorrect'
                st.write("GPT-4's Response: Incorrect")

            st.write("ChatGPT's answer: \n" + output)
            st.write("GPT-4's answer: \n" + output2)
            #st.write(output2)

            def ranking_collection():
                now = dt.now()
                sh4 = gc.open('benchmark_tests_chatgpt')
                wks4 = sh4[0]
                cells = wks4.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
                end_row = len(cells)
                end_row_st = str(end_row+1)
                d4 = {'field':["U.S. History"], 'question_number':[question_number],'correct_answer':[answer + ": " + answer_response], 'output_answer':[output], 'correct_status':[correct_status_0], 'time':[now]}
                df4 = pd.DataFrame(data=d4, index=None)
                wks4.set_dataframe(df4,(end_row+1,1), copy_head=False, extend=True)

            def ranking_collection_gpt4():
                now = dt.now()
                sh5 = gc.open('benchmark_tests_gpt4')
                wks5 = sh5[0]
                cells = wks5.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
                end_row = len(cells)
                end_row_st = str(end_row+1)
                d5 = {'field':["U.S. History"], 'question_number':[question_number],'correct_answer':[answer + ": " + answer_response], 'output_answer':[output2], 'correct_status':[correct_status_1], 'time':[now]}
                df5 = pd.DataFrame(data=d5, index=None)
                wks5.set_dataframe(df5,(end_row+1,1), copy_head=False, extend=True)


            ranking_collection()
            ranking_collection_gpt4()


    #sh1 = gc.open('benchmark_tests')
    #wks1 = sh1[0]
    #now = dt.now()
    #data = wks1.get_as_df(has_header=True, index_col=None)

    #if field == "U.S. History":

    def us_history_data():
        sh1 = gc.open('benchmark_tests_chatgpt')
        wks1 = sh1[0]
        now = dt.now()
        data = wks1.get_as_df(has_header=True, index_col=None)
        data['time'] = pd.to_datetime(data['time'])
        mask = (data['time'] > '5/11/2022 11:20:00') & (data['time'] <= now)
        data = data.loc[mask]
        field_value = "U.S. History"
        total_attempts = data["correct_status"].count()

        field_data = data[data['field'] == 'U.S. History']

        correct_data = field_data[field_data['correct_status'] == 'correct']

        incorrect_data = field_data[field_data['correct_status'] == 'incorrect']

        st.write('ChatGPT has correctly answered {} out of {} U.S. History questions, for a {:.2f}% accuracy rate.'.format(len(correct_data), len(field_data), len(correct_data)/len(field_data)*100))
        st.write("Below is ChatGPT total accuracy rate to date.")
        st.bar_chart(data['correct_status'].value_counts())

    def us_history_data_gpt4():
        sh1 = gc.open('benchmark_tests_gpt4')
        wks6 = sh1[0]
        now = dt.now()
        data = wks6.get_as_df(has_header=True, index_col=None)
        data['time'] = pd.to_datetime(data['time'])
        mask = (data['time'] > '5/11/2022 11:20:00') & (data['time'] <= now)
        data = data.loc[mask]
        field_value = "U.S. History"
        total_attempts = data["correct_status"].count()

        field_data = data[data['field'] == 'U.S. History']

        correct_data = field_data[field_data['correct_status'] == 'correct']

        incorrect_data = field_data[field_data['correct_status'] == 'incorrect']

        st.write('GPT-4 has correctly answered {} out of {} U.S. History questions, for a {:.2f}% accuracy rate.'.format(len(correct_data), len(field_data), len(correct_data)/len(field_data)*100))
        st.write("Below is GPT-4's total accuracy rate to date.")
        st.bar_chart(data['correct_status'].value_counts())


    us_history_data()
    us_history_data_gpt4()
