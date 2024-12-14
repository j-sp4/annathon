This is a template for benchmarking models.

By default, LightRAG seems to use a GPT model and its associated embedding model. However, it may be useful to compare LightRAG's default config with the capabilities of other configurations (different language models & different embedding models).

#### Here's a collection of alternative language models that are available:
- GPT?
- Ollama?
- Huggingface repos such as those listed on https://github.com/InternLM/InternLM

#### Here's a collection of alternative embedding models that are available:
- https://huggingface.co/spaces/mteb/leaderboard


<br><br>

## Todo: 
- create test data of various types (text < 1000 words, text > 1000 words, VQA UltraDomain)?
    - < 1000 words: Husband story
    - \> 1000 words: Husband saga
    - UltraDomain: https://huggingface.co/datasets/TommyChien/UltraDomain
- create interesting metrics for evaluating configurations
- benchmark output format:
    - (date, language model, embedding model, embedding dims, RAM usage, VRAM usage, speed, [metric 1, metric 2, ...])