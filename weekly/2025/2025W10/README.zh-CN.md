# 2025 年第 10 周技术阅读汇总

by @corenel (Yusu Pan) and LLMs

以下为 2025 年 第 10 周（3 月 3 日至 3 月 9 日）期间我所阅读或者输入的内容。为简洁起见，仅列出标题、URL 以及 LLM 生成的概要，以供有兴趣者阅读，进一步的分析与反思不在此赘述。

- [2025 年第 10 周技术阅读汇总](#2025-年第-10-周技术阅读汇总)
  - [专题](#专题)
    - [Mac Studio (M4 Max or M3 Ultra)](#mac-studio-m4-max-or-m3-ultra)
    - [QwQ-32B](#qwq-32b)
    - [Manus](#manus)
  - [有趣的事与物](#有趣的事与物)
    - [生成式人工智能](#生成式人工智能)
    - [学术研究](#学术研究)
      - [语言模型](#语言模型)
      - [生成式模型](#生成式模型)
      - [自动驾驶](#自动驾驶)
      - [目标检测与跟踪](#目标检测与跟踪)
      - [语义分割](#语义分割)
      - [场景重建](#场景重建)
      - [深度估计](#深度估计)
      - [其他论文](#其他论文)
    - [软件与开发](#软件与开发)
    - [项目与团队管理](#项目与团队管理)
    - [知识管理](#知识管理)
    - [ACGN](#acgn)
    - [播客](#播客)

## 专题

### Mac Studio (M4 Max or M3 Ultra)

> TL;DR: 512 GB 统一内存的 Mac Studio (M3 Ultra) 的性价比高于之前讨论的 NVIDIA Project DIGITS (128 GB)、OrangePi AI Studio Pro (192 GB) 等，生态也完善，有需求可以购买用来个人部署超大规模的 LLMs（并发不行），特别是 MoE 模型（如 DeepSeek V3/R1）。但是需要考虑是否真的需要如此规模的模型，是否更小尺寸的模型（如 QwQ-32B）也能满足需求，以及是否真的需要本地部署。

Mac Studio M3 Ultra 凭借其 512GB 统一内存和优化的性能，正成为本地部署大语言模型的重要选择。在各种高性能计算设备中，它究竟能否胜任 AI 开发者日益增长的需求？

M3 Ultra 的出现引发了对本地部署大模型可能性的重新思考。虽然苹果官方确认 M4 Max 芯片不具备 UltraFusion 技术，暗示 M4 Ultra 可能缺席，但 M3 Ultra 凭借巨大的统一内存和相对实惠的每 GB 成本，仍然展现出独特价值。

据 EXO Labs 测试，两台 M3 Ultra 512GB 设备通过 Thunderbolt 5 连接，可以运行完整版 DeepSeek R1（8-bit）模型，实现 20 token/s 的速度。而在成本效益方面，M3 Ultra 的 512GB 内存相比 NVIDIA Project DIGITS（128GB）和 OrangePi AI Studio Pro（192GB）等方案更具吸引力。

值得一提的是，RTX4090 的改装版本也在悄然崛起，96GB 显存版本预计 5 月份出货，标价约 ¥29800，而 48GB 版本则已有现货，售价约 ¥23000。

- [No M4 Ultra Chip? Apple Confirms the M4 Max Chip Lacks UltraFusion](https://www.macrumors.com/2025/03/05/apple-confirms-m4-max-lacks-ultrafusion/)： 苹果公司不太可能推出 M4 Ultra 芯片，因为 M4 Max 芯片缺乏 UltraFusion 技术，且苹果官方暗示并非每代 M 系列芯片都有 Ultra 版本。
  - M4 Max 芯片不具备 UltraFusion 连接器，这是 M4 Ultra 缺席的最直接技术原因。
  - 苹果官方表态“并非每代都有 Ultra 芯片”，暗示了苹果芯片发布策略的转变，M4 Ultra 的缺席可能是策略调整的一部分。
  - 新款 Mac Studio 发布，提供 M4 Max 和 M3 Ultra 芯片选项，但没有 M4 Ultra，从产品层面印证了 M4 Ultra 的缺失。

  > Apple told Ars Technica that not every generation of M-series chips for Macs will include an "Ultra" chip. That seems like Apple indirectly confirming that it has no plans to release an M4 Ultra chip, and the M4 Max's lack of UltraFusion technology makes it even more likely there won't be an M4 Ultra chip.

- [10 万块的 Mac Studio M3 Ultra 实用性解析](https://phpstone.com/mac-studio-m3-ultra-preview/)：Mac Studio M3 Ultra 定位为高性能桌面工作站，虽然价格昂贵，但对于特定专业用户（尤其是 AI 开发者和内容创作者）而言，其极致性能、超大内存、高速接口和优异的软硬件生态整合，使其在特定应用场景下展现出独特的实用价值。
  - 本地 AI 开发工作站标杆: M3 Ultra 凭借 512GB 统一内存和优化的 MLX 框架，成为强大的本地 AI 开发平台，尤其适合大模型微调和本地部署，降低了 AI 开发的门槛和成本。
  - 专业内容创作的强大工具: M3 Ultra 的 CPU、GPU 和媒体引擎性能大幅提升，配合雷雳 5 接口和 macOS 生态，使其成为 8K 视频剪辑、3D 渲染等高负载内容创作的强大工具，提升专业工作流效率。
  - 苹果生态系统的价值溢价: Mac Studio M3 Ultra 的高价部分源于苹果生态系统的溢价，包括 macOS 的易用性、MLX 框架的便捷性、与专业软件的无缝集成等，这些软硬件协同优势是其“实用性”的重要组成部分。
- [EXO Labs](https://x.com/exolabs/status/1897360590987051041)

  > 2 x M3 Ultra 512GB ($18,000) connected with Thunderbolt 5 can run the full DeepSeek R1 (8-bit) with exo at 20 tok/sec.

- [Thread by @alexocheema - Opinions of The M3 Ultra 512GB Mac Studio](https://x.com/alexocheema/status/1897349404522078261)：Apple M3 Ultra Mac Studio 凭借其巨大的统一内存（512GB）和相对较低的每 GB 成本，非常适合运行大规模稀疏模型，如 DeepSeek V3/R1 等 MoE 模型。 尽管其内存带宽相对较低，但对于特定类型的 AI 模型架构（MoE 和 Modular Routing）来说，这可能是一个优势，尤其是在成本效益方面。作者认为 Apple 的时机把握得很好，并且对 Apple 能够如此迅速地推出这款产品表示赞赏。
  - Apple M3 Ultra Mac Studio 凭借其 512GB 大内存和低每 GB 成本，成为运行大规模稀疏激活模型（如 MoE 模型）的经济高效的本地解决方案。
  - Apple 在硬件设计上进行了权衡，牺牲了内存带宽（导致较低的内存刷新率）以换取更大的内存容量和更低的成本，这种策略特别适合内存容量敏感型但带宽需求相对较低的稀疏激活模型。
  - 未来的 AI 硬件发展趋势可能更加定制化，需要根据不同模型架构的特点进行软硬件协同优化，而 M3 Ultra 的设计思路为这种趋势提供了一个案例。

  > The M3 Ultra 512GB Mac Studio fits perfectly with massive sparse MoEs like DeepSeek V3/R1. 2 M3 Ultra 512GB Mac Studios with
  >
  > @exolabs is all you need to run the full, unquantized DeepSeek R1 at home.
  >

最近还有 RTX4090 改 96GB 显存（48GB 则是去年就有了）的传言与测试：

- [青龍聖者 on X: "4090 96gb verify."](https://x.com/bdsqlsz/status/1898307273967145350)
- 96GB 的需要定制驱动（改 48GB 的不需要）
- 厂家（华锐科技工厂）在闲鱼上据称 5 月份出货，96GB 当前标价 ¥29800（不确定是否为实际价格），48GB 版本现货则是 ¥23000

### QwQ-32B

> TL;DR: 总体而言与 `QwQ-Max-Preview` 的 Thinking 能力相近，能够比较好地解决用来测试的问题（历史事件核实与文言文撰写、社交媒体发文意图推断、中等难度 C++ 代码纠错等）。考虑到仅有 32B，非常适宜于本地部署。但是在推理能力上与 o1 pro、DeepSeek R1 等相比还有差距。

QwQ-32B 模型的发布标志着开源大模型的进一步突破，尤其在推理能力方面表现出色。这一模型展现了哪些亮点？

QwQ-32B 是千问团队基于强化学习技术打造的 32B 参数推理模型，其性能可与拥有 6710 亿参数（实际激活 370 亿）的 DeepSeek-R1 媲美。测试表明，它在解决历史事件核实、文言文撰写、社交媒体意图推断以及中等难度 C++ 代码纠错等任务上表现优异。

虽然与 Claude 3.7 Sonnet、o1 pro、DeepSeek R1 等顶级模型相比仍有差距，但考虑到其仅有 32B 参数规模，性价比极高。尤为可喜的是，QwQ-32B 几乎与线上 Qwen-2.5-Max-Thinking-QwQ-Preview 性能相当（仅差 0.2 分），表明千问此次开源的确是线上同等水平的版本。

对于本地部署需求的用户而言，QwQ-32B 目前是单机能部署的最具性价比的中文模型之一，社区已有 unsloth 等工具提供的优化部署方案可供参考。

- [[初步体验 QwQ-Max-Preview]]
- [QwQ-32B: Embracing the Power of Reinforcement Learning](https://qwenlm.github.io/blog/qwq-32b/)

  > 大规模强化学习（RL）有潜力超越传统的预训练和后训练方法来提升模型性能。近期的研究表明，强化学习可以显著提高模型的推理能力。例如，DeepSeek R1 通过整合冷启动数据和多阶段训练，实现了最先进的性能，使其能够进行深度思考和复杂推理。这一次，我们探讨了大规模强化学习（RL）对大语言模型的智能的提升作用，同时很高兴推出我们最新的推理模型 QwQ-32B。这是一款拥有 320 亿参数的模型，其性能可与具备 6710 亿参数（其中 370 亿被激活）的 DeepSeek-R1 媲美。这一成果突显了将强化学习应用于经过大规模预训练的强大基础模型的有效性。此外，我们还在推理模型中集成了与 Agent 相关的能力，使其能够在使用工具的同时进行批判性思考，并根据环境反馈调整推理过程。我们希望我们的一点努力能够证明强大的基础模型叠加大规模强化学习也许是一条通往通用人工智能的可行之路。
  >
  > 我们在冷启动的基础上开展了大规模强化学习。在初始阶段，我们特别针对数学和编程任务进行了 RL 训练。与依赖传统的奖励模型（reward model）不同，我们通过校验生成答案的正确性来为数学问题提供反馈，并通过代码执行服务器评估生成的代码是否成功通过测试用例来提供代码的反馈。随着训练轮次的推进，这两个领域中的性能均表现出持续的提升。在第一阶段的 RL 过后，我们增加了另一个针对通用能力的 RL。此阶段使用通用奖励模型和一些基于规则的验证器进行训练。我们发现，通过少量步骤的通用 RL，可以提升其他通用能力，同时在数学和编程任务上的性能没有显著下降。

- [Qwen on X](https://x.com/Alibaba_Qwen/status/1897366093376991515)

  > Qwen2.5-Plus + Thinking (QwQ) = QwQ-32B .

- [A few hours with QwQ and Aider - and my thoughts](https://www.reddit.com/r/LocalLLaMA/comments/1j4p3xw/a_few_hours_with_qwq_and_aider_and_my_thoughts/)

  > Those benchmarks beating Deepseek R1 (full fat) are definitely bogus. This model is not in that tier. But it's basically managed to become three iterative prompts to Qwen32B and Qwen-Coder32B in a single prompt, which is absolutely incredible. I think a lot of folks will get use out of this model.

- [Recommended settings for QwQ 32B](https://www.reddit.com/r/LocalLLaMA/comments/1j4p1fb/recommended_settings_for_qwq_32b/)

  > See [generation_config.json](https://huggingface.co/Qwen/QwQ-32B/blob/main/generation_config.json):
  >
  > ```json
  > {
  >   "repetition_penalty": 1.0,
  >   "temperature": 0.6,
  >   "top_k": 40,
  >   "top_p": 0.95
  > }
  > ```

- [karminski-牙医](https://x.com/karminski3/status/1897776454647288222)

  > Qwen-QwQ-32B-BF16 目前测试得分为 278.9 分（图 1），在榜单中超过了 DeepSeek-V3, 距离 DeepSeek-R1 还比较远。
  >
  > 但是！距离线上的 Qwen-2.5-Max-Thinking-QwQ-Preview 仅差 0.2 分！这意味着千问这次开源的的确就是线上水平的版本！（性能类似 [http://chat.qwen.ai](http://chat.qwen.ai) 进去后点击左下角的 Thinking (QwQ)）
  >
  > 也就是说 QwQ-32B 目前是我们单机能部署的最具性价比的模型了！不愧是你千问！续写了 Qwen-coder 的传奇！

- [Tutorial: How to Run QwQ-32B effectively | Unsloth Documentation](https://docs.unsloth.ai/basics/tutorial-how-to-run-qwq-32b-effectively)
- [Structured outputs with QwQ 32B](https://www.boundaryml.com/blog/qwq-32b-function-calling)
- [Aider polyglot 测试](https://x.com/paulgauthier/status/1898063999553642635)

  > QwQ 32B as architect with Qwen 2.5 Coder Instruct as editor scored 26% on the aider polyglot benchmark. This is a step up from QwQ 32B alone. QwQ+Coder also had no editing errors, versus QwQ alone erroring on 1/3 of tasks.

- [Prompts for QwQ-32B](https://www.reddit.com/r/LocalLLaMA/comments/1j4v3fi/prompts_for_qwq32b/)

  > 3 options for QwQ system prompt: Low/Medium/High Reasoning Effort

### Manus

> TL;DR: 并不新鲜，谨慎观望，没有太深的护城河。

Manus 作为一款备受关注的新型 AI 助手，引发了关于 Agent 产品竞争优势的深度讨论，但它真正的护城河究竟在哪里？

Manus 的爆火表明市场对通用 Agent 产品有着强烈需求，但其技术壁垒可能并不如想象的那么高。从交互角度看，Manus 确实具有创新性，能降低用户使用门槛，但其技术架构相对容易被分析和复制，短期内难以形成技术壁垒。

业内专家指出，Agentic AI 产品的持久竞争优势并非仅来自工具数量或 AI 智能的堆砌，而是建立在工具、数据和智能三个维度的 " 复利效应 " 之上。尤其是数据层面的复利效应，以及基于数据沉淀之上的知识管理和组织能力，才是构建长期且难以复制的护城河的关键。

社区反应迅速，已有 autoMate、OpenManus 和 OpenHands 等开源替代项目正在涌现，这进一步佐证了技术壁垒的有限性。对于创业团队而言，抢占生态位和快速迭代可能是更重要的策略。

- [Manus爆火的背后，Agentic AI产品如何构筑持久的竞争优势？](https://grapeot.me/manus.html)：Agentic AI 产品的持久竞争优势并非仅仅来自于工具数量或 AI 智能的堆砌，而是构建在工具、数据和智能三个维度上的“复利效应”之上。其中，尤其以数据层面的复利效应，以及基于数据沉淀之上的知识管理和组织能力，是构建长期且难以复制的护城河的关键。最终胜出的企业将是那些能够理解并适应 AI 与人类共进化模式，建立可持续协作机制的公司，而不仅仅是拥有最强技术的公司。
  - Agentic AI 的竞争优势源于复利效应：  工具、数据和智能三个维度的复利效应共同构筑了 Agentic AI 产品的核心竞争力，而非单一的技术突破。
  - 数据和知识管理是持久护城河：  在工具和智能层面易被复制的情况下，数据积累、知识外化以及基于此形成的组织能力，才是构建长期竞争壁垒的关键。
  - AI 与人类共进化是未来趋势：  Agentic AI 的竞争最终将演变为组织适应 AI 时代的能力竞争，理解并建立 AI 与人类共进化协作机制的企业将占据优势。
- [Manus 的护城河在哪里？](https://baoyu.io/blog/where-is-manus-moat)：Manus 这款 AI 产品在用户交互方面具有显著创新，但由于当前模型和数据的限制，它目前缺乏真正的护城河。  作者认为，虽然 Manus 在交互设计上令人惊艳，但其技术实现原理相对容易被分析和模仿，长期的竞争优势将取决于其能否在模型能力、数据积累以及用户体验上建立起壁垒。
  - 交互创新是亮点，但技术实现易被模仿。 Manus 的交互方式令人惊艳，降低了用户使用门槛，但其技术架构相对容易被分析和复制，短期内难以形成技术壁垒。
  - 护城河需从模型、数据和用户体验多维度构建。  AI 产品的长期竞争优势需要依靠模型能力、数据积累和独特的用户体验来构建护城河，单一的交互创新不足以支撑长期发展。
  - 抢占生态位和快速迭代是重要策略。  在 AI 早期发展阶段，快速推出产品，抢占市场生态位，并通过持续迭代优化用户体验和积累数据，是构建长期竞争优势的关键策略 (“卡生态位” 观点)。
- [Thread by @xiaokedada](https://x.com/xiaokedada/status/1897552294616674767)

    > 虽然没有 manus 邀请码，但是从 [manus.im](https://manus.im/usecases) 也能一览大概。我的一些碎碎的想法：
    >
    > 1. 一个很棒的产品，在通用 Agent 上市面上其实没有太多可用的产品，比较多的还是 Coding Agent 这类垂直产品，但 Coding Agent 毕竟面向普通用户。交互形式上面向普通用户做了形式上的创新。
    >
    > 2. ChatGPT 的自由画布其实有点通用 Agent 的形态，如果做好的话。
    >
    > 3. 本质上可能还是没离开 Lilian 的这张图（如果你对 Agent 有所了解的话）。底层技术上没有太多创新，更多还是增强工具能力和交互形态。Agent 的另一种思路是 RL based Agent，就是 OpenAI Operator 这种，通过 RL 提升 Tool Use 的能力，这完全源自于大语言模型自身，manus 看来并不是这种途径。
    >
    > 4. 有个很有意思的点，manus 每次操作前会列出一个清单，然后完成一个 todo 之后回顾这个 todo 完成后续的内容，有点像 Agent + workflow 的新范式，而且它把这个过程公开出来了，更觉得 Agent 是个人了（学的 DeepSeek?）。但这种方式也不是独创的，比如 windsurf 每次操作前，都会强制 Analyze 当前目录一样。
    >
    > 5. Agent 对大多数人来说，处于不了解、没听说过的状态。我相信今天每个 Agent 产品的一小步，都是未来的一大步。

开源替代：

- [OWL (Optimized Workforce Learning)](https://github.com/camel-ai/owl)
- [autoMate](https://github.com/yuruotong1/autoMate)
- [OpenManus](https://github.com/mannaandpoem/OpenManus)
- [OpenHands](https://github.com/All-Hands-AI/OpenHands)

商业竞品：

- [Flowith Oracle Mode](https://doc.flowith.io/oracle-mode-agent-mode/about-oracle-mode)

## 有趣的事与物

### 生成式人工智能

生成式 AI 技术不断突破边界，新的应用场景和工具层出不穷，如何把握其中的关键发展？

olmOCR 的出现解决了 PDF 文档内容提取和线性化的难题，为大规模利用 PDF 文档数据训练语言模型开辟了新路径。基于 Qwen2-VL-7B-Instruct 微调而来，它的开源使学术界和工业界都获得了宝贵资源。

在 AI 应用认知方面，《AI 不会吃掉你》一文提出了重要观点：AI 应被视为工具，一种“劳保用品”，帮助人类从重复性的“麻烦”中解放出来。真正的价值和安全感来源于自身内在的认知和解决问题的能力，而非对 AI 威胁的恐慌。

“Deep Research”作为热门概念被各大公司竞相推广，但其技术本质其实是“报告生成系统”——接受用户查询，使用 LLM 作为代理来迭代搜索和分析信息，并生成详细报告。文章将实现方式分为未经训练的 DAG 和 FSM 方法，以及经过训练的端到端和大型推理模型方法。

其他值得注意的进展包括 FlowDown（AI 对话客户端应用）、LettuceDetect（RAG 幻觉检测工具）、Aya Vision 8B/32B（23 种语言的多模态视觉模型）以及 Wan2.1 与 HunyuanVideo-I2V 等视频生成模型。

- [olmOCR - Unlocking Trillions of Tokens in PDFs with Vision Language Models](https://arxiv.org/html/2502.18443v1)：olmOCR 有效地解决了 PDF 文档内容提取和线性化的难题，为大规模利用 PDF 文档数据训练语言模型开辟了新的途径，并且其开源特性和低成本使其具有广泛的应用价值。

  - PDF 文档是未被充分利用的巨大文本数据宝藏： PDF 文档蕴含着数万亿 tokens 的高质量文本数据，但由于格式复杂性，现有工具难以有效提取和利用。
  - olmOCR 结合 VLM 和 “文档锚定” 技术，实现了低成本、高效、高质量的 PDF 文本线性化：  olmOCR 通过创新的 “文档锚定” 技术，有效提升了 VLM 在 PDF 文本提取方面的性能，并实现了远超其他工具的成本效益。
  - 开源 olmOCR 工具包和数据集，推动 PDF 文档理解领域的研究和应用：  olmOCR 工具包、`olmOCR-7B-0225-preview` 模型和 `olmOCR-mix-0225` 数据集的开源，为学术界和工业界提供了宝贵的资源，促进了 PDF 文档理解技术的普及和发展。
  - 备注：
    - 基于 Qwen2-VL-7B-Instruct 微调而来，可以与 Qwen2.5-VL 以及 Mistral OCR 对比
    - 注意其 [Usage](https://huggingface.co/allenai/olmOCR-7B-0225-preview#usage) 指出模型需要指定格式的输入与经过处理后的提示词

- [AI 不会吃掉你](https://roriri.one/2025/03/04/ai-is-not-eating-you/)：AI 不会取代或“吃掉”你，对 AI 产生的焦虑感很大程度上是人为营销制造的，而真正的价值和安全感来源于自身内在的认知和对问题的解决能力。AI 应该被视为一种工具，一种 “劳保用品”，帮助人类从重复性的 “麻烦” 中解放出来，从而更好地专注于创造性的 “问题” 和 “课题”。 核心在于保持前额叶 “开机”，进行理性思考，而非被情绪化的营销手段所裹挟。

  - AI 不是威胁，而是工具：  AI 不会 “吃掉” 你，不必过度恐慌。它本质上是一种工具，可以被人类利用来解决问题，提升效率，解放创造力。应该理性看待 AI，而非将其妖魔化。
  - 警惕 “AI 焦虑” 营销，保持理性思考：  市场上存在大量贩卖 “AI 焦虑” 的营销手段，旨在利用人们的恐惧进行牟利。 应该保持警惕，运用理性思考，不被情绪化营销所裹挟，做出明智的判断和决策。
  - 内在价值和意义的追寻才是核心：  真正的价值和安全感来源于自身内在的认知、能力和对问题的解决能力，以及对自身价值和意义的追寻。 AI 无法取代这种内在的价值感。 应该关注自身价值的提升和内在需求的满足，而非过度关注外部的 “AI 威胁”。

- [The Differences between Deep Research, Deep Research, and Deep Research](https://leehanchung.github.io/blogs/2025/02/26/deep-research/)：“Deep Research” 作为一个新兴的热门概念，目前被广泛宣传和应用，但其定义和技术实现方式并不清晰。文章旨在通过技术实现的视角，区分不同类型的“Deep Research”，并澄清围绕这一概念的炒作，回归其本质——报告生成系统。  作者认为，与其说是全新的突破，不如说是对过去几年 AI 工程领域中“报告生成”概念的重新包装和营销。

  - “Deep Research” 概念的兴起：  2024 年底至 2025 年初，Google (Gemini 1.5 Deep Research)、OpenAI (Deep Research)、Perplexity (Deep Research)、DeepSeek、阿里巴巴 (Qwen)、xAI 等多家公司相继推出或宣传了“Deep Research” 或 “Deep Search” 功能。
  - “Deep Research” 定义的模糊性： 尽管各家公司都在推广 “Deep Research”，但对于其具体含义和技术实现，业界并没有统一的清晰定义。许多开源实现也涌现出来，进一步加剧了概念的混淆。
  - “Deep Research” 的本质是报告生成：  文章通过分析各家公司的宣传语，提炼出 “Deep Research” 的核心定义：“深度研究是一个报告生成系统，它接受用户查询，使用大型语言模型（LLM）作为代理来迭代搜索和分析信息，并生成详细的报告作为输出。” 在自然语言处理 (NLP) 领域，这实际上就是 “报告生成” (report generation)。
  - “Deep Research” 的多种实现方式： 文章将 “Deep Research” 的技术实现分为未经训练的 DAG 和 FSM 方法，以及经过训练的端到端和大型推理模型方法，并详细分析了每种方法的特点和优缺点，为理解 “Deep Research” 的技术本质提供了清晰的框架。

- [FlowDown](https://flowdown.ai/en-US) ：A blazing fast and smooth client app for AI conversations. Switch between AI services or use local models on your device.

  - 备注：
    - 仅 LLM API Client 而论，macOS 可考虑 [ChatWise](https://chatwise.app/)，Windows 用户可考虑 [Cherry Studio](https://github.com/CherryHQ/cherry-studio)，网页版可考虑 [Open WebUI](https://github.com/open-webui/open-webui)。
    - 本地运行则可考虑 [LM Studio](https://lmstudio.ai/) 或 [Ollama](https://ollama.com/)，或者直接使用 llama.cpp 或 MLX。实际部署则使用 [vLLM](https://github.com/vllm-project/vllm) 与 [SGLang](https://github.com/sgl-project/sglang)。
    - 量化模型，GGUF 可考虑使用 [unsloth](https://huggingface.co/unsloth)、[bartowski](https://huggingface.co/bartowski)，MLX 则是 [mlx-community](https://huggingface.co/mlx-community) 的版本。

- [New Yorker Opinion - The Government Knows A.G.I. Is Coming](https://www.nytimes.com/2025/03/04/opinion/ezra-klein-podcast-ben-buchanan.html)：通用人工智能 (AGI) 很可能在未来两到三年内到来，并且美国政府（包括拜登政府和特朗普政府）对此有所认识，正在尝试为迎接 AGI 的到来做准备。  文章强调了 AGI 带来的巨大机遇与挑战，尤其是在国家安全、经济竞争和劳动力市场方面，并呼吁社会各界，特别是政府部门，认真思考并制定应对策略。

  - 备注：中文翻译见 [此网页](https://baoyu.io/translations/ezra-klein-podcast-ben-buchanan.html)，文章仅能代表前拜登政府 AI 顾问 Ben Buchanan 的观点。

- [Cursor+Claude 3.7 Sonnet一段话生成高保真app原型图的提示词](https://x.com/AlchainHust/status/1896878623539573023) 以及 [使用建议](https://x.com/manateelazycat/status/1897344213479776361)

  - 备注：需要模型 + 范例 + 后期自行调整
  - 使用 Claude 3.7 Sonnet 的例子还有 [别再用AI写垃圾代码！4个技巧帮你用AI写出漂亮炫酷的应用](https://mp.weixin.qq.com/s/tUOAfd4OI56QxD94-0PPKw)

- [LettuceDetect](https://github.com/KRLabsOrg/LettuceDetect) is a lightweight and efficient tool for detecting hallucinations in Retrieval-Augmented Generation (RAG) systems. It identifies unsupported parts of an answer by comparing it to the provided context. The tool is trained and evaluated on the [RAGTruth](https://aclanthology.org/2024.acl-long.585/) dataset and leverages [ModernBERT](https://github.com/AnswerDotAI/ModernBERT) for long-context processing, making it ideal for tasks requiring extensive context windows.

- [Aya Vision 8B/32B](https://huggingface.co/collections/CohereForAI/c4ai-aya-vision-67c4ccd395ca064308ee1484)：Aya Vision is a state-of-the-art family of vision models that brings multimodal capabilities to 23 languages.

- [Wan2.1](https://github.com/Wan-Video/Wan2.1) 与 [HunyuanVideo-I2V](https://github.com/Tencent/HunyuanVideo-I2V)：就简单测试而言 Wan2.1 的图像生成视频的指令遵循强于 Hunyuan Video I2V，且据称在特定提示词下不用微调也能生成 NSFW 的内容。

- [LLM Quantization Comparison](https://dat1.co/blog/llm-quantization-comparison)：量化是高效部署大型语言模型的关键技术，它能在降低内存占用和提高推理速度的同时，不可避免地会牺牲一定的模型质量。 文章进一步指出，不同的量化程度对模型性能的影响各异，并且这种影响在不同的任务类型和硬件平台上也会有所不同。  文章最终结论强调，选择合适的量化策略需要在速度、内存和精度之间进行权衡，并且需要根据具体的应用场景和硬件条件进行优化选择。

  - 量化是 LLM 部署的关键，但精度与效率存在权衡： 文章明确指出量化是高效部署大型语言模型的必要手段，它能够显著降低内存占用和提高推理速度。然而，更低的量化精度通常会导致模型性能的下降，需要在精度和效率之间进行权衡。
  - 量化效果受任务类型和模型规模影响：  实验结果表明，不同量化级别对不同任务类型的影响程度不同。例如，在 Coding 和 Data Analysis 任务中，低比特量化导致性能显著下降，而在 Reasoning 任务中，大模型在重度量化下仍能表现出色。这说明量化策略的选择需要考虑具体的任务类型和模型规模。
  - 4-bit 量化是当前较优的平衡点，硬件平台影响量化效果：  文章结论指出，4-bit 量化格式在精度和效率之间提供了良好的平衡，是目前较为流行的选择。同时，硬件平台对量化模型的推理速度有显著影响，服务器级 GPU 在处理大型量化模型时更具优势。这提示我们在实际部署量化模型时需要考虑硬件平台的限制和优化。
  - 备注：如果使用 unsloth 转换的模型，体感 Q5 在不显著增加显存占用的情况下生成结果优于 Q4

- [A Practical Guide to Implementing DeepSearchDeepResearch](https://jina.ai/news/a-practical-guide-to-implementing-deepsearch-deepresearch/)：DeepSearch 和 DeepResearch 代表了 2025 年搜索技术的新标准，它们通过迭代的“搜索 - 阅读 - 推理”循环，以及“测试时计算”的理念，显著提升了搜索的准确性和深度，标志着搜索范式从传统快速但浅层的检索，转向重视精度和召回率，用户也逐渐接受更长的等待时间以换取更高质量的结果。DeepSearch 是一个原子构建块，通过持续迭代搜索、阅读网页和推理，直至找到最佳答案或超出预算。 DeepResearch 则建立在 DeepSearch 之上，专注于生成高质量、可读性强的长篇研究报告，它将报告分解为多个章节，并对每个章节应用 DeepSearch，最后整合所有章节以提高整体连贯性。

  - DeepSearch/DeepResearch 代表了搜索范式的转变： 从快速浅层检索转向重视精度和召回率的深度探索，用户接受更长的等待时间以换取更高质量的结果。
  - “测试时计算” 是关键驱动力：  通过在推理阶段投入更多计算资源，例如 CoT 和 Wait-injection，提升 LLM 的推理能力，是 DeepSearch/DeepResearch 的核心技术理念。
  - 迭代式 “搜索 - 阅读 - 推理” 循环是 DeepSearch 的核心机制： 通过不断迭代搜索、阅读网页和推理，直至找到最佳答案或超出预算，克服了传统 RAG 和多跳 QA 的局限性。

- [交替直接差分学習法ADDifT(Alternating Direct Difference Training)の解説｜hakomikan](https://note.com/hakomikan/n/n716397e39d56#7f0f4d60-3596-4137-a7e2-1b8ac7ec9411)：提出了名为交替直接差分学习法 (ADDifT) 的新型 LoRA 学习方法，该方法能够显著缩短差分学习的训练时间，并支持多图集同步学习，且具有应用于多种扩散模型的潜力。  文章旨在介绍 ADDifT 方法的原理、优势以及初步实验结果，并展望其未来的发展方向。

  - 直接差分学习 (Direct Difference Training)：  ADDifT 直接学习两张图像噪声预测的差异，避免了传统方法学习图像绝对内容带来的冗余和低效。
  - 交替学习 (Alternating Training)：  通过正反两个方向的差分学习交替进行，抵消了非目标差异的学习，提高了学习的精确性。
  - Scheduled Random Timesteps：  针对小步数训练中 Timesteps 分布不均的问题，提出有计划的随机 Timesteps 选择策略，提升了训练的稳定性和效率。

- [とうとう現れたSDXLの後継？CogView4-6Bを解説する](https://zenn.dev/discus0434/articles/cogview4-6b-commentary)：文章最主要的论点是 CogView4-6B 的出现是 SDXL 之后图像生成 AI 领域的一个重大转折点，因为它是一个采用了最新技术、具有高性能，并且采用 Apache-2.0 许可的开源模型，这打破了自 Flux.1 以来图像生成 AI 领域进展缓慢且实用性受限的局面。 文章认为 CogView4-6B 不仅在技术上先进，而且在商业应用和进一步发展方面具有巨大的潜力，预示着图像生成 AI 新的开源潮流。
- [The Model is the Product  Vintage Data](https://vintagedata.org/blog/posts/model-is-the-product)：人工智能（AI）发展的下一个阶段已经到来，“模型即产品”（The model is the product）。作者认为，当前的科研和市场发展趋势都指向这个方向，即模型本身将成为核心价值和商业模式的中心，而不是仅仅作为应用程序的基础。文章指出，通用模型的无限扩展已遇到瓶颈，而面向特定任务的“观点训练”（Opinionated training）模型表现出惊人的效果，同时推理成本也在大幅下降。这些因素共同推动模型提供商向上游价值链迁移，直接构建最终产品，而非仅仅提供 API 接口。
- [prompt-optimizer](https://github.com/linshenkx/prompt-optimizer)：一款提示词优化器，助力于编写高质量的提示词。
- [Thread by @rao2z - RL is great but RL envy in LLMs may not be](https://x.com/rao2z/status/1897469961138004250?s=12&t=_TGttdSvvxvf3v4RXMA2vg)：对大型语言模型（LLMs）中强化学习（RL）作用的重新评估，并质疑其在 DeepSeek R1 等模型成功中被过分强调的可能性。 作者认为，R1 的成功可能更多地归功于其基础模型的能力和有效的奖励信号，而非 RL 本身。他进一步提出，在 R1 的情境下，RL 和监督微调（SFT）之间的区别可能不像论文中描述的那么显著，甚至可能类似于随机梯度下降（SGD）与批量梯度下降（Batch）的区别。作者还对“推理轨迹”的概念提出质疑，并探讨了 LLM 中马尔可夫决策过程（MDP）的不同形式。
- [Hallucinations (Confabulations) Document-Based Benchmark for RAG. Includes human-verified questions and answers.](https://github.com/lechmazur/confabulations)：现有的针对检索增强生成 (RAG) 的大型语言模型 (LLM) 幻觉 (Confabulation) 基准测试存在缺陷，需要更有效的方法来评估和减少 LLM 在 RAG 系统中产生幻觉的频率。  文章提出并介绍了一个新的基准测试 `confabulations`，专注于评估 LLM 在面对基于提供文档的误导性问题时，产生不存在答案（幻觉）的频率。这个基准旨在更准确地衡量 LLM 在 RAG 应用中的可靠性，并帮助优化 RAG 系统以减少幻觉。

### 学术研究

#### 语言模型

- [[Token-Efficient Long Video Understanding for Multimodal LLMs]]：提出了 STORM (Spatiotemporal TOken Reduction for Multimodal LLMs) 架构，这是一种新型的视频多模态大型语言模型架构，旨在通过引入基于 Mamba 状态空间模型的时序编码器，在图像编码器和语言模型之间有效地整合时空动态信息，从而提升模型在长视频理解任务中的性能和效率。STORM 架构及其配套的 token 压缩策略（包括训练时的时序池化、空间池化以及测试时的时序 token 采样）能够在显著降低计算成本和推理延迟的同时，在各种长视频理解基准测试中取得最先进的性能，并且优于现有方法，尤其是在 MLVU 和 LongVideoBench 基准上取得了超过 5% 的性能提升。
- [[Words or Vision Do Vision-Language Models Have Blind Faith in Text?]]：视觉 - 语言模型（VLMs）在处理视觉和文本信息时，存在“盲目信任文本”（blind faith in text）的现象。 当视觉信息和文本信息出现不一致时，VLMs 会不成比例地信任文本数据，即使文本是错误或误导性的，从而导致模型在视觉中心任务中的性能显著下降，并引发潜在的安全隐患。
  - “盲目信任文本” 导致 VLMs 在视觉中心任务中性能下降，并可能引发安全风险。尤其是在文本信息被破坏或误导时，VLMs 的准确率会显著降低，这在安全攸关的应用场景中构成潜在威胁。
  - “盲目信任文本” 现象受多种因素影响，但难以通过简单的指令或扩大模型规模完全解决。影响因素包括指令提示、语言模型大小、文本相关性、Token 顺序和单模态确定性。有监督微调 (SFT) 是一种有效的缓解策略，但仍需持续探索更根本的解决方案。
  - 备注：与之前在衣服上贴一个诸如“Don't Detect”之类的文本，或者其他对抗性的图案来欺骗目标检测模型的类似。
- [[Using GRPO to Beat o1, o3-mini and R1 at "Temporal Clue" - OpenPipe]]：通过使用 Group Relative Policy Optimization (GRPO) 强化学习方法，可以训练小型、开源的大语言模型 (LLM)，使其在逻辑推理任务（以 "Temporal Clue" 谜题为例）上达到甚至超越一些大型专有模型的性能水平，同时显著降低推理成本。 换句话说，文章证明了小型开源模型通过有效的强化学习训练，能够在特定复杂推理任务上实现媲美甚至超越大型模型的效果，且更具成本效益。
- - [[Headroom for AI development – Machine Learning (Theory)]]：当前基于 Transformer 的大型语言模型 (LLM) 虽然取得了显著的进步，但仍然存在根本性的效率低下问题，尤其是在样本效率、表征效率以及长程记忆和规划能力方面。与人类和动物相比，LLM 还有巨大的提升空间，未来的研究应该超越简单地扩展现有模型，探索更具创新性的架构和方法。
- [[ClipGrader Leveraging Vision-Language Models for Robust Label Quality Assessment in Object Detection]]：提出了一种名为 ClipGrader 的新型方法，该方法利用视觉 - 语言模型（Vision-Language Models, VLM），特别是 CLIP (Contrastive Language-Image Pre-training)，来自动且有效地评估目标检测任务中边界框标注的质量。  ClipGrader 不仅能评估类别标签的正确性，还能评估边界框的空间精确度，为大规模目标检测数据集的标注质量控制和验证提供了一个可扩展的 AI 辅助工具。
- [[ABC Achieving Better Control of Multimodal Embeddings using VLMs]]：提出了名为 ABC 的新型多模态嵌入模型，该模型通过利用视觉 - 语言模型（VLM）的骨干网络，能够更有效地融合图像特征和自然语言指令，从而实现对多模态嵌入表示的更精细控制。  作者认为，现有的基于 CLIP 的方法在处理需要用户指令或存在歧义的视觉任务时存在局限性，而 ABC 模型通过深度整合视觉和语言信息，克服了这些问题，并在多种基准测试中取得了优异的性能。 核心创新在于利用 VLM 架构实现模态间的深度交互，并通过解耦预训练和指令微调的方法，提高了模型的效率和灵活性。

#### 生成式模型

- [[Simulating the Real World A Unified Survey of Multimodal Generative Models]]：为了实现通用人工智能（AGI），模拟真实世界至关重要，而现有的多模态生成模型研究通常将不同维度（2D 图像、视频、3D、4D）视为独立领域，缺乏系统性的整合和跨维度理解。因此，本文旨在构建一个统一的框架，从数据维度增长的角度（2D -> 视频 -> 3D -> 4D）系统地综述多模态生成模型在真实世界模拟中的应用和进展，并为未来的研究提供指导。
- [[PhotoDoodle Learning Artistic Image Editing from Few-Shot Examples]]：提出了一个名为 PhotoDoodle 的新型图像编辑框架，该框架旨在通过少量样本学习艺术家的独特风格，实现照片涂鸦的自动化。PhotoDoodle 能够将装饰性元素无缝地叠加到照片上，同时保持背景的一致性和艺术风格的准确捕捉。文章强调，PhotoDoodle 解决了现有方法在照片涂鸦任务中面临的挑战，例如和谐融合、背景保护和风格高效提取。

#### 自动驾驶

- [[UniMLVG Unified Framework for Multi-view Long Video Generation with Comprehensive Control Capabilities for Autonomous Driving]]：提出了一个名为 UniMLVG (Unified Framework for Multi-view Long Video Generation) 的统一框架，用于生成具有全面控制能力的多视角长视频，特别针对自动驾驶场景。文章的核心结论是 UniMLVG 框架能够有效地生成高质量、时空一致且可控的自动驾驶场景多视角长视频，并在生成质量和条件控制方面超越了现有技术。  为了实现这一目标，UniMLVG 创新性地采用了多任务、多条件、多阶段的训练策略，并引入了显式视角建模方法。实验结果表明，UniMLVG 在 FID 和 FVD 指标上均显著优于现有方法，并在条件遵循度量上也取得了领先水平。
- [[Dur360BEV A Real-world 360-degree Single Camera Dataset and Benchmark for Bird-Eye View Mapping in Autonomous Driving]]：提出 Dur360BEV 数据集以及一个基准架构，证明仅使用单个球形摄像头即可有效生成用于自动驾驶的鸟瞰图 (BEV) 地图。  文章旨在通过减少硬件复杂性（使用单个 360 度摄像头代替多摄像头系统）来解决自动驾驶中 BEV 生成的挑战，并展示了即使在简化的传感器配置下也能实现有竞争力的性能。
  - 推出 Dur360BEV 数据集， 这是首个大规模真实世界单球形摄像头自动驾驶数据集，填补了现有数据集在传感器模态上的空白，为单摄像头 BEV 感知研究提供了重要资源。
  - 提出 SI2BEV 基准架构， 证明了仅使用单个球形摄像头即可有效生成用于自动驾驶的 BEV 地图，简化了硬件设置，降低了系统复杂性和成本。
  - 创新性地应用 Focal Loss 于 BEV 分割，  有效解决了 BEV 分割任务中严重的类别不平衡问题，显著提升了分割性能，为 BEV 感知模型的优化提供了新思路。
- [[Deep Height Decoupling for Precise Vision-based 3D Occupancy Prediction]]：通过引入深度高度解耦（Deep Height Decoupling, DHD）框架，可以显著提升基于视觉的 3D occupancy prediction 的精度，并达到目前最优水平。  文章认为，现有方法在 2D 到 3D 的视图转换过程中，由于未充分考虑物体的高度信息，导致特征混淆，从而限制了预测精度。DHD 框架通过显式地预测和利用高度先验知识，有效地解决了这个问题。
  - 高度解耦是关键。 传统方法在 2D-to-3D 视图转换中忽略了物体的高度分布差异，导致特征混淆，限制了预测精度。DHD 框架通过 Mask Guided Height Sampling (MGHS) 模块，将高度图解耦为多个高度区间，并进行掩码投影，实现了高度感知的特征采样，有效减少了特征混淆。
  - 协同特征聚合提升表示能力。  DHD 框架引入 Synergistic Feature Aggregation (SFA) 模块，通过通道和空间注意力机制，协同聚合基于深度和基于高度细化的特征，进一步提升了特征表示能力，实现了更精确的 occupancy prediction。
- [[HazardNet A Small-Scale Vision Language Model for Real-Time Traffic Safety Detection at Edge Devices]]：提出了 HazardNet，一个小型视觉语言模型 (VLM)，通过对预训练的 Qwen2-VL-2B 模型进行微调，并利用新创建的 HazardQA 数据集进行训练，能够在边缘设备上实现高效的、实时的交通安全事件检测，并且在性能上可以超越或媲美更大的模型，从而为改善城市交通安全和管理做出贡献。  文章强调了 HazardNet 的小规模、高效性和在边缘设备上的部署潜力，以及其在交通安全事件检测方面的优越性能。
  - HazardNet 证明了小规模 VLM 在边缘设备上进行高性能实时交通安全事件检测的可行性。  通过对 Qwen2-VL-2B 模型进行参数高效微调，HazardNet 在保持模型体积小的同时，实现了与大型模型相媲美的性能，使其非常适合资源受限的边缘设备部署。
  - HazardQA 数据集的提出填补了交通安全领域 VQA 数据集的空白，为训练和评估交通安全事件检测模型提供了新的资源。  HazardQA 数据集专注于安全关键场景，并采用问答形式的标注，能够更好地训练模型理解和推理交通安全事件。
  - 参数高效微调方法 (LoRA/QLoRA) 是在小规模 VLM 上实现高性能的关键技术。  通过仅微调少量参数，LoRA/QLoRA 显著提升了 HazardNet 的性能，同时保持了模型的效率，验证了参数高效微调方法在资源受限场景下的有效性。
- [[SegLocNet Multimodal Localization Network for Autonomous Driving via Bird’s-Eye-View Segmentation]]：提出了名为 SegLocNet 的新型多模态定位网络，该网络通过鸟瞰视角 (BEV) 语义分割，在无需 GNSS 的情况下，实现了高精度、鲁棒性强且泛化能力好的自动驾驶车辆定位。文章的核心结论是 SegLocNet 在 nuScenes 和 Argoverse 数据集上，均超越了当前最先进的定位方法，并且能够有效利用高清 (HD) 和标清 (SD) 地图，在城市环境中实现精准的自车定位。

#### 目标检测与跟踪

- [[Omnidirectional Multi-Object Tracking]]：提出了一个名为 OmniTrack 的新型全方位多目标跟踪（MOT）框架，旨在解决现有 MOT 算法在全景图像中表现不佳的问题，并在性能上达到了最先进水平。
  - 提出 OmniTrack 框架：  针对全景图像多目标跟踪的挑战，创新性地提出了 OmniTrack 框架，该框架集成了 Tracklet Management、FlexiTrack Instance 和 CircularStatE Module 三个核心组件，有效提升了全景 MOT 的性能。
  - 贡献 QuadTrack 数据集：  为了弥补全景 MOT 数据集的不足，发布了 QuadTrack 数据集，该数据集具有宽视场角、复杂运动和真实场景等特点，为全景 MOT 研究提供了新的 benchmark。
  - 达到 SOTA 性能：  通过在 JRDB 和 QuadTrack 数据集上的大量实验，证明 OmniTrack 框架在全景 MOT 任务上取得了最先进的性能，超越了现有的 E2E 和 TBD 方法。
- [[YOLO-MST Multiscale deep learning method for infrared small target detection based on super-resolution and YOLO]]：提出了一种名为 YOLO-MST 的新型红外小目标检测深度学习方法，该方法通过结合图像超分辨率技术和多尺度观测，显著提高了红外小目标检测的精度和鲁棒性。文章最终得出结论，YOLO-MST 方法在两个公开数据集（IRIS 和 SIRST）上均取得了优于现有先进方法的检测性能，有效解决了传统方法和现有深度学习方法在复杂背景和小目标检测中存在的漏检、误报和精度低等问题。
- [[Locate Anything on Earth Advancing Open-Vocabulary Object Detection for Remote Sensing Community]]：现有的开放词汇目标检测 (Open-Vocabulary Object Detection, OVD) 模型在自然图像上表现良好，但在遥感图像领域由于数据领域差距巨大而性能显著下降。为了推动遥感领域 OVD 的发展，本文提出了“地球万物定位 (Locate Anything on Earth, LAE)” 任务，并为此构建了大规模遥感开放词汇目标检测数据集 LAE-1M，以及首个针对 LAE 任务的基础模型 LAE-DINO。
- [[VoxelNextFusion A Simple, Unified and Effective Voxel Fusion Framework for Multi-Modal 3D Object Detection]]：提出了 VoxelNextFusion，一个简单、统一且有效 的体素融合框架，用于 多模态 3D 目标检测。该框架旨在解决现有基于体素的多模态 3D 目标检测方法在融合稀疏点云特征和稠密图像特征时遇到的挑战，特别是针对 远距离目标检测性能不佳 的问题。VoxelNextFusion 通过提出的 P2-Fusion (Patch-Point Fusion) 和 FB-Fusion (Foreground-Background Fusion) 模块，有效地桥接了稀疏点云和稠密图像之间的差距，显著提升了 3D 目标检测的性能，尤其是在 困难场景和远距离目标 的检测上。
  - P2-Fusion (Patch-Point Fusion) 的重要性：  文章强调了 P2-Fusion 模块在解决稀疏点云和稠密图像分辨率不匹配问题上的关键作用。通过 Patch Fusion 策略，P2-Fusion 能够更充分地利用图像的语义信息和连续性，克服了一对一投影的局限性，是性能提升的关键因素之一。
  - FB-Fusion (Foreground-Background Fusion) 的贡献：  文章指出 FB-Fusion 模块通过区分前景和背景特征，并增强前景特征，能够有效抑制背景噪声，进一步提升检测性能。FB-Fusion 模块的引入，使得 VoxelNextFusion 能够更专注于重要的目标特征，减少背景干扰，从而提高检测精度。
  - 备注：后续可能可以考虑如何更有效地利用图像的上下文信息和时间信息
- [[MI-DETR An Object Detection Model with Multi-time Inquiries Mechanism]]：现有的 DETR 类模型中级联解码器架构限制了对象查询从图像特征中学习全面信息的能力，为了充分利用图像特征以应对复杂场景下的目标检测挑战，本文提出了具有并行多时间询问 (Multi-time Inquiries, MI) 机制的新型解码器架构 MI-DETR。  MI-DETR 通过并行多时间询问机制，使对象查询能够学习更全面的信息，从而提升目标检测性能。
- [[RTGen Real-Time Generative Detection Transformer]]：提出了一个名为 RTGen (Real-Time Generative Detection Transformer) 的新型实时生成式物体检测器，它克服了传统物体检测器依赖预定义类别的限制，并且在保持高精度的同时，实现了显著的推理速度提升。RTGen 的核心创新在于将非自回归语言模型集成到物体检测解码器中，实现了物体和文本信息的并行处理，从而在速度和性能上都超越了现有方法。
- [[The Common Objects Underwater (COU) Dataset for Robust Underwater Object Detection]]：现有的陆地物体检测数据集在水下环境中的应用效果有限，因此需要专门的水下物体检测数据集来提升水下物体检测模型的性能。  为了解决这个问题，作者们创建并发布了一个新的水下物体数据集，名为 COU (Common Objects Underwater)，并证明了使用 COU 数据集训练的模型在水下物体检测任务中，比仅使用陆地数据集训练的模型表现更优。

#### 语义分割

- [[DSV-LFS Unifying LLM-Driven Semantic Cues with Visual Features for Robust Few-Shot Segmentation]]：结合大型语言模型（LLMs）驱动的语义提示与视觉特征的密集匹配，可以显著提升小样本语义分割（Few-Shot Semantic Segmentation, FSS）的鲁棒性和性能，使其在泛化到新类别和应对各种场景时表现更优异。  文章提出的名为 DSV-LFS 的框架，通过融合从 LLM 获取的语义知识和从视觉匹配得到的空间信息，克服了传统 FSS 方法在特征表示不完整和偏差方面的局限性，最终实现了最先进的性能。
  - 融合 LLM 语义知识与视觉特征匹配是提升 FSS 鲁棒性和性能的关键。  文章核心主张通过结合 LLM 提供的类别语义信息和视觉密集匹配提供的空间信息，可以克服传统 FSS 方法的局限性，显著提升模型在新类别上的泛化能力和在复杂场景下的分割精度。
  - DSV-LFS 框架通过双提示机制 (语义提示 + 视觉提示) 有效地实现了 LLM 语义知识与视觉特征的融合。  提出的 DSV-LFS 框架通过 Class Semantic Encoder 模块生成语义提示，Dense Matching Module 生成视觉提示，并使用 Prompt-based Decoder 模块进行融合和分割，形成了一个端到端的有效解决方案。
  - 实验结果表明 DSV-LFS 框架在多个基准数据集上取得了最先进的 FSS 性能，并展现了良好的跨域泛化能力。  通过在 PASCAL-5<sup>i</sup> 和 COCO-20<sup>i</sup> 数据集以及跨域场景下的实验，DSV-LFS 框架的性能显著优于现有方法，验证了其有效性和优越性。
- [[COARSE Collaborative Pseudo-Labeling with Coarse Real Labels for Off-Road Semantic Segmentation]]：提出了名为 COARSE 的半监督领域自适应框架，用于解决非结构化越野环境下的语义分割问题，尤其是在缺乏密集标注数据和只有粗略标注数据的情况下。 COARSE 框架通过结合粗略的领域内标签和密集的领域外标签，利用预训练的视觉 Transformer (DINOv2) 的强大特征提取能力，以及互补的像素级解码器 (PixelDecoder) 和补丁级解码器 (PatchDecoder)，并通过协作伪标签策略，显著提升了越野语义分割的性能和泛化能力。
  - COARSE 框架有效解决了越野语义分割中粗略标注数据利用率低的问题。 通过协作伪标签策略，结合粗略的领域内标签和密集的领域外标签，显著提升了模型性能，降低了对昂贵密集标注数据的依赖。
  - 互补解码器 (PixelDecoder & PatchDecoder) 和 DINOv2 预训练模型的结合是 COARSE 框架成功的关键。  DINOv2 提供了强大的领域泛化特征，互补解码器则从不同角度利用这些特征，并通过 disagreement 策略生成高质量伪标签。
  - 伪标签密度可以作为一种新的启发式方法，指导数据标注和模型迭代优化。  高伪标签密度区域可能指示模型预测不确定性高的区域，值得优先进行人工标注，实现更高效的数据利用和模型改进。
- [[Label-Efficient LiDAR Panoptic Segmentation]]：提出了一种名为 L3PS (Limited-Label LiDAR Panoptic Segmentation) 的新型方法，该方法能够显著降低 LiDAR 全景分割对大量标注数据的依赖，通过利用少量标注图像生成高质量的 3D 全景伪标签，并有效训练 LiDAR 分割网络，最终在标注效率和分割性能之间取得平衡。
  - 标签效率至上: 核心主张是大幅度降低 LiDAR 全景分割对昂贵且耗时的点云标注的依赖，转向更经济高效的图像标注。
  - 2D-3D 伪标签转换: 关键观点是利用先进的 2D 图像全景分割模型和预训练模型，生成高质量的 2D 伪标签，并通过投影将其转化为 3D 点云伪标签，作为训练数据的基础。
  - 几何信息驱动的 3D 细化: 关键观点是通过设计 3D 细化模块，充分利用点云的几何特性和时间序列信息，显著提升初始 3D 伪标签的质量，使其足以训练高性能的 LiDAR 分割模型。
  - 备注：与 [[OVM3D-Det - Training an Open-Vocabulary Monocular 3D Object Detection Model without 3D Data]] 的标注生成方法相似
- [[Golden Cudgel Network for Real-Time Semantic Segmentation]]：提出了 Golden Cudgel Network (GCNet)，这是一种用于实时语义分割的新型网络，旨在 同时提升性能和推理速度。GCNet 的核心创新在于其 自放大和自收缩 的特性：在训练阶段，网络扩展自身结构以增强学习能力；在推理阶段，网络收缩简化结构以提高速度，且性能几乎不受影响。这种设计克服了现有实时语义分割模型中常见的两个问题：多路径模块导致的推理速度下降以及对高性能教师模型的依赖。文章最终结论是，通过实验验证，GCNet 在 Cityscapes、CamVid 和 Pascal VOC 2012 等数据集上，在性能和速度方面均优于当前最先进的实时语义分割模型。
  - 备注：推理速度对比的表格挺详细，可供参考。
- [[BEVMOSNet Multimodal Fusion for BEV Moving Object Segmentation]]：通过融合来自摄像头、激光雷达 (LiDAR) 和雷达 (Radar) 的多模态数据，并利用多模态可变形交叉注意力 (Multimodal Deformable Cross-Attention, MDCA) 机制进行传感器融合，可以显著提升鸟瞰图 (Bird's-Eye-View, BEV) 移动物体分割 (Moving Object Segmentation, MOS) 的精度和鲁棒性，尤其是在低光照、夜间和恶劣天气条件下。
- [[Segment-Level Road Obstacle Detection Using Visual Foundation Model Priors and Likelihood Ratios]]：利用视觉基础模型 (Visual Foundation Model, VFM) (特别是 Segment Anything Model, SAM) 的分割级别特征，结合似然比 (Likelihood Ratio) 方法，能够有效且鲁棒地进行道路障碍物检测，并且在组件级别指标上优于现有的像素级别方法，同时无需手动选择阈值。
- [[RMP-SAM Towards Real-Time Multi-Purpose Segment Anything]]：提出了一种名为 RMP-SAM (Real-Time Multi-Purpose Segment Anything) 的新型实时多用途分割模型，该模型旨在解决现有分割方法在实时性和多任务通用性之间的平衡问题，并在交互式分割、全景分割和视频实例分割三个子任务上，实现了速度和精度之间的最佳权衡。
- [[Attention-Guided Integration of CLIP and SAM for Precise Object Masking in Robotic Manipulation]]：通过创新性地集成 CLIP (Contrastive Language-Image Pretraining)、SAM (Segment Anything Model) 和 Grad-CAM (Gradient-based Class Activation Mapping) 这三个先进的 AI 模型，并结合梯度注意力机制和定制数据集进行微调，可以显著提升机器人操作中物体掩膜的精度，尤其是在便利店商品识别这种特定领域内。  这种集成方法能够克服现有方法在领域特定数据上的局限性，为机器人系统提供更精确的物体掩膜输入，从而实现更准确和自适应的物体操作。

#### 场景重建

- [[EvidMTL Evidential Multi-Task Learning for Uncertainty-Aware Semantic Surface Mapping from Monocular RGB Images]]：现有的单目 RGB 图像语义表面地图构建方法常常产生过度自信的语义预测，并且受到稀疏和噪声深度感知的影响，导致地图表示不一致。为了解决这个问题，文章提出了 EvidMTL 和 EvidKimera 框架，通过引入证据多任务学习 (Evidential Multi-Task Learning) 来实现不确定性感知的语义表面地图构建，从而提高地图的准确性和一致性，并增强机器人决策的可靠性。
- [[GaussianGraph 3D Gaussian-based Scene Graph Generation for Open-world Scene Understanding]]：现有的基于 3D 高斯溅射 (3DGS) 的场景理解方法在语义分割精度和空间推理能力方面存在局限性。为了解决这些问题，文章提出了 GaussianGraph 框架，该框架通过集成自适应语义聚类和场景图生成来增强 3DGS 的场景理解能力。GaussianGraph 能够实现更精确的语义分割和更强大的空间推理，从而为复杂场景理解和交互提供更鲁棒的解决方案。
  - 备注：主要关注静态场景
- [[No Parameters, No Problem 3D Gaussian Splatting without Camera Intrinsics and Extrinsics]]：提出了一种新颖的联合优化方法，可以在无需相机内参和外参的情况下训练 3D 高斯溅射（3DGS）模型。文章旨在解决现有 3DGS 技术过度依赖精确预计算的相机参数（如焦距和相机位姿）的问题，并进一步放宽输入要求，使得仅使用图像集合即可完成高质量的场景重建和新视角合成。
  - 联合优化框架：通过联合优化相机内参、外参和 3DGS 模型参数，实现了相机参数估计和场景表示学习的协同提升，克服了传统方法中相机参数预处理的瓶颈。
  - 梯度推导和混合训练策略：理论推导了相机内参（焦距）的梯度，并将其纳入反向传播优化过程，同时引入全局轨迹信息和混合训练策略（追踪高斯核和普通高斯核），提高了训练的稳定性和精度。
- [[LiteGS A High-Performance Modular Framework for Gaussian Splatting Training]]：LiteGS 是一个高性能、模块化的 Gaussian Splatting 训练框架，它显著提升了训练效率和可用性，同时保持或提升了渲染质量。  LiteGS 通过模块化设计、优化的算法和双 API 支持，克服了传统 3DGS 实现的局限性，使其更适用于快速原型设计和生产环境。
  - 模块化设计是提升 3DGS 框架灵活性和可定制性的关键。  LiteGS 通过将渲染过程分解为模块化组件，使得用户可以更容易地进行定制和扩展，加速新算法的迭代和原型设计。
  - 针对 GPU 架构的精细化优化是提升 3DGS 训练效率的关键。  LiteGS 通过聚类、压缩、稀疏梯度、多批次归约等技术，充分利用 GPU 的并行计算能力和内存管理机制，显著提升了训练速度。
  - 双 API 支持 (Python & CUDA) 能够平衡快速原型设计和生产环境性能需求。  LiteGS 提供 Python API 用于快速实验和原型开发，CUDA API 用于性能关键的应用，满足了不同场景的需求。
- [[Evolving High-Quality Rendering and Reconstruction in a Unified Framework with Contribution-Adaptive Regularization]]：提出了一种名为 CarGS 的统一框架，通过贡献自适应正则化 (Contribution-adaptive Regularization) 有效地解决高质量渲染和精确表面重建之间的固有冲突，从而在保持实时速度和最小存储空间的同时，实现最先进的渲染质量和重建精度。  文章旨在证明，通过学习高斯基元的自适应贡献，可以构建一个高效且有效的统一模型，克服传统方法在渲染和重建之间权衡的难题。
  - 贡献自适应正则化 (Contribution-adaptive Regularization) 是解决渲染和重建统一框架中固有冲突的关键。  文章指出，现有方法在统一框架中难以兼顾渲染和重建，核心问题在于高斯基元对两项任务的贡献存在冲突。通过学习自适应贡献，可以有效缓解这种冲突，实现性能提升。
  - 提出的 CarGS 模型通过轻量级模块 (Lite-Geo) 和几何引导的密集化策略，在统一框架下实现了 SOTA 的渲染和重建性能，同时保持了高效性。  CarGS 的核心贡献在于将几何正则化知识融入紧凑的 MLP 中，并结合几何引导的密集化策略，最终在性能、效率和存储空间上都取得了显著的优势。
  - covariance (协方差) 是高斯基元贡献中对几何重建至关重要的属性。  通过实验分析，文章揭示了 covariance 在几何重建中的关键作用，这为 CarGS 模型设计针对 covariance 的贡献自适应正则化模块提供了理论依据。
- [[DoF-Gaussian Controllable Depth-of-Field for 3D Gaussian Splatting]]：提出了 DoF-Gaussian 框架，这是一种用于 3D 高斯 Splatting (3D-GS) 的可控景深 (Depth-of-Field, DoF) 方法，旨在解决现有 3D-GS 方法无法有效处理浅景深输入图像和缺乏可控景深效果的问题。  文章的核心结论是，DoF-Gaussian 通过引入基于几何光学原理的透镜成像模型，并结合场景深度先验调整和散焦到聚焦的自适应策略，能够有效地从浅景深输入图像中重建场景，并实现可控的景深效果，同时保持了 3D-GS 的实时渲染效率。实验结果表明，DoF-Gaussian 在散焦去模糊和可控景深渲染方面优于现有方法。
  - 透镜成像模型是实现可控景深的关键。  文章明确指出，从针孔相机模型到透镜相机模型的转变是实现 DoF 控制的核心。通过参数化光圈大小和焦距等透镜参数，并使其可学习，DoF-Gaussian 能够模拟真实的景深效果，并允许用户交互式地调整景深参数，这超越了以往 3D-GS 方法的能力。
  - 深度先验和散焦到聚焦自适应策略是提升性能的保障。  为了应对浅景深图像带来的几何重建挑战和理想 CoC 与真实 CoC 的差异，文章创新性地提出了深度先验调整和散焦到聚焦自适应策略。这些策略有效地提升了场景几何结构的准确性，并增强了散焦去模糊的性能，保证了 DoF-Gaussian 在处理真实浅景深图像时的鲁棒性和高质量渲染效果。
- [[MUSt3R Multi-view Network for Stereo 3D Reconstruction]]：提出了 MUSt3R (Multi-view Network for Stereo 3D Reconstruction)，这是一种新型的多视图网络，用于立体 3D 重建。MUSt3R 在多个 3D 下游任务中取得了最先进的性能，包括无需相机标定的视觉里程计、相对位姿估计、尺度和焦距估计、3D 重建和多视图深度估计。它能够在离线和在线场景中高效运行，适用于 SfM 和视觉 SLAM 应用。
  - 备注：TL;DR make DUSt3R symmetric and iterative+multi-layer memory mechanism->multi-view DUSt3R
- [[MTReD 3D Reconstruction Dataset for Fly-over Videos of Maritime Domain]]：提出并验证了一个新的海事领域三维重建基准数据集 MTReD (Maritime Three Dimensional Reconstruction Dataset)，以及一个新的感知相似性指标 DiFPS (DinoV2 Features Perception Similarity)，用于评估海事场景三维重建的几何一致性和视觉完整性。 文章通过实验证明了现有方法在海事场景三维重建中的局限性，并展示了 MTReD 数据集和 DiFPS 指标的有效性，以及预处理方法对提升重建质量的积极作用。
- [[Efficient Perspective-Correct 3D Gaussian Splatting Using Hybrid Transparency]]：通过结合混合透明度渲染方法和透视矫正的 3D 高斯 splat 评估方法，可以显著提升 3D 高斯 Splatting (3DGS) 的渲染效率和视觉质量，同时解决传统 3DGS 中存在的透视失真和深度排序错误导致的伪影问题，最终实现更快、更稳定、更高质量的实时渲染。  文章提出的方法在保持或提升图像质量的同时，实现了训练和渲染速度的显著提升，并解决了多视角一致性问题。
- [[FlexDrive Toward Trajectory Flexibility in Driving Scene Reconstruction and Rendering]]：当前基于 3D Gaussian Splatting 的驾驶场景重建和渲染技术，在预先记录的车辆轨迹上渲染质量很高，但在偏离轨迹的视角下质量显著下降。  为了解决这个问题，文章提出了 FlexDrive 框架，核心思想是通过 逆视图扭曲 (Inverse View Warping, IVW) 技术生成高质量的路径外 (out-of-path) 视角的监督信号，并结合 深度自举 (Depth Bootstrap, DB) 策略来获取精确的深度信息，从而显著提升路径外视角的重建和渲染质量，并保持路径内 (in-path) 视角的竞争力。  最终，FlexDrive 旨在实现驾驶场景重建和渲染的轨迹灵活性，使其更适用于实际的驾驶模拟器应用。

#### 深度估计

- [[Prompting Depth Anything for 4K Resolution Accurate Metric Depth Estimation]]：提出了 Prompt Depth Anything (PromptDA)，一种用于度量深度估计的新范式，通过使用低成本激光雷达（LiDAR）作为提示（Prompt）来引导深度基础模型，从而实现高分辨率（高达 4K）且精确的度量深度估计。文章的核心思想是将度量深度估计视为一个下游任务，通过向深度基础模型提供度量信息提示，解锁其在精确度量深度估计方面的潜力。
  - 低成本 LiDAR 作为有效的度量 Prompt。文章验证了低成本 LiDAR (例如 iPhone LiDAR) 可以作为有效的度量 Prompt，引导深度基础模型生成精确的度量深度图，并克服了单目深度估计的尺度模糊性问题。
  - 数据流水线和边缘感知损失是训练 PromptDA 的关键。为了解决训练数据不足和真实数据标注质量不高的问题，文章提出了可扩展的数据流水线 (合成 LiDAR 模拟 + 真实伪 GT 深度) 和边缘感知损失函数，保证了 PromptDA 的有效训练和 SOTA 性能。

#### 其他论文

- [[AnyAnomaly Zero-Shot Customizable Video Anomaly Detection with LVLM]]：提出了可定制的视频异常检测 (Customizable Video Anomaly Detection, C-VAD) 技术，并开发了名为 AnyAnomaly 的模型来实现这一技术。C-VAD 的核心思想是利用用户定义的文本描述作为异常事件的定义，从而实现零样本的视频异常检测，无需针对特定环境重新训练模型。AnyAnomaly 模型在 C-VAD 任务上表现出色，并在传统视频异常检测 (VAD) 基准数据集上取得了有竞争力的甚至是最先进的性能，尤其是在泛化能力方面超越了传统方法。
- [[PokéChamp an Expert-level Minimax Language Agent]]：通过将大型语言模型 (LLM) 与 minimax 树搜索相结合，可以构建出在复杂、部分可观察的两人零和博弈（如 Pokémon 战斗）中达到专家级水平的 AI 智能体，而无需额外的 LLM 训练或特定任务的微调。通过介绍名为 PokéChamp 的智能体，并实验验证了其在 Pokémon Gen 9 OU 模式下的卓越性能，证明了这一论点。PokéChamp 利用 LLM 增强了 minimax 算法的关键模块，使其能够有效利用游戏历史和人类知识，从而在搜索空间巨大且信息不完全的环境中做出更优决策。
- [[Ironies of Automation]]：自动化在工业流程中的应用，虽然旨在取代人工操作，但实际上常常会以意想不到的方式增加而非减少对人类操作员的依赖和挑战。  更进一步说，自动化的进步程度越高，人类操作员的关键作用可能就越发重要。这并非因为自动化不成功，而是因为自动化系统不可避免地会将那些设计者无法或不愿自动化的复杂、异常和非预期任务留给人类操作员处理。
  - 自动化悖论：  自动化程度越高，人类操作员的关键作用可能越发重要。自动化旨在减少人的参与，但实际上将更复杂、更关键的任务留给了人类。
  - 技能退化与监控难题：  自动化导致操作员手动技能退化，但在异常情况下又需要操作员具备高超的技能进行人工接管。同时，自动化系统本身也带来了监控难题，人类难以长时间有效地监控自动化系统的运行状态。
  - 人机协作是未来方向：  “人机功能分配” 的经典方法不足以应对自动化带来的挑战，未来需要发展更充分的人机协作模式，利用计算机支持人类操作员的决策和操作，共同应对复杂系统和异常情况。
- [[EgoLife Towards Egocentric Life Assistant]]：为了实现能够伴随并提升个人效率的以人工智能驱动的可穿戴眼镜为载体的自我中心生活助手，作者团队提出了 EgoLife 项目，并构建了 EgoLife 数据集和 EgoLifeQA 基准，以及 EgoButler 系统，旨在解决自我中心人工智能助手的关键技术挑战，并促进该领域的研究。
- [[PCE-GAN A Generative Adversarial Network for Point Cloud Attribute Quality Enhancement based on Optimal Transport]]：提出了一种名为 PCE-GAN (Point Cloud Attribute Quality Enhancement Generative Adversarial Network) 的新型点云属性质量增强算法，该算法基于最优传输理论，旨在同时优化数据保真度和感知质量，从而显著提升压缩点云的视觉质量。  文章结论是，PCE-GAN 在客观指标（PSNR, BD-rate）和主观视觉质量 (IWSSIMp) 上均优于现有技术，并在处理纹理复杂的点云时表现出更优异的性能，更符合实际应用需求。
- [[OceanSim A GPU-Accelerated Underwater Robot Perception Simulation Framework]]：提出了 OceanSim，一个 GPU 加速的水下机器人感知仿真框架，能够高保真地模拟水下环境和多种传感器，并且在渲染效率上显著优于现有的水下仿真器。文章旨在填补现有水下仿真器在物理精度、渲染效率和多传感器支持方面的研究空白，为水下机器人感知算法的开发、测试和验证提供更有效、更真实的工具。OceanSim 的核心目标是缩小“仿真 - 现实”差距 (sim-to-real gap)，并促进水下机器人技术的发展。
- [[DELTA Dense Efficient Long-range 3D Tracking for any video]]：提出了名为 DELTA (Dense Efficient Long-range 3D Tracking for Any video) 的新方法，首次实现了在任意视频中对每个像素进行高效、密集的、长距离 3D 跟踪，并达到了最先进的精度，同时显著提升了速度。DELTA 提出的全局 - 局部注意力机制，有效平衡了计算效率和跟踪精度，既能捕捉全局运动，又能关注局部细节，是实现高效密集跟踪的核心技术。文章强调了深度表示形式对 3D 跟踪性能的显著影响，并实验证明 log-depth 表示比传统欧几里得深度更优越，为 3D 视觉任务的输入数据表示提供了重要启示。

### 软件与开发

软件开发领域的思想和工具也在不断演进，从代码哲学到实用工具，这些进展如何影响日常开发？

“Every Line Is a Potential Bug”提醒开发者，每一行代码都可能是潜在的 Bug，应该只编写绝对必要且立即需要的代码，避免推测性编程和过早优化。这一理念与奥卡姆剃刀、YAGNI 以及 KISS 原则相似。

Tailscale 作为远程设备访问工具获得广泛认可，它解决了 CGNAT 环境下传统 DDNS 和端口转发失效的问题，并提供端口转发、文件共享等多种功能。对于国内用户，可考虑自行部署 derper-docker 与 ip_derper 作为中继服务器。

在命令行工具使用上，虽然 alias 命令是定义 shell 别名的传统方法，但使用放置在 $PATH 环境变量中的脚本作为别名通常是更优选择，提供了更高的灵活性、可维护性和可扩展性。对于项目管理，Makefile 仍是很好的统一入口和封装工具。

其他值得关注的进展包括：测试电梯的思路启示（通过有限状态机模型进行测试设计）、流式 HTML 技术用于创建实时 Web 应用、设备端 ML 框架调试策略、Quartz 静态站点生成器、Unix 文件系统的历史沿革、Python 单例模式的反思、MinerU 高质量数据提取工具、WebRTC 音频 AI SDK 集成方法以及用户空间 TCP/IP 协议栈的实现教程。

- [Every Line Is a Potential Bug](https://www.teamten.com/lawrence/writings/every_line_is_a_potential_bug.html)：每一行代码都可能是潜在的 Bug。因此，除非绝对必要且立即需要，否则不要编写任何代码。作者强调要避免为了推测性的需求或过早的优化而增加代码的复杂性，因为这会引入不必要的 Bug 风险，并可能在未来导致更严重的问题。
  - 每一行代码都可能是潜在的 Bug： 这是文章最核心的主张，强调代码的风险性。
  - 避免不必要的代码： 为了降低 Bug 风险，应该只编写绝对必要且立即需要的代码，避免推测性编程和过早优化。
  - 简洁性优于微小的性能提升：  在权衡代码的简洁性和性能时，应该优先考虑简洁性，除非性能瓶颈非常明显且优化收益远大于引入复杂性的风险。
  - 备注：与奥卡姆剃刀、YAGNI 以及 KISS 原则相似，但是该文章的核心假设与应对方式值得商榷。
- [Tailscale is pretty useful](https://blog.6nok.org/tailscale-is-pretty-useful/)：Tailscale 非常实用，它是一个有用的工具，可以简化远程设备访问，并提供了超出传统远程访问方法的多种便利功能。作者通过分享自己的使用经验，强调了 Tailscale 在解决 CGNAT 环境下远程访问难题，以及在日常使用中提供的额外价值。
  - Tailscale 简化了 CGNAT 环境下的远程访问：  Tailscale 解决了传统 DDNS 和端口转发在 CGNAT 环境下失效的问题，让用户可以轻松访问位于家庭或办公室网络中的设备。
  - Tailscale 提供多功能集成和用户友好体验：  除了基本的远程访问，Tailscale 还集成了端口转发、文件共享 (Taildrop)、VPN 出口节点等功能，并以用户友好的方式呈现，降低了使用门槛。
  - Tailscale 代表个人网络工具的新趋势：  Tailscale 不仅仅是一个 VPN，而是一个个人网络管理平台，预示着未来个人网络工具将更加注重设备互联、安全通信和便捷操作。
  - 备注：
    - Tailscale 本身仅提供国外的 DERP 中继服务器，在国内使用的话，可以考虑在云服务器（固定公网 IP）或者宽带（动态公网 IP）上自行部署 [derper-docker](https://github.com/fredliang44/derper-docker) 与 [ip_derper](https://github.com/yangchuansheng/ip_derper)，后者需要牺牲一部分安全性。控制端也可自建 [headscale](https://github.com/juanfont/headscale)。
    - 除了极端复杂的 NAT 与 MTU 环境（比如学校 VPN），连接都比较稳定。能打洞成功则不需要中继服务器，不能则通过中继服务器转发。与之类似的 Zerotier 不支持自建 TCP 中继，moon 节点实际上只是一个 UDP 中继节点。
    - 延伸阅读：
      - [The New Internet - Tailscale's Vision for the Future of Connectivity](https://tailscale.com/blog/new-internet)
      - [How NAT traversal works](https://tailscale.com/blog/how-nat-traversal-works)
      - [浅探 Tailscale DERP 中转服务](https://kiprey.github.io/2023/11/tailscale-derp/)
- [Why "alias" is my last resort for aliases](https://evanhahn.com/why-alias-is-my-last-resort-for-aliases/)：尽管 `alias` 命令是定义 shell 别名的传统方法，但使用放置在 `$PATH` 环境变量中的脚本 (`~/bin` 目录下的脚本) 作为别名通常是更优的选择，因为它提供了更高的灵活性、可维护性和可扩展性。  作者认为脚本应该成为别名设置的默认方法，而 `alias` 仅在特定情况下作为最后手段使用。
  - 脚本别名优于 `alias` 作为默认选择： 作者主张，由于脚本别名在灵活性、可编程性、可维护性和跨平台性方面的优势，它应该成为别名设置的默认方法，而 `alias` 退居为特定情况下的最后选择。
  - `alias` 在特定场景下仍然重要：  作者承认 `alias` 在特殊 shell 功能（如改变工作目录）、命令补全、条件定义、易于绕过、简洁性和性能方面具有优势，因而在这些特定场景下仍然不可替代。
  - 工具选择的权衡性：  文章的核心思想是强调工具选择的权衡性，即没有绝对最优的工具，选择应该基于具体需求和场景，需要在不同工具的优缺点之间进行权衡。
  - 备注：
    - 除了在命令行中使用 alias 与自制脚本，针对软件项目写 Makefile 也是很好的统一入口与封装（无论是 Python 还是 C++ 还是其他语言），并且方便传入覆写参数，以及自动化工具调用。比如 zetton-core 中将仓库的编译、测试、代码覆盖率检查等一大长串 `colcon` 命令封装为 `make build` 等命令。
    - 延伸阅读：
      - [I Like Makefiles](https://switowski.com/blog/i-like-makefiles/)
      - [How I stopped worrying and loved Makefiles](https://gagor.pro/2024/02/how-i-stopped-worrying-and-loved-makefiles/)
      - [Makefile tricks for Python projects](https://ricardoanderegg.com/posts/makefile-python-project-tricks/)
- [如何测试电梯](http://hanzilu.com/wordpress/?p=239)：即使不了解系统内部实现原理，也可以通过构建系统的计算模型（例如有限状态机），并基于此模型设计测试用例，来进行有效的系统测试。文章以经典的“如何测试电梯”面试题为例，阐述了运用有限状态机模型进行测试设计的思路，强调了从系统外部逻辑行为出发进行测试的重要性。
  - 模型抽象简化复杂性：  面对复杂系统测试，即使不了解内部实现，也可通过构建如有限状态机这样的抽象模型来抓住系统核心逻辑，降低测试设计的复杂性。
  - 逻辑行为测试优先：  测试应侧重于验证系统的外部逻辑行为是否符合预期，而非过度依赖内部实现细节。从用户视角出发，关注系统的状态变化和事件响应是关键。
  - 模型驱动提升测试效率：  运用模型（如有限状态机）可以系统化地指导测试用例设计，确保测试覆盖率，并提升测试效率和质量。
- [The Cursed Art of Streaming HTML](https://rinici.de/posts/streaming-html)：流式 HTML 是一种可行的技术，可以用于创建实时 Web 应用程序，而无需过度依赖 JavaScript。作者认为，通过利用浏览器对 `Connection: keep-alive` 的支持以及服务器端的流式处理能力，可以实现类似于 WebSocket 或 SSE 的实时更新效果，但实现方式更为简单，并且在一定程度上减少了对 JavaScript 的依赖。
- [Debugging Disposable ML Frameworks](https://petewarden.com/2025/03/06/debugging-disposable-ml-frameworks/)：在开发和调试用于设备端部署的一次性机器学习框架时，采用分模块测试、中间张量对比、关注量化和保持清晰的认知模型是至关重要的调试策略。 作者强调，虽然有很多关于训练 Transformer 模型的资源，但关于设备端部署的调试指导相对缺乏，因此分享了他在构建此类框架过程中积累的实用经验和技巧，旨在帮助开发者避免常见的陷阱，更有效地进行调试。
  - 设备端 ML 框架调试的特殊性与挑战： 与模型训练不同，设备端部署的调试缺乏足够的资源和指导，需要开发者掌握特定的调试技巧。
  - 分模块、中间张量对比是有效的调试策略： 通过将模型分解为模块，并对比已知良好模型和自定义框架的中间张量，可以快速定位错误模块，提高调试效率。
  - 清晰的认知模型是高效调试的基础： 开发者需要深入理解模型架构、算法原理和实现细节，才能有效地进行调试和问题解决。
- [quartz](https://github.com/jackyzha0/quartz)：Quartz is a fast, batteries-included static-site generator that transforms Markdown content into fully functional websites.
- [50 years in filesystems 1974](https://blog.koehntopp.info/2023/05/05/50-years-in-filesystems-1974.html)：Unix V7 文件系统虽然诞生于 1974 年，受限于当时的硬件条件，存在诸多局限性，但其设计中的核心概念和结构却非常清晰和简洁，并对后来的文件系统，乃至现代操作系统的 POSIX 标准产生了深远的影响。  文章通过回顾 Unix V7 文件系统的关键组件和设计决策，展示了早期文件系统的基本原理，并以此反思技术进步的本质以及早期设计对现代系统的持续影响。
- [50 years in filesystems 1984](https://blog.koehntopp.info/2023/05/06/50-years-in-filesystems-1984.html)：1984 年发布的 BSD 快速文件系统 (FFS) 是对传统 Unix 文件系统的重要改进，它通过引入多项创新设计，显著提升了文件系统的性能和效率，以适应当时快速发展的硬件和用户需求。  文章通过回顾 BSD FFS 的设计背景、核心创新以及性能提升，论证了其在文件系统发展史上的里程碑意义。
- [再也别问 Singleton 了好吗？](https://frostming.com/2025/singleton/)：在 Python 语言中，Singleton（单例模式）通常是不必要的，并且经常被滥用。更简洁、更符合 Python 哲学的方式是使用模块级别的变量来实现单例的需求。  作者认为，Singleton 作为一个经典设计模式，在 Python 中并没有其在其他语言中那样的必要性，反而因为其复杂性导致误用和成为面试八股文。
- [MinerU](https://github.com/opendatalab/MinerU)：一站式开源高质量数据提取工具，将 PDF 转换成 Markdown 和 JSON 格式。
- [Integrating Audio AI SDK with WebRTC (1) A Look Inside WebRTC's Audio Pipeline](https://www.gaudiolab.com/blog/137) 与 [Integrating the Audio AI SDK into WebRTC (2) Methodology for Building a Testing Environment for Effective Integration Development](https://www.gaudiolab.com/blog/138)：在 WebRTC 中集成音频 AI SDK（例如 Gaudio Lab 的 GSEP-LD）时，构建一个强大且高效的测试环境至关重要，这直接关系到集成开发的有效性与最终效果。  文章强调，由于 WebRTC 音频处理模块 (APM) 的复杂性和集成点选择的多样性，以及潜在的各种环境因素和子模块交互影响，细致周全的测试是确保成功集成的关键步骤。文章进一步指出，利用命令行界面 (CLI) 工具和开源项目可以有效地简化测试环境的搭建和管理，从而应对复杂场景下的集成测试需求。
- [Let's code a TCPIP stack, 1 Ethernet & ARP](https://www.saminiir.com/lets-code-tcp-ip-stack-1-ethernet-arp/)：实现一个最小化的用户空间 TCP/IP 协议栈，从 Ethernet 和 ARP 开始，是学习网络和系统编程的有效教育方法。  文章通过实际代码示例和步骤，展示了如何使用 Linux TAP 设备来捕获网络数据包，并解析 Ethernet 帧和 ARP 协议，最终成功实现 ARP 响应，验证了该论点。文章旨在说明即使 TCP/IP 协议栈看起来复杂，但从基础协议如 Ethernet 和 ARP 入手，并进行逐步实现，是可行的，并且对于深入理解网络协议栈的工作原理非常有帮助。
- [Let's code a TCPIP stack, 2 IPv4 & ICMPv4](https://www.saminiir.com/lets-code-tcp-ip-stack-2-ipv4-icmpv4/)：在用户空间中实现一个最小可用的 TCP/IP 协议栈，包括 IPv4 和 ICMPv4 层是可行的，并且可以通过 ICMP 回显请求（ping）进行验证。  文章旨在展示构建网络协议栈的实践方法，并鼓励读者理解 IPv4 和 ICMPv4 的基本原理和实现细节。
- [Let's code a TCPIP stack, 3 TCP Basics & Handshake](https://www.saminiir.com/lets-code-tcp-ip-stack-3-tcp-handshake/)：理解 TCP 协议的基本原理，特别是其可靠性机制和三次握手过程，是构建 TCP/IP 协议栈的关键步骤。 文章通过理论介绍、协议头分析和握手过程详解，并结合代码测试，逐步展示了 TCP 协议栈中 TCP 握手功能的实现方法和验证过程。最终目的是为读者理解 TCP 协议栈的构建打下基础，并为后续实现可靠数据传输功能做铺垫。

### 项目与团队管理

- [A few words about indie app business](https://blog.charliemonroe.net/a-few-words-about-indie-app-business/)：独立应用业务是一场马拉松，而非短跑冲刺，成功需要长期坚持、不断迭代和适应变化。
  - 耐心与迭代： 不要期望一夜成名，要从小处着手，快速迭代，根据用户反馈不断改进产品。
  - 长期投入的必要性： 独立应用业务需要长期的时间和精力投入，难以兼顾全职工作，要做好长期艰苦奋斗的准备。
  - 风险意识与多元化： 行业变化迅速，应用可能面临被淘汰的风险，要保持风险意识，并进行多元化发展，降低风险。
- [Your Next Two Zeroes](https://taylor.town/next-two-zeroes)：规模扩大一个数量级（10 倍）通常可以通过现有方法和工具进行调整，但规模扩大两个数量级（100 倍）则会彻底颠覆问题域，迫使我们重新思考所有方面，包括方法、工具、技能和思维模式。 这种规模的跃迁不仅仅是量的积累，更是质的突变，需要放弃原有的“成功秘诀”，以全新的视角和方法来应对。
  - 规模跃迁的临界点： 文章的核心主张是规模扩大两个数量级（100 倍）是一个关键的临界点，会引发系统性的质变，而非仅仅是量的积累。
  - 原有方法的失效： 随着规模的跃迁，原本有效的 “成功秘诀” 和方法论会失效，甚至成为阻碍前进的 “臭本能”。
  - 认知模式的转变： 应对规模跃迁的关键在于认知模式的转变，需要放弃固有的思维定势，以 “重新成为新手” 的心态去学习和适应新的挑战。
- [A Founder's Guide Essential Management Advice for Startups by @ttunguz](https://tomtunguz.com/management-advice-for-startups/)：有效的管理对于初创公司从混乱增长走向可持续成功至关重要，并且管理不是天生的才能，而是一种可以学习、实践和完善的学科。文章强调，随着初创公司规模扩大，管理能力的重要性与技术或客户群的扩展同等重要。

### 知识管理

- [为什么笔记用户要保卫自己的「数字主权」？](https://sspai.com/post/96863)：在数字时代，个人知识库已成为重要的数字资产，用户需要掌握对自己笔记数据的完全控制权，以避免数据丢失、平台垄断和未来技术发展带来的限制。
  - 笔记用户应捍卫数字主权: 核心主张是用户应掌握对其笔记数据的完全控制权，避免平台垄断、数据丢失和未来技术限制，这是知识管理和知识复利的基础。
  - 开源格式 + 多端备份是保障数字主权的关键策略: 推荐使用开源纯文本格式（如 Markdown）作为笔记载体，并采用多端同步备份方案（如 Git），以确保数据安全、可移植性和长期可用性。
  - 数字主权是迎接 AI 时代知识复利的前提: 强调在 AI 技术快速发展的时代，掌握数字主权，特别是使用纯文本格式，能够更好地利用个人知识库，享受新技术红利，实现知识复利的最大化。
- [从 Pandoc 到 Quarto：纯文本学术写作的实践与优化](https://sspai.com/post/97056)：Quarto 作为基于 Pandoc 的下一代科学出版系统，通过提供更强大的功能和更友好的用户体验，例如代码执行、交叉引用、参考文献预览等，以及针对中文学术写作的优化方案，是比 Pandoc 更为理想的纯文本学术写作工具，能够显著提升学术写作的效率和体验，最终让作者更专注于内容本身，产出更高质量的学术成果。
  - 备注：平常的技术写作用 Markdown 就行，学术论文还是得用 LaTeX。
- [人工智能真能替你写作吗？我自己的「AI 蓝军」测试](https://xiaobot.net/post/fe497700-0d5b-40ad-a15a-543463986876)：人工智能（特别是生成式 AI）在写作领域已经展现出强大的能力，能够辅助甚至在一定程度上替代人类完成写作任务，但这并不意味着人类写作者会被完全取代。  文章强调，在 AI 时代，知识工作者需要积极适应变化，掌握 AI 工具，将其作为助手来提升生产力，专注于人类独特的思考、价值观和审美判断，才能在未来的内容生产领域保持竞争力。文章通过作者自身的“AI 蓝军”测试经历，验证了 AI 在写作流程中的应用潜力，并探讨了人类写作者在 AI 时代的定位和发展方向。
  - 深度调研阶段：
    - 选择话题: 作者首先选定了自己感兴趣的 MCP 协议作为话题
    - 使用 OpenAI Deep Research: 提交明确问题，让 AI 进行深入调研
    - 生成原始报告: 获取详细全面但带有明显 "AI 味 " 的调研报告
  - 结构优化阶段：
    - 使用 Claude 3.7 Sonnet: 这个模型善于处理长文本且遵循指令能力强
    - 结构调整策略: 通过精心设计的提示词，让 AI 重新组织内容结构
    - 生成结构化内容: 输出更符合作者风格的文章框架，但仍有部分 AI 特征
  - 风格润色阶段：
    - 使用 ChatGPT 4.5: 这个模型在风格模仿上表现出色
    - 分段处理策略: 采用多轮对话方式，避免一次处理导致的压缩和质量下降
    - 风格润色提示词: 精确描述语言风格、读者称呼、标点使用等细节要求
    - 生成自然文章: 输出几乎无法分辨是 AI 写作的高质量文章
  - 配图生成阶段：
    - 使用 ChatGPT 4.0: 根据文章内容生成匹配的封面图
    - 最终审核: 作者进行简单修改，删除冗余总结语
- [从素材到成文，揭秘 Dailyio 的大模型写作全流程｜Digital Explorer055](https://next.iois.me/digital-explorer-055/)：大模型能够有效地赋能内容创作者的工作流程，但并非取代人类，而是一种人机协作模式。  文章强调，在严肃写作和产业分析等场景下，大模型仍然需要人类深度介入，尤其是在素材发现、数据准备和风格引导等环节。作者通过分享自己为“AI Insider”邮件通讯生产内容的工作流程，具体展示了如何利用大模型提升效率、处理信息和模仿写作风格，但同时也警示了完全依赖大模型的风险，强调了高质量输入（素材和指令）对于输出质量的关键作用。
  - 获取素材：使用现代浏览器工具高效获取文本素材
    - 使用 Brave 等基于 Chromium 的浏览器
    - 借助 bypass paywalls clean 扩展越过付费墙
    - 使用 MarkDownload 将网页转为 Markdown 格式
    - 在 Obsidian 中有序管理素材
  - 处理素材：根据素材类型选择不同的提示词策略
    - 新闻类：使用 " 苏格拉底提问法 " 提示词
    - 观点类：使用 "Enrich" 提示词
  - 风格学习：让大模型学习作者的个人写作风格
    - 精选代表性写作样本（300-400 字/篇）
    - 使用 " 分阶段模仿风格进行写作 " 的提示词
    - 让模型分析并确认风格特征
  - 实施写作：基于素材和风格进行创作
    - 准备素材和大纲
    - 选择适合的模型（推荐使用 Claude 系列）
    - 通过 API 方式与模型交互
    - 执行五步写作流程，完成创作

### ACGN

- [桌游设计杂记（5）  用三个月，测试并编辑一个重度的战棋游戏 - 少数派](https://sspai.com/post/97061)：成功开发一款重度战棋桌游，并使其达到可以向海外出版商投稿的程度，需要精细的分工合作、高强度的内部测试迭代、以及对产品化和编辑环节的重视。  文章通过记录《其惟春秋》这款游戏在三个月内的开发过程，具体阐述了如何通过高效的内部测试、及时的版本迭代、多语言准备、规则书撰写、以及产品化准备等环节，克服时间紧迫的困难，最终产出可用于投稿的游戏样品。同时，文章也强调了桌游开发不仅仅是玩法和美术，更包含了原型制作、测试、规则书、编辑、生产等多个环节，需要团队协作和专业分工才能保证质量和效率。

### 播客

- [后互联网时代的乱弹] 第 153 期 全球驻华办
- [编码人声] 聊聊外设种种草，主播们的压箱好物
- [晚点聊 LateTalk] 105: 潞晨尤洋争议中谈三方云平台 DeepSeek 成本：为何我不做 MaaS 了？
- [晚点聊 LateTalk] 104: 3700 次预训练寻找非共识，MiniMax-01 开发者讲述 4 年线性注意力之旅
- [忽左忽右] 389 王家卫的电影世界与六零年代的沪港想象
- [科技乱炖] 我们目睹了人类历史上最大的黑客盗窃案
- [硬地骇客] EP95 对话字节 Trae 团队：探秘 AI IDE 演进之路
- [张小珺 Jùn｜商业访谈录] 95. 对肖弘的 3 小时访谈：Agent、AI 应用创业的 2 年、做“博弈中重要变量”
- [OnBoard!] EP 67. 解析 DeepSeek R1 技术创新与生态影响：强化学习，Long CoT，数据，Agent 与开源生态
- [硅谷 101] E182｜影子美元与金融新秩序：起底全球人均最赚钱的公司 Tether
- [半拿铁 | 商业沉浮录] No.140 90 年代下岗潮
