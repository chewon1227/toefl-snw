# TOEFL Speaking Evaluation System

An automated evaluation system for TOEFL Speaking test. Provides audio recording, transcription, grammar checking, pronunciation assessment, and comprehensive evaluation based on TOEFL scoring criteria.

## Key Features

- **Audio Recording**: Real-time audio recording functionality
- **Audio Transcription**: Accurate speech-to-text conversion using Whisper AI
- **Grammar Checking**: English grammar error detection and correction suggestions using LanguageTool
- **Pronunciation Assessment**: AI-based pronunciation scoring and improvement suggestions
- **TOEFL Scoring**: Evaluation based on official TOEFL Speaking scoring criteria
- **Result Storage**: Automatic saving and management of evaluation results in Excel files

## Installation

```bash
pip install -r requirements.txt
```

For macOS:
```bash
brew install ffmpeg
```

Set Groq API key in `eval/toefl_eval.py` file:

```python
client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.groq.com/openai/v1"
)
```

## Usage

```python
from toefl_eval import evaluate_existing_file

evaluate_existing_file("task1.wav", 1)
```

```python
from toefl_eval import record_audio, evaluate_response

audio_file = record_audio("my_recording.wav", duration=60)
result = evaluate_response(audio_file, 1)
```

```python
from toefl_eval import record_and_transcribe

transcript = record_and_transcribe("my_recording.wav", duration=60)
```

## Evaluation Criteria

### Grammar Assessment (0-4 points)
- Grammar error detection using LanguageTool
- Specific correction suggestions

### Pronunciation Assessment (0-4 points)
- AI-based pronunciation quality evaluation
- Improvement suggestions

### Official TOEFL Scoring Criteria
- **Delivery** (0-4 points): Fluency, pronunciation, intonation
- **Language Use** (0-4 points): Grammar accuracy, vocabulary, sentence variety
- **Topic Development** (0-4 points): Clear opinion, logical organization, completeness
- **Total Score** (0-30 points)

## Result Storage

Results are automatically saved to `toefl_speaking_results.xlsx` file 
- Evaluation date and time
- Task number
- Audio transcript
- Individual scores and feedback for each criterion
- Total TOEFL score

