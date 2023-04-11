from llama_index import GPTSimpleVectorIndex,LLMPredictor
from langchain import OpenAI, PromptTemplate

llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt-4"))
index = GPTSimpleVectorIndex.load_from_disk(save_path='./index.json', llm_predictor=llm_predictor)

question = "PHPカンファレンスについての記事を執筆してください。"

template = """
## 役割
あなたは技術ブログのライターです。

## 指示
- 日本語で答えてください。
- 文字数は3000字程度で執筆してください
- わからないときはわからないと答えてください。
- マークダウン形式で執筆してください。

## 質問
{question}
"""
prompt = PromptTemplate(
    input_variables=['question'],
    template=template,
)

response = index.query(prompt.format(question=question))
print(response)
