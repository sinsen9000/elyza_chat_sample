import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_model():
    model_name = "elyza/Llama-3-ELYZA-JP-8B"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        use_cache=True,
        trust_remote_code=True,
    )
    model.eval()
    model = torch.compile(model)
    return tokenizer, model

def rinna_text2text(tokenizer, model,prompt, add_prompt="", topk=40, words=84):
    with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
        token_ids = tokenizer.encode(prompt+add_prompt, add_special_tokens=False, return_tensors="pt")
        output_ids = model.generate(
            token_ids.to(model.device),
            max_new_tokens=words,
            do_sample=True,
            top_k=topk,
            temperature=0.7,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
        )
        result = add_prompt + tokenizer.decode(output_ids.tolist()[0][token_ids.size(1) :], skip_special_tokens=True)
    return result

if __name__ == '__main__':
    tokenizer, model = load_model()
    split_compile = re.compile(r'[\(\)（）]')
    past_text_list = [["よろしく。","(お辞儀をする)元気だった?"]]
    user_name = "マスター"
    bot_name = "あかり"
    txt_datas = [s.strip() for s in open("yami.txt", encoding = "utf-8").readlines()]

    while True:
        in_w = input("入力")

        past_text = ""
        for i, t in enumerate(reversed(past_text_list)):
            output_sentence = split_compile.split(t[1])
            past_text = f"""ユーザのセリフ「{t[0]}」<|eot_id|><|start_header_id|>assistant<|end_header_id|>

    {bot_name}のセリフ「{output_sentence[2]}」
    動作内容「{output_sentence[1]}」<|eot_id|><|start_header_id|>user<|end_header_id|>

    """ + past_text
            if i == 2: break
        text = f"ユーザのセリフ「{in_w}」" if not in_w in ["","\n"] else f"ユーザの動作内容「死んでしまい、動けない」"
        past_text += text
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

    女性の「{bot_name}」になりきり、以下の項目を厳密に守ってユーザーと会話しろ。

    ## {bot_name}の設定
    - 「あかりちゃん」と呼ばれている。
    - ユーザーの友達。
    - {bot_name}自身を示す一人称は「私」。 

    ## {bot_name}の口調
    - 丁寧語を使わない。
    - 一人称は「私」。

    ## ユーザーの設定
    - 名前 = {user_name}。
    - 性別 = 男性。
    - 「マスターくん」と呼ばれている。

    [ユーザーのセリフから、必ず「{bot_name}のセリフ」と「動作内容」を作成せよ。]<|eot_id|><|start_header_id|>user<|end_header_id|>

    {past_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

    {bot_name}のセリフ「"""

        print(prompt)
        for j in range(6):
            output = rinna_text2text(tokenizer, model,prompt,topk=40)
            output = output.replace("<|eot_id|>","")
            output = output.replace("\n","__")
            print(output)
            output_split = re.split("」.*?「", output)
            if len(output_split) >= 2 and output_split[-1] != "":
                output = re.sub(r'[\(（]','【',output)
                output = re.sub(r'[\)）]','】',output)
                break

        print(output_split)
        output = f"({output_split[1]}){output_split[0]}"
        output = output.replace("」","")
        output = output.replace("__","")

        print(output)
        if len(past_text_list) > 20: del past_text_list[0]
        past_text_list.append([in_w, output])
