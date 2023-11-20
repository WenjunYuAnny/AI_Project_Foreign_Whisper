import os
from transformers import T5ForConditionalGeneration, T5Tokenizer

def read_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        original_script = file.readlines()
    return original_script
    
def text_from_srt(original_scripts):
    origianl_script_text = []
    current_text = ""

    for line in original_scripts:
        line = line.strip()
        if line.isdigit():
            if current_text:
                origianl_script_text.append(current_text)
            current_text = ""
        elif '-->' in line:
            continue
        elif line:
            if current_text != "":
                current_text += " "
            current_text += line
    if current_text:
        origianl_script_text.append(current_text)

    return origianl_script_text

def translate(original_script_text):
    model_name = "t5-base"
    tokenizer = T5Tokenizer.from_pretrained(model_name, model_max_length=1024)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    task_prefix = "translate English to French: "
    inputs = tokenizer([task_prefix + line for line in original_script_text], return_tensors="pt", padding=True)
    output_sequences = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        do_sample=False,
        max_length=200,
    )
    translated_script_text = tokenizer.batch_decode(output_sequences, skip_special_tokens=True)
    # print(translated_content)
    return translated_script_text

def text_to_srt(original_script, translated_script_text):
    translated_script = []
    count = 0
    for i, line in enumerate(original_script):
        if line.strip().isdigit():
            translated_script.append(line)
        elif '-->' in line:
            translated_script.append(line)
        elif line == '\n':
            translated_script.append(line)
        elif line:
            translated_script.append(translated_script_text[count])
            count += 1
            translated_script.append('\n')
    return translated_script

def save_srt(source_path, output_dir, translated_script):
    filename = os.path.basename(source_path)
    output_path = os.path.join(output_dir, filename) + '.srt'
    with open(output_path, 'w', encoding='utf-8') as file:
        file.writelines(translated_script)   

def translate_srt_file(source_path, output_dir):
    original_script = read_srt(source_path)
    original_script_text = text_from_srt(original_script)
    translated_script_text = translate(original_script_text)
    translated_script = text_to_srt(original_script, translated_script_text)
    save_srt(source_path, output_dir, translated_script)

def translate_srt_from_dir(source_dir, output_dir):
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        translate_srt_file(file_path, output_dir)

source_dir = 'transcript_srt'
output_dir = 'translated_srt'
translate_srt_from_dir(source_dir, output_dir)



