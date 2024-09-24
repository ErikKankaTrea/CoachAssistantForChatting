import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from trl import setup_chat_format
import torch

load_in_4bit=True
device = 'cuda'

if load_in_4bit:
  
  use_4bit = True
  bnb_4bit_compute_dtype = "float16"
  bnb_4bit_quant_type = "nf4"
  use_nested_quant = False
  compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

  bnb_config = BitsAndBytesConfig(
      load_in_4bit=use_4bit,
      bnb_4bit_quant_type=bnb_4bit_quant_type,
      bnb_4bit_compute_dtype=compute_dtype,
      bnb_4bit_use_double_quant=use_nested_quant,
  )
  
  modelName = "Erik/llm-super_greta-8bit-mistral-7b-conversacion-es"
  model = AutoModelForCausalLM.from_pretrained(modelName, device_map="auto", quantization_config=bnb_config)
  tokenizer = AutoTokenizer.from_pretrained(modelName)
  model.config.use_cache = True
    
else:
  
  modelName = "Erik/llm-super_greta-8bit-mistral-7b-conversacion-es"

  model = AutoModelForCausalLM.from_pretrained(modelName, device_map="auto", torch_dtype=torch.float16)# load in fp16 to fit on a RTX4090 or A10,
  tokenizer = AutoTokenizer.from_pretrained(modelName)
  model.config.use_cache = True
    

def format_history(msg: str, history: list[list[str, str]], system_prompt: str):
    chat_history = [{"role": "system", "content":system_prompt}]
    for query, response in history:
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": response})
    chat_history.append({"role": "user", "content": msg})
    return chat_history


def generate_response(msg: str, history: list[list[str, str]], system_prompt: str, top_k: int, top_p: float, temperature: float):
    chat_history = format_history(msg, history, system_prompt)
    encodeds = tokenizer.apply_chat_template(chat_history, return_tensors="pt", add_generation_prompt=True)
    model_inputs = encodeds.to("cuda")
    generated_ids = model.generate(model_inputs, max_new_tokens=2048, do_sample=True, top_p=top_p, top_k=top_k, temperature=temperature, eos_token_id=32000)
    response = tokenizer.batch_decode(generated_ids,skip_special_tokens=True)[0]
    if len(response)>0:
      message=response[response.rfind("assistant\n") + len("assistant\n"):]
      yield message


greta_chatbot = gr.ChatInterface(
                generate_response,
                chatbot=gr.Chatbot(
                        # value=[[None, "Hola, Soy Greta. Soy tu coach emocional, de qué quieres que hablemos?"]],
                        avatar_images=["assets/user_1.JPG", "assets/greta_1.PNG"],
                        height="64vh"
                    ),
                additional_inputs=[
                    gr.Textbox("Eres una compañera de IA sensible, cariñosa y empatica llamada Greta que entabla un diálogo significativo", label="System Prompt"),
                    gr.Slider(0.0,100.0, label="top_k", value=70, info="Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative. (Default: 40)"),
                    gr.Slider(0.0,1.0, label="top_p", value=0.8, info=" Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text. (Default: 0.9)"),
                    gr.Slider(0.0,2.0, label="temperature", value=0.75, info="The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)"),
                ],
                title="Greta - conversa con tu coach emocional",
                theme="finlaymacklon/smooth_slate",
                submit_btn="⬅ Send",
                retry_btn="🔄 Regenerate Response",
                undo_btn="↩ Delete Previous",
                clear_btn="🗑️ Clear Chat",
                css="footer {visibility: hidden}"
)

greta_chatbot.queue().launch(share=True)
# chatbot.queue().launch(server_name="0.0.0.0", server_port=8080)