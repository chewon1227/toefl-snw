import os
import pandas as pd
from datetime import datetime
import language_tool_python
import whisper
import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.groq.com/openai/v1"
)
3

whisper_model = whisper.load_model("base")
grammar_tool = language_tool_python.LanguageTool('en-US')

def ask_llama(prompt):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# STT by whisper 
def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path, language='en')
    return result["text"]

def evaluate_grammar(text):
    # convert to lowercase to ignore case in grammar check
    matches = grammar_tool.check(text.lower())
    feedback = [f"{match.message} → Suggestion: {match.replacements}" for match in matches]
    score = max(0, 4 - len(matches) // 3)
    return score, feedback

def evaluate_pronunciation(text):
    prompt = f"""
You are a TOEFL speaking evaluator. Based on this transcript:
"{text}"
Give:
- Pronunciation Score (0-4)
- Specific pronunciation issues
- Suggestions for improvement
Respond:
Score: x/4
Feedback: ...
"""
    output = ask_llama(prompt)
    lines = output.splitlines()
    score_line = next((l for l in lines if "Score:" in l), "Score: 2/4")
    feedback_line = next((l for l in lines if "Feedback:" in l), "Feedback: Needs work.")
    score = int(score_line.split(":")[1].split("/")[0].strip())
    return score, feedback_line.replace("Feedback:", "").strip()

def evaluate_toefl_rubric(text, task_num):
    if task_num == 1:
        prompt = f"""
            You are a TOEFL Speaking Task 1 evaluator. This is an independent speaking task.
            Transcript:
            "{text}"

            Evaluate based on the following:
            - Delivery (fluency, pronunciation, intonation)
            - Language Use (grammar accuracy, vocabulary, sentence variety)
            - Topic Development (clear opinion, logical organization, completeness)

            Score each from 0 to 4 and give a total score out of 30.
            Format:
            Delivery: x/4
            Language Use: x/4
            Topic Development: x/4
            Total Score: xx/30
            """
    else:
        prompt = f"""
            You are a TOEFL Speaking Task {task_num} evaluator. This is an **integrated speaking task**.
            Transcript:
            "{text}"

            Evaluate based on the following:
            - Delivery (fluency, pronunciation, intonation)
            - Language Use (grammar accuracy, vocabulary, sentence variety)
            - Topic Development (accurate use of reading/listening source, coherence, completeness)

            Score each from 0 to 4 and give a total score out of 30.
            Format:
            Delivery: x/4
            Language Use: x/4
            Topic Development: x/4
            Total Score: xx/30
            """

    output = ask_llama(prompt)
    lines = output.splitlines()
    delivery = int([l for l in lines if "Delivery:" in l][0].split(":")[1].split("/")[0].strip())
    language = int([l for l in lines if "Language Use:" in l][0].split(":")[1].split("/")[0].strip())
    topic = int([l for l in lines if "Topic Development:" in l][0].split(":")[1].split("/")[0].strip())
    total = int([l for l in lines if "Total Score:" in l][0].split(":")[1].split("/")[0].strip())
    return delivery, language, topic, total

def get_results(data, excel_path="toefl_speaking_results.xlsx"):
    df = pd.DataFrame([data])
    print("\n📊 Evaluation Result:")
    print(df.to_markdown(index=False))

    if os.path.exists(excel_path):
        existing_df = pd.read_excel(excel_path)
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel(excel_path, index=False)

def evaluate_response(audio_path, task_number):
    transcript = transcribe_audio(audio_path)
    grammar_score, grammar_feedback = evaluate_grammar(transcript)
    pronunciation_score, pronunciation_feedback = evaluate_pronunciation(transcript)
    delivery_score, language_score, topic_score, total_score = evaluate_toefl_rubric(transcript, task_number)

    result = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Task": task_number,
        "Transcript": transcript,  # ✅ Transcript 포함
        "Grammar Score": grammar_score,
        "Grammar Feedback": "; ".join(grammar_feedback),
        "Pronunciation Score": pronunciation_score,
        "Pronunciation Feedback": pronunciation_feedback,
        "Delivery Score": delivery_score,
        "Language Score": language_score,
        "Topic Score": topic_score,
        "Total TOEFL Score": total_score
    }

    get_results(result)
    return result

def record_audio(filename="input.wav", duration=60, fs=44100):
    print(f"Recording for {duration} seconds... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)
    print(f"Recording saved as {filename}")
    return filename

def evaluate_existing_file(filepath, task_number):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    return evaluate_response(filepath, task_number)

def record_and_transcribe(filename="input.wav", duration=60):
    audio_path = record_audio(filename=filename, duration=duration)
    transcript = transcribe_audio(audio_path)
    txt_path = filename.replace(".wav", ".txt")
    with open(txt_path, "w") as f:
        f.write(transcript)
    print(f"Transcript saved as {txt_path}")
    return transcript

