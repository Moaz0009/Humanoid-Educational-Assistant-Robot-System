import ollama

def evaluate_answer(correct_answer, student_answer):
    model_name = "prakasharyan/qwen-arabic"

    prompt = f"هل الإجابة التالية صحيحة , تغاضي عن التهجئة وقارن بناء علي المعني ؟\n" \
             f"الإجابة الصحيحة: {correct_answer}\n" \
             f"إجابة الطالب: {student_answer}\n" \
             f"يرجى تحديد ما إذا كانت إجابة الطالب صحيحة (1) أو خاطئة (0)."
    
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    
    try:
        response_text = response['message']['content']
    except KeyError:
        return "Erorr, Try again!"  # In case of unexpected response structure
    print(response_text)
    return response_text # 0 ->(incorrect), 1 -> (Correct)
