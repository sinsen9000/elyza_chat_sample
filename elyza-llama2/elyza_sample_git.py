import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
import ctranslate2
import re
import random

Termination_sig = ["！", "？", "!", "?", "。", "、", "!?", "?!"] #[:5] -> 句点, [:6] -> 句読点含む
B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
def rinna_text2text(model, tokenizer, prompt, topk=1):
    #print(prompt)
    with torch.no_grad():
        token_ids = tokenizer.convert_ids_to_tokens(tokenizer.encode(prompt, add_special_tokens=False))
        output_ids = model.generate_batch(
            [token_ids],
            max_length=64,
            #sampling_topp=0.95,
            sampling_topk=topk,
            repetition_penalty=1.2,
            include_prompt_in_result=False,
        )
    return  tokenizer.decode(output_ids[0].sequences_ids[0], skip_special_tokens=True)

tokenizer = AutoTokenizer.from_pretrained(
    "elyza/ELYZA-japanese-Llama-2-7b-fast-instruct",
)
model = ctranslate2.Generator("llama-elyza-fast-ct2",device='auto')

past_text_list = [["こんにちは。","よろしくね!"]]


user_name = "マスター"
bot_name = "あかり"

while True:
    in_w = input("入力")

    task1 = "あなたは、質問に何でも答える高性能なアンドロイドで、「%s」と言う名前です。"%(bot_name,)
    relation_task = "%sは、「%s」と言う名前の人物と一緒に暮らしています。"%(bot_name,user_name)
    state_task = ""#%(bot_name,user_name)
    emotion_task = ""
    context = ""
    text = "%sは、以下のような話し方をします。\n"%(bot_name + context) if context != "" else ""
    DEFAULT_SYSTEM_PROMPT = task1 + text + relation_task + state_task + emotion_task
    
    past_text = ""
    for i, t in enumerate(past_text_list):
        past_text += "\n%s: %s\n%s: %s"%(user_name, t[0], bot_name, t[1])
    if not in_w == "……。": past_text += "\n%s: %s\n"%(user_name, in_w)
    question = "以下の会話情報の続きをシミュレーションをしましょう。ただし、()の中には%sが動作する内容が入る。"%bot_name
    start_text = "%s: ("%(bot_name,)
    
    prompt = "{bos_token}{b_inst} {system}{prompt} {e_inst} {past}".format(
    bos_token=tokenizer.bos_token,
        b_inst=B_INST,
        system=f"{B_SYS}{DEFAULT_SYSTEM_PROMPT}{E_SYS}",
        prompt=question+"\n"+past_text,
        e_inst=E_INST+"\n",
        past=start_text
    )
    print(prompt)
    top_k=1
    for j in range(1,4):
        output = start_text+rinna_text2text(model,tokenizer,prompt,topk=top_k)
        
        temp = []
        t_f = False
        name_len = len("%s: "%bot_name)
        for i in output.splitlines():
            if "%s:"%bot_name in i[:name_len]:
                output = i.replace("%s: "%bot_name,"")
                break
        output_sentence = "".join(re.split(r'[\(\)（）]', output)[2:]) #文章だけ
        #print(output_sentence)
        if len(output_sentence) > 2 and not output_sentence in [j[1] for j in past_text_list]: break #被ったら再作成
        top_k=5*j

    print(output) #動作も含めて
    if len(past_text_list) > 5: del past_text_list[0]
    if not in_w == "……。":
        past_text_list.append([in_w, output_sentence])
    else:
        past_text_list[-1][1] += output
        print(past_text_list[-1][1])
