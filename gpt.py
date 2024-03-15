from openai import OpenAI

def gpt_init(topic):
    # не забудь запустить сервер с моделью
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

    history = [
    {"role": "system", "content": f"You are an English teacher. You should have a conversation with user about {topic}. Your conversation should be from 5 to 10 phrases."},
    {"role": "user", "content": "Start conversation with any question."},]

    try:
        completion = client.chat.completions.create(
            model="local-model", 
            messages=history,
            temperature=0.7,
            max_tokens=128)
    except Exception as e:
        raise RuntimeError('Something wrong with GPT. Check it.')

    response = completion.choices[0].message.content
    new_answer = {"role": "assistant", "content": response}
    history.append(new_answer)
    print('GPT initialized')
    return client, history
        
def gpt_answer(client, history, prompt):
    completion = client.chat.completions.create(
        model="local-model",
        messages=history,
        temperature=0.7,
        max_tokens=128)
            
    return completion.choices[0].message.content

# EOF
