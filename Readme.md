# PatternPivot: Elevating Video Content for Maximum Audience Retention

## Introduction
PatternPivot emerged from the necessity to help content creators fine-tune their videos to bolster audience retention and engagement in an age where capturing attention is crucial yet challenging. Creators often face the hurdle of repurposing their video content effectively, and that's where PatternPivot steps in.

## What PatternPivot Does
PatternPivot is a video generation service that focuses on enabling creators to transform their existing videos into catchy, engaging content in various short-term formats and variations quickly. With LLM-powered transcription at its core, PatternPivot allows for the remixing of video segments, ensuring the new content is primed for audience retention. The innovation lies in its ability to adapt to the competitive content arena, giving creators a much-needed edge.

## How PatternPivot Was Built
The architecture of PatternPivot is the culmination of API integrations, LLM's, a local open-source vector database and free open-source embeddings and semantic search techniques. 

### Our system architecture:

![Video Generation Systems Architecture Diagram](Generating_Video_Systems_Diagram.png)

- The YouTube Data API v3 is used to fetch video content.
- Taking screenshots with OpenAI's Dall-e to generate new images.
- Retrieving video statistics for further processing and storing JSON in AWS DynamoDB currently with the intention of utlizing Google Cloud JSON API in the future.
- The vector database used is the open source version of Milvus Local server in Docker. Embedding conversion are designed to be limited to only a select corpus of transcripts as needed by topic stored locally in the server spun up in localhost by the Milvus docker container. 
- Chunking and retrieval augmented generation (RAG) are achieved using LangChain.
- New video transcripts are refined through iterative LLM prompting.
- LLM embeddings are using HuggingFace-hosted "WhereIsAI/UAE-Large-V1" and/or "llmrails/ember-v1" 
- Embeddings retrieval are using either nearest neighbors or cosine similarity.
- OpenAI API's Dall-e is prompted using screencaptures of youtube videos using selenium.
- The only paid API usage for this initiative would be generating images using Dall-e through OpenAI's API and until DynamoDB hits over 25GB or Google Cloud JSON API hitting it's 1 TB limit. 
- Converting transcripts to speech to create new video content will involve Coqui, an open source python module.

The iterative development process was key, focusing on prototypes and refining our algorithms for heightened accuracy. The backend infrastructure is cloud-based, scalable, and designed for efficient processing and a smooth user experience.

## Challenges Faced
Our journey was marked by the challenge of planning for the processing extensive data volumes at scale.

## Our Proud Accomplishments
We take pride in our AI-driven methodology that identifies and refines content segments, significantly improving the quality of content for viewers.

## Lessons Learned
The PatternPivot journey has been a deep dive into the significance of text data in content creation and the transformative power of AI in the creative domain. 

## The Future of PatternPivot
Our roadmap includes advancing PatternPivot with sophisticated video generation capabilities. We envision PatternPivot as the ultimate tool for creators who strive to maximize their content's effectiveness and widen their reach.

## Conclusion
PatternPivot stands at the forefront of content optimization, empowering creators with AI-driven tools to craft content that resonates and retains. With a commitment to continual improvement, PatternPivot is poised to enhance productivity in the content creation domain.
