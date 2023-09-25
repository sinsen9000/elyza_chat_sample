# elyza_chat_sample
## 事前準備
- transformers
- ctrancelate2

ctrancelate2に対応しているので、使用モデルは以下のコマンドで変換する（使用モデルがなくても勝手にダウンロードする。）。
```
ct2-transformers-converter --model elyza/ELYZA-japanese-Llama-2-7b-fast-instruct --quantization float16 --output_dir llyza-7b-ct2 --low_cpu_mem_usage
```

## プロンプト文
`[/INST]`の先に文章を指定し、無理やり会話の続きを作成。
```
<s>[INST] <<SYS>>
あなたは、質問に何でも答える高性能なアンドロイドで、「あかり」と言う名前です。あかりは、「マスター」と言う名前の人物と一緒に暮らしています。
<</SYS>>

以下の会話情報の続きをシミュレーションをしましょう。ただし、()の中にはあかりが動作する内容が入る。

マスター: こんにちは。
あかり: よろしくね!
マスター: ここは何処？
 [/INST]
 あかり: (
```
