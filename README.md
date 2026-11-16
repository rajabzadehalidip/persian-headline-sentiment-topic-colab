# Persian headline classification | Colab project

This project is a beginner-friendly Google Colab workflow for class annotation and LLM-assisted text analysis of Persian news headlines.

## Files

- `Persian_Headline_Sentiment_and_Topic_Classification.ipynb` — guided Colab notebook.
- `headlines_2000_sample.xlsx` — clean, reproducible random sample of 2,000 headlines.
- `gold_annotation_template_100.xlsx` — a random 100-headline subset of the 2,000; blank columns for two independent raters and their agreed consensus.

## Recommended class sequence

1. Choose category definitions as a class. The workbook and notebook include starter sentiment and topic categories.
2. In pairs, annotate the 100-row template independently. Do not discuss labels until both raters finish.
3. Discuss disagreements and fill `consensus_sentiment` and `consensus_topic`; preserve both original rater columns.
4. Upload the notebook to Google Colab. Run the cells from top to bottom, upload both Excel files, and add a `GEMINI_API_KEY` secret in Colab.
5. Write or revise the Persian prompt, run the gold-sample pilot, review human–human and LLM–consensus agreement (percent agreement and Cohen's kappa), then set `RUN_FULL_DATASET = True` to annotate the complete 2,000-row sample.
6. Download the annotated Excel workbook and discuss the plots and error cases.

## Annotation design

- Sentiment is the headline's expressed framing of the event: positive, negative, or neutral.
- Topic is one main subject per headline. The starter list includes politics/government, economy, society/law, international affairs/conflict, culture/religion, health/education, sports, science/technology, and other/unclear.
- If the class changes labels, update the Codebook and dropdowns in the gold workbook and the category lists in the notebook before annotation.
- Cohen's kappa is calculated separately for sentiment and topic. The notebook does not calculate macro-averaged classification scores.

## Setup notes

- Open the `.ipynb` file in Colab (upload it to Google Drive, then choose **Open with Google Colaboratory**).
- The notebook uses Google's `google-genai` Python SDK and a Gemini API key stored in Colab Secrets. Never put the API key in a shared code cell.
- The gold template is blank by design. It becomes the reference set only after independent annotation and consensus discussion.
- Full-scale means the uploaded 2,000-row analysis sample. API quota or billing limits may apply; review your account limits before the full run.

## Data provenance

The 2,000-row file is a seeded random sample from the user's 85,056-row Persian headline collection. `record_id` is a stable sample key. The model is sent the headline text, not outlet/year metadata. The source collection spans ten sampled outlets and Solar Hijri years 1395–1404; it should not be treated as a census of all Persian-language news.
