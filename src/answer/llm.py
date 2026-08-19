from transformers import (AutoTokenizer, AutoModelForCausalLM,
                          PreTrainedTokenizerBase)
from src.model import MinimalSource
from typing import Any
import torch


TO_STRIP = [
    "The answer is: ",
    "Answer: ",
    "The answer",
]

AVOID = [
    "Answer: ",
    "Answer:",
    "Answer",
    "Answer ",
    "Answer\n",
]

SYSTEM_CONTEXT: str = """
SYSTEM:
Answer the question in a single sentence using the context.

USER:
Context:
"""

MAX_TOKEN_SIZE = 100


class Llm():
    """
    llm model of QWEN/QWEN3_0.6B
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        *,
        device: Any = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = True,
    ) -> None:
        """
        Initialize the language model and tokenizer.

        If no device is provided, the best available device is selected with
        the following priority: MPS, CUDA, then CPU. The model is configured
        for inference only.

        Args:
            model_name: The Hugging Face model identifier to load.
            device: The device used to run the model.
            dtype: The data type used for the model weights.
            trust_remote_code: Whether to trust custom code from the model
                repository.
        """

        self._model_name: str = model_name

        # Auto-select device with priority: mps > cuda > cpu
        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        self._device = device

        if dtype is None:
            dtype = (torch.float16 if self._device in
                     ["cuda", "mps"] else torch.float32)
        self._dtype = dtype

        # --- load tokenizer & model ---------------------
        self._tokenizer: PreTrainedTokenizerBase = (
            AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=trust_remote_code))
        if self._tokenizer.pad_token_id is None:
            # ensure we have a pad token to keep batch helpers happy
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

        self._model: Any = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=self._dtype,
            device_map="auto" if self._device == "cuda" else None,
            trust_remote_code=trust_remote_code,
        )
        self._model.to(self._device)
        self._model.eval()

        # switch to inference-only mode
        for p in self._model.parameters():
            p.requires_grad = False

        self.max_tokens = self._model.config.max_position_embeddings
        self.curr_tokens = MAX_TOKEN_SIZE

        self.input_ids: list[int] = []

    def encode(self, text: str) -> torch.Tensor:
        """
        Encode text into a tensor of token IDs.

        Args:
            text: The text to tokenize.

        Returns:
            A 2-D tensor containing the token IDs on the configured device.
        """
        ids = self._tokenizer.encode(text, add_special_tokens=False)
        return torch.tensor([ids], device=self._device, dtype=torch.long)

    def decode(self, ids: torch.Tensor | list[int]) -> str:
        """
        Decode token IDs into text.

        Special tokens are removed from the decoded output.

        Args:
            ids: A tensor or list containing token IDs.

        Returns:
            The decoded text.
        """
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        return str(self._tokenizer.decode(ids, skip_special_tokens=True))

    def add_prompt(self, value: str) -> None:
        """
        Add text to the current prompt.

        The text is tokenized and added to the current input only if
        the model's maximum token limit is not exceeded.

        Args:
            value: The text to add to the prompt.
        """
        ids = self.encode(value)[0]
        len_ids = len(ids)

        if self.curr_tokens + len_ids > self.max_tokens:
            return
        self.curr_tokens += len_ids
        self.input_ids.extend(ids)

    def generate_prompt(self, question: str,
                        source: list[MinimalSource]) -> None:
        """
        Build the prompt from the system context, retrieved sources,
        and user question.

        Retrieved chunks are added until the model's token limit is reached.
        The question is appended after the retrieved context.

        Args:
            question: The question to answer.
            source: The retrieved sources used as context.
        """
        self.add_prompt(SYSTEM_CONTEXT)

        question_ids = self.encode(f"QUESTION:\n{question}")[0]

        self.curr_tokens += len(question_ids)

        for i, elem in enumerate(source):
            self.add_prompt(f"\nChunk [{i+1}] \n{elem.content}\n")
        self.input_ids.extend(question_ids)

    def find_first_valid(self, result: str) -> str | list[str]:
        """
        Extract the most relevant answer from the generated text.

        Args:
            result: The raw text generated by the language model.

        Returns:
            The extracted answer.
        """
        splitted_result: list[str] = result.split("\n")
        larger: int = 0
        bigger_key: int = 0

        for i, line in enumerate(splitted_result):
            if line in AVOID or (("Answer" in line or "Explain" in line) and
                                 ("question" in line or
                                  "sentence" in line or
                                  "context" in line)):
                continue
            elif i == 0:
                larger = len(line)
            elif len(line) > larger:
                larger = len(line)
                bigger_key = i

        value = splitted_result[bigger_key]
        for key in TO_STRIP:
            if key in value:
                value = value.lstrip(key)
        return value

    def generate(self) -> str:
        """
        Generate an answer from the current prompt.

        The current input token IDs are passed to the model, which generates
        up to MAX_TOKEN_SIZE new tokens. The generated text is then decoded
        and processed to extract the answer.

        Returns:
            The generated and cleaned answer.
        """
        input_ids = torch.tensor(
            [self.input_ids],
            device=self._device,
            dtype=torch.long
        )

        output_ids = self._model.generate(
            input_ids,
            eos_token_id=self._tokenizer.eos_token_id,
            max_new_tokens=MAX_TOKEN_SIZE)

        result = self.decode(output_ids[0][len(self.input_ids):])
        return str(self.find_first_valid(result))

    def reset(self) -> None:
        """
        Reset the current prompt state.

        Clears the stored input token IDs and resets the current token count,
        allowing a new question to be processed.
        """
        self.input_ids = []
        self.curr_tokens = MAX_TOKEN_SIZE
