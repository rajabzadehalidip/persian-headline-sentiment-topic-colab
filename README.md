# Text analysis classroom labs | Google Colab

Two beginner-friendly classroom experiments, with Persian instructions. Open a notebook, run the numbered sections, upload your file and edit the prompt. No programming experience is required.

| Experiment | Open notebook | Guide | API |
|---|---|---|---|
| YouTube comments: optimism/pessimism about AI, expressed emotion, stance toward the video | [Open in Colab](https://colab.research.google.com/github/rajabzadehalidip/persian-headline-sentiment-topic-colab/blob/main/YouTube_AI_Comments_Analysis.ipynb) | [Persian PDF guide with real Colab screenshots](output/pdf/youtube-comments-guide-fa.pdf) · [Markdown source](docs/youtube-comments-guide-fa.md) | GapGPT **or** OpenRouter |
| 2,000 Persian headlines: sentiment and topic | [Open in Colab](https://colab.research.google.com/github/rajabzadehalidip/persian-headline-sentiment-topic-colab/blob/main/Persian_Headline_Sentiment_and_Topic_Classification.ipynb) | [راهنمای فارسی PDF](docs/student-guide-fa.pdf) | GapGPT · GPT-6 Luna |

## YouTube comment experiment

`YouTube_AI_Comments_Analysis.ipynb` contains the experiment code and instructions, but **does not contain the YouTube comments data**. The QR code/link only opens the notebook; students need a permitted comments file from the instructor and upload it themselves. See the [complete step-by-step guide with real Colab screenshots](docs/youtube-comments-guide-fa.md). Students can upload CSV/TSV, Excel (`.xlsx`), JSON/JSONL or line-based TXT; confirm the comment-text column; select GapGPT or OpenRouter; and enter the key through a hidden password prompt or Colab Secrets. The key is never embedded in the notebook or exported results.

Students edit the prompt and supply a short summary of the video's actual claims. The notebook does not watch the video. The three targets are independent: liking AI is different from agreeing with the video; emotion refers to what the comment expresses. `mixed`, `neutral`, `not_addressed` and `unclear` options prevent forced judgments. Missing video/reply context remains visible.

Start with the same seeded 10-comment pilot, inspect it against independent human labels, then change the prompt and compare the same comments. A blank human-annotation sample can be downloaded before seeing model labels. The optional larger run defaults off and requires a technically successful pilot of the current configuration plus an explicit human-review/cost checkbox. The initial larger-run limit is 100 comments; all rows can be selected separately.

Charts show label distributions, **not accuracy**. Exports include Excel, CSV and a lossless JSON log with prompts, evidence, raw responses, requested/returned model IDs, sampling seed and errors. Previous outputs are reused within a live session only when the entire configuration and comment match. Interrupted runs keep completed rows. No scraped YouTube comments, identities, API keys or real model results are included in this public repository.

## Persian headline classification

This project is a beginner-friendly Google Colab workflow for class annotation and LLM-assisted text analysis of Persian news headlines.

## Quick start / شروع سریع

- [Open the notebook in Google Colab](https://colab.research.google.com/github/rajabzadehalidip/persian-headline-sentiment-topic-colab/blob/main/Persian_Headline_Sentiment_and_Topic_Classification.ipynb)
- [راهنمای سادهٔ فارسی، گام‌به‌گام (PDF)](docs/student-guide-fa.pdf)
- [Download the 2,000-headline workbook](https://raw.githubusercontent.com/rajabzadehalidip/persian-headline-sentiment-topic-colab/main/headlines_2000_sample.xlsx)
- [Download the 100-headline human-annotation template](https://raw.githubusercontent.com/rajabzadehalidip/persian-headline-sentiment-topic-colab/main/gold_annotation_template_100.xlsx)

The headline workbook and annotation template are included in this repository, but Colab does not automatically load them. Download both files and upload them when the notebook asks. The gold template is blank for students to annotate; it is not pre-labeled ground truth.

Start with the two-person human annotation, then run the pilot before enabling the full dataset. Each student should use their own GapGPT API key; API use may have quota or billing limits. Its pilot does not automatically reserve an independent final test set; use a fresh human-labeled test sample before making deployment claims.

## Files

- `Persian_Headline_Sentiment_and_Topic_Classification.ipynb` — guided Colab notebook.
- `headlines_2000_sample.xlsx` — clean, reproducible random sample of 2,000 headlines.
- `gold_annotation_template_100.xlsx` — a random 100-headline subset of the 2,000; blank columns for two independent raters and their agreed consensus.

## Recommended class sequence

1. Choose category definitions as a class. The workbook and notebook include starter sentiment and topic categories.
2. In pairs, annotate the 100-row template independently. Do not discuss labels until both raters finish.
3. Discuss disagreements and fill `consensus_sentiment` and `consensus_topic`; preserve both original rater columns.
4. Open the notebook in Colab, upload both Excel files, and add your own `GAPGPT_API_KEY` secret in Colab. The notebook uses GapGPT's OpenAI-compatible endpoint (`https://api.gapgpt.app/v1`) with model `gpt-6-luna`.
5. Write or revise the Persian prompt, run the gold-sample pilot, review human–human and LLM–consensus agreement (percent agreement and Cohen's kappa), then set `RUN_FULL_DATASET = True` to annotate the complete 2,000-row sample.
6. Download the annotated Excel workbook and discuss the plots and error cases.

## Annotation design

- Sentiment is the headline's expressed framing of the event: positive, negative, or neutral.
- Topic is one main subject per headline. The starter list includes politics/government, economy, society/law, international affairs/conflict, culture/religion, health/education, sports, science/technology, and other/unclear.
- If the class changes labels, update the Codebook and dropdowns in the gold workbook and the category lists in the notebook before annotation.
- Cohen's kappa is calculated separately for sentiment and topic. The notebook does not calculate macro-averaged classification scores.

## Setup notes

- Open the `.ipynb` file in Colab (upload it to Google Drive, then choose **Open with Google Colaboratory**).
- The notebook uses the OpenAI Python SDK with GapGPT's OpenAI-compatible API. Each student stores their own key as `GAPGPT_API_KEY` in Colab Secrets; never put the key in a shared code cell. The connection cell makes one small synthetic request before the gold-sample pilot.
- The gold template is blank by design. It becomes the reference set only after independent annotation and consensus discussion.
- Full-scale means the uploaded 2,000-row analysis sample. API quota or billing limits may apply; review your account limits before the full run.

## Data provenance

The 2,000-row file is a seeded random sample from the user's 85,056-row Persian headline collection. `record_id` is a stable sample key. The model is sent the headline text, not outlet/year metadata. The source collection spans ten sampled outlets and Solar Hijri years 1395–1404; it should not be treated as a census of all Persian-language news.
