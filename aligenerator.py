from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
import time

logger = logging.getLogger(__name__)

class AICodeGenerator:
    def __init__(self, model_name="bigcode/starcoder"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        self.load_model()

    def load_model(self):
        try:
            logger.info(f"Загрузка модели {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            self.is_loaded = True
            logger.info("Модель успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            self.is_loaded = False

    def generate_code(self, prompt, max_tokens=256):
        if not self.is_loaded:
            raise RuntimeError("Модель не загружена")

        start_time = time.time()
        try:
            enhanced_prompt = f"# Задача: {prompt}\n# Решение:\n"
            inputs = self.tokenizer(enhanced_prompt, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    attention_mask=inputs.attention_mask
                )
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            result = generated_text.replace(enhanced_prompt, "").strip()
            logger.info(f"Код сгенерирован за {time.time() - start_time:.2f} сек")
            return result
        except Exception as e:
            logger.error(f"Ошибка генерации кода: {e}")
            raise

_generator = None
def get_generator():
    global _generator
    if _generator is None:
        _generator = AICodeGenerator()
    return _generator

def generate_code(prompt, max_tokens=256):
    generator = get_generator()
    return generator.generate_code(prompt, max_tokens)