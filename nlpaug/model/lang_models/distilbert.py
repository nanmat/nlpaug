import logging

try:
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer
except ImportError:
    # No installation required if not using this function
    pass

from nlpaug.model.lang_models import LanguageModels
from nlpaug.util.selection.filtering import *


class DistilBert(LanguageModels):
    # https://arxiv.org/pdf/1910.01108.pdf
    START_TOKEN = '[CLS]'
    SEPARATOR_TOKEN = '[SEP]'
    MASK_TOKEN = '[MASK]'
    SUBWORD_PREFIX = '##'

    def __init__(self, model_path='distilbert-base-uncased', temperature=1.0, top_k=None, top_p=None, device='cuda', silence=True):
        super().__init__(device, temperature=temperature, top_k=top_k, top_p=top_p, silence=True)
        try:
            import transformers
        except ModuleNotFoundError:
            raise ModuleNotFoundError('Missed transformers library. Install transfomers by `pip install transformers`')
            
        self.model_path = model_path

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        if silence:
            # Transformers thrown an warning regrading to weight initialization. It is expected
            orig_log_level = logging.getLogger('transformers.' + 'modeling_utils').getEffectiveLevel()
            logging.getLogger('transformers.' + 'modeling_utils').setLevel(logging.ERROR)
            self.model = AutoModelForMaskedLM.from_pretrained(model_path)
            logging.getLogger('transformers.' + 'modeling_utils').setLevel(orig_log_level)

        self.model.to(self.device)
        self.model.eval()

    def id2token(self, _id):
        # id: integer format
        return self.tokenizer.convert_ids_to_tokens([_id])[0]

    def is_skip_candidate(self, candidate):
        return candidate[:2] == self.SUBWORD_PREFIX

    def predict(self, text, target_word=None, n=1):
        # Prepare inputs
        tokens = self.tokenizer.tokenize(text)

        tokens.insert(0, self.START_TOKEN)
        tokens.append(self.SEPARATOR_TOKEN)
        target_pos = tokens.index(self.MASK_TOKEN)

        token_inputs = self.tokenizer.convert_tokens_to_ids(tokens)
        mask_inputs = [1] * len(token_inputs)  # 1: real token, 0: padding token

        # Convert to feature
        token_inputs = torch.tensor([token_inputs]).to(self.device)
        mask_inputs = torch.tensor([mask_inputs]).to(self.device)

        # Prediction
        with torch.no_grad():
            outputs = self.model(input_ids=token_inputs, attention_mask=mask_inputs)
        target_token_logits = outputs[0][0][target_pos]

        # Selection
        seed = {'temperature': self.temperature, 'top_k': self.top_k, 'top_p': self.top_p}
        target_token_logits = self.control_randomness(target_token_logits, seed)
        target_token_logits, target_token_idxes = self.filtering(target_token_logits, seed)
        if len(target_token_idxes) != 0:
            results = self.pick(target_token_logits, target_token_idxes, target_word=target_word, n=n)
        else:
            results = None

        results = (results,)

        return results
