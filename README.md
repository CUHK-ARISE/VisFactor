# Human Cognitive Benchmarks Reveal Foundational Visual Gaps in MLLMs

[![arXiv](https://img.shields.io/badge/arXiv-2502.16435-b31b1b.svg)](https://arxiv.org/abs/2502.16435)

## 👁️Overview

This repository contains the official implementation of **VisFactor**, a novel benchmark derived from the Factor-Referenced Cognitive Test (FRCT) that digitizes 20 vision-centric subtests from established cognitive psychology assessments. Our work systematically investigates the gap between human visual cognition and state-of-the-art Multimodal Large Language Models (MLLMs).

## 🎯 Key Features

- **Comprehensive Evaluation**: 4 core domains of human visual cognition
  - **Visualization and Spatial Processing**: Mental rotation, spatial relations
  - **Perceptual and Closure**: Figure-ground discrimination, pattern completion
  - **Memory**: Visual working memory, recognition tasks
  - **Reasoning**: Abstract visual reasoning, analogical thinking
- **Extensive Model Coverage**: 20 frontier MLLMs from GPT, Gemini, Claude, LLaMA, Qwen, and SEED families
- **Rigorous Assessment**: Based on well-established psychometric tests (FRCT)

## 📈 Leaderboard

![VisFactor Leaderboard](./Leaderboard.jpg)

## 🚀 Quick Start

> **Note**: This evaluation framework is built on [VLMEvalKit](https://github.com/open-compass/VLMEvalKit/tree/main). For detailed information beyond this guide, please refer to their repository. We extend our sincere gratitude to the VLMEvalKit team for their excellent work.

### Installation

```bash
git clone https://github.com/CUHK-ARISE/VisFactor.git
cd VisFactor
pip install -r requirements.txt
```

### Preparation

1. **Download the VisFactor dataset**

   ```bash
   mkdir -p ~/LMUData
   cd ~/LMUData
   # Download files will be placed here
   ```

   Place `VisFactor.tsv` and `VisFactor_CoT.tsv` in this directory.

2. **Configure API credentials**

   ```bash
   cd VisFactor/
   vim .env  # or use any text editor
   ```

   Example `.env` configuration:

   ```
   # OpenAI
   OPENAI_API_KEY=your_openai_key
   OPENAI_API_BASE=https://api.openai.com/v1
   
   # Google
   GOOGLE_API_KEY=your_google_key
   
   # Other Services
   STEPAI_API_KEY=your_stepai_key
   REKA_API_KEY=your_reka_key
   GLMV_API_KEY=your_glmv_key
   SENSENOVA_API_KEY=your_sensenova_key
   MOONSHOT_API_KEY=your_kimi_key
   DOUBAO_VL_KEY=your_doubao_key
   
   # Hunyuan-Vision
   HUNYUAN_SECRET_KEY=your_hunyuan_key
   HUNYUAN_SECRET_ID=your_hunyuan_id
   
   # Deployment Services
   CW_API_BASE=your_congwang_base
   CW_API_KEY=your_congwang_key
   LMDEPLOY_API_BASE=your_lmdeploy_base
   ```

### Evaluation

#### Standard Evaluation

```bash
python3 run.py --data VisFactor --model GeminiPro2-5 --verbose
```

#### Chain-of-Thought (CoT) Evaluation

```bash
python3 run.py --data VisFactor_CoT --model GeminiPro2-5 --verbose
```

### Command Arguments

| Argument      | Type      | Default  | Description                                                  |
| ------------- | --------- | -------- | ------------------------------------------------------------ |
| `--model`     | list[str] | required | VLM names supported in VLMEvalKit (see `supported_VLM` in `vlmeval/config.py`) |
| `--mode`      | str       | 'all'    | Evaluation mode: 'all' (inference + evaluation) or 'infer' (inference only) |
| `--api-nproc` | int       | 4        | Number of threads for API requests                           |
| `--work-dir`  | str       | '.'      | Directory to save evaluation results                         |
| `--reuse`     | flag      | False    | Use previously generated results if available                |

## ⚙️Generate testcases

We also provide a script to automatically generate some test cases, including CF1-3, CS1-3, MA1, S1-2, SS3, VZ1-2.

First, prepare some images:

```bash
mkdir visfactor/Collected_Figures
```

Place your images in this folder, then run the script to generate new questions:

```bash
cd visfactor
python3 generate_images.py
```

## 📄 Citation

If you find VisFactor useful in your research, please cite our paper:

```bibtex
@article{huang202human,
  title={Human Cognitive Benchmarks Reveal Foundational Visual Gaps in MLLMs},
  author={Huang, Jen-Tse and Dai, Dasen and Huang, Jen-Yuan and Yuan, Youliang and Liu, Xiaoyuan and Wang, Wenxuan and Jiao, Wenxiang and He, Pinjia and Tu, Zhaopeng and Duan, Haodong},
  journal={arXiv preprint arXiv:2502.16435},
  year={2025}
}
```
