"""Build the self-contained Colab from the reviewed core and beginner UI cells."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cells = []


def markdown(source):
    cells.append({"cell_type": "markdown", "id": "yt-md-" + str(len(cells)), "metadata": {}, "source": source.strip().splitlines(keepends=True)})


def code(source, tag=None):
    metadata = {"cellView": "form"}
    if tag:
        metadata["tags"] = [tag]
    cells.append({"cell_type": "code", "id": "yt-code-" + str(len(cells)), "metadata": metadata, "execution_count": None, "outputs": [], "source": source.strip().splitlines(keepends=True)})


markdown("""
# آزمایش کامنت‌های یوتیوب: نگاه به AI، هیجان و موضع نسبت به ویدئو

**نیازی به برنامه‌نویسی ندارید.** کنار هر بخش، دکمهٔ ▶ را به‌ترتیب از بالا به پایین بزنید. کدهای پنهان را تغییر ندهید؛ فقط فایل، سرویس و کادر پرامپت را انتخاب یا ویرایش کنید. GPU لازم نیست.

این دفتر سه سؤال متفاوت می‌پرسد:

| سؤال | هدف |
|---|---|
| خوش‌بین یا بدبین؟ | نگاه کامنت به اثر AI بر آیندهٔ انسان |
| چه هیجانی؟ | هیجانِ بیان‌شده در متن، مانند امید، ترس یا خشم |
| موافق یا مخالف؟ | موضع نسبت به **ادعاهای ویدئو**؛ نه صرفاً دوست‌داشتن AI |

ابتدا یک نمونهٔ تصادفی ثابت از **۱۰ کامنت** را بررسی می‌کنیم. پرامپت را تغییر می‌دهیم و همان نمونه را دوباره می‌سنجیم. اجرای بزرگ‌تر اختیاری است.

**قبل از شروع:** از منوی File، گزینهٔ Save a copy in Drive را بزنید. فایل کامنت‌ها، حساب Google و کلید GapGPT **یا** OpenRouter را آماده کنید. کلید را در سلول کد ننویسید. درخواست‌های API ممکن است هزینه داشته باشند. متن کامنت و، در صورت انتخاب، متن والد به سرویس انتخابی ارسال می‌شود؛ نام کاربری و سایر ستون‌ها به‌صورت خودکار ارسال نمی‌شوند. فایل کامنت‌ها در این مخزن عمومی قرار ندارد.
""")

setup = '''#@title ۱) آماده‌سازی — فقط ▶ را بزنید و صبر کنید
%pip -q install "openpyxl>=3.1,<4" "ipywidgets>=8.1,<9" "requests>=2.31,<3"
from google.colab import files, output
output.enable_custom_widget_manager()
import ipywidgets as widgets
from IPython.display import display, Markdown, HTML, clear_output
import matplotlib.pyplot as plt
'''
setup += "\n" + (ROOT / "tools/youtube_comments_core.py").read_text(encoding="utf-8")
setup += '''
STATE = {"df": None, "connection": None, "cache": {}, "runs": [], "file_name": ""}
print("آماده شد. حالا بخش ۲ را اجرا کنید. کلیدی ذخیره یا چاپ نشده است.")
'''
code(setup, "lab-core")

markdown("""
## ۲. فایل کامنت‌ها را بارگذاری کنید

▶ را بزنید و **فقط یک فایل** انتخاب کنید. فرمت‌ها: Excel با پسوند `xlsx`، یا `csv`، `tsv`، `json`، `jsonl` و `txt`.

ستون متن معمولاً خودکار پیدا می‌شود. **پیش‌نمایش را بخوانید:** اگر به‌جای کامنت، نام کاربر یا لینک می‌بینید، ستون متن را از فهرست عوض کنید. برای Excel می‌توانید شیت را تغییر دهید. ستون والد اختیاری است و باید **متن** کامنت والد باشد، نه شناسهٔ آن. برای فایل TXT، هر خط یک کامنت محسوب می‌شود؛ متن‌های چندخطی را با CSV/Excel بارگذاری کنید.
""")
code('''#@title ۲) انتخاب فایل، شیت و ستون متن
STATE.update(df=None, file_name="", upload_bytes=None)
uploaded = files.upload()
if len(uploaded) != 1:
    print("لطفاً این بخش را دوباره اجرا و فقط یک فایل انتخاب کنید.")
else:
    file_name, raw_bytes = next(iter(uploaded.items()))
    STATE.update(file_name=file_name, upload_bytes=bytes(raw_bytes))
    preview = widgets.Output()
    columns_box = widgets.VBox()
    sheet_box = widgets.VBox()
    encoding_box = widgets.Dropdown(options=[("خودکار / UTF-8", "auto"), ("UTF-8", "utf-8-sig"), ("UTF-16", "utf-16"), ("Persian Windows-1256", "cp1256"), ("Western Windows-1252", "cp1252")], description="Encoding:", style={"description_width": "initial"})
    if Path(file_name).suffix.lower() == ".xlsx":
        try:
            sheet_names = pd.ExcelFile(io.BytesIO(raw_bytes), engine="openpyxl").sheet_names
            STATE["sheet_widget"] = widgets.Dropdown(options=sheet_names, description="Sheet:")
            sheet_box.children = [STATE["sheet_widget"]]
        except Exception:
            STATE["sheet_widget"] = None
    else:
        STATE["sheet_widget"] = None

    def update_preview(*_):
        with preview:
            clear_output(wait=True)
            try:
                column = STATE["text_widget"].value
                frame = prepare_frame(STATE["df"], column, STATE["parent_widget"].value)
                usable = sum(input_issue(row) is None for row in frame.to_dict("records"))
                print(f"{len(frame)} ردیف؛ {usable} کامنت قابل اجرا. ردیف تکراری حذف نشده است.")
                print("فقط متن کامنت و والد انتخاب‌شده ارسال می‌شود. این پیش‌نمایش را تأیید کنید:")
                display(frame.head(5))
                print("ردیف‌های خالی یا بسیار بلند برچسب ساختگی نمی‌گیرند. در اجرای همهٔ ردیف‌ها وضعیتشان ثبت می‌شود.")
            except Exception as exc:
                print("ستون متن کامنت‌ها را انتخاب کنید.", str(exc))

    def load_selected_file(*_):
        try:
            sheet = STATE["sheet_widget"].value if STATE["sheet_widget"] else None
            STATE["df"] = read_comments_file(file_name, STATE["upload_bytes"], sheet=sheet, encoding=encoding_box.value)
            column_names = list(STATE["df"].columns)
            STATE["text_widget"] = widgets.Dropdown(options=column_names, value=guess_text_column(column_names), description="Comment column:", style={"description_width": "initial"}, layout=widgets.Layout(width="95%"))
            parents = [("بدون متن والد", None)] + [(c, c) for c in column_names]
            parent_default = "parent_context" if "parent_context" in column_names else None
            STATE["parent_widget"] = widgets.Dropdown(options=parents, value=parent_default, description="Parent text:", style={"description_width": "initial"}, layout=widgets.Layout(width="95%"))
            STATE["text_widget"].observe(update_preview, names="value")
            STATE["parent_widget"].observe(update_preview, names="value")
            columns_box.children = [STATE["text_widget"], STATE["parent_widget"]]
            update_preview()
        except Exception as exc:
            STATE["df"] = None
            columns_box.children = []
            with preview:
                clear_output(wait=True)
                print("فایل خوانده نشد:", str(exc))
                print("فرمت و شیت را بررسی کنید؛ برای فایل CSV نامفهوم، Encoding را عوض کنید.")

    display(sheet_box, encoding_box, columns_box, preview)
    encoding_box.observe(load_selected_file, names="value")
    if STATE["sheet_widget"]:
        STATE["sheet_widget"].observe(load_selected_file, names="value")
    load_selected_file()
''', "upload-ui")

markdown("""
## ۳. سرویس و کلید را انتخاب کنید

در فرم زیر GapGPT یا OpenRouter را انتخاب و ▶ را بزنید. سپس کلید را در **کادر رمز مخفی** وارد کنید و Enter بزنید. کلید در فایل خروجی ثبت نمی‌شود و در حافظهٔ همین نشست می‌ماند. کلید را در کد، پرامپت یا چت کلاس ننویسید.

شناسهٔ مدل را می‌توانید خالی بگذارید: پیش‌فرض GapGPT برابر `gpt-4o-mini` و OpenRouter برابر `openai/gpt-4o-mini` است. موجودبودن مدل و اعتبار حساب را در سرویس خود بررسی کنید. اگر مدرس مدل دیگری مشخص کرد، شناسهٔ دقیق آن را وارد کنید. تغییر سرویس/مدل نیازمند اجرای دوبارهٔ همین بخش است.

گزینهٔ `USE_COLAB_SECRET` اختیاری است: برای استفاده از Secrets، نام راز را `GAPGPT_API_KEY` یا `OPENROUTER_API_KEY` بگذارید. در حالت پیش‌فرض، کادر رمز مخفی استفاده می‌شود.
""")
code('''#@title ۳) اتصال به سرویس — کلید را فقط در کادر رمز وارد کنید
PROVIDER = "GapGPT" #@param ["GapGPT", "OpenRouter"]
MODEL_ID = "" #@param {type:"string"}
USE_COLAB_SECRET = False #@param {type:"boolean"}
from getpass import getpass
STATE["connection"] = None
try:
    if USE_COLAB_SECRET:
        from google.colab import userdata
        private_key = userdata.get("GAPGPT_API_KEY" if PROVIDER == "GapGPT" else "OPENROUTER_API_KEY")
    else:
        private_key = getpass("API key (مخفی؛ سپس Enter): ")
    STATE["connection"] = make_connection(PROVIDER, MODEL_ID, private_key)
    private_key = ""
    connection = STATE["connection"]
    print(f"تنظیم شد: {connection.provider} / {connection.model}")
    print("کلید چاپ نمی‌شود. هنوز درخواست طبقه‌بندی ارسال نشده؛ نخستین پایلوت اتصال را امتحان می‌کند.")
except Exception:
    private_key = ""
    print("اتصال تنظیم نشد. سرویس، کلید و شناسهٔ مدل را بررسی و همین بخش را دوباره اجرا کنید.")
''', "connection-ui")

markdown("""
## ۴. ادعاهای ویدئو و پرامپت را بنویسید

پس از ▶، دو کادر ظاهر می‌شود. در کادر اول، **دو یا سه جمله دربارهٔ ادعاهای اصلی ویدئو** بنویسید. عنوان یا موضوع کلیِ «اثر AI بر تکامل انسان» برای تعیین موافق/مخالف کافی نیست. برنامه ویدئو را از روی لینک تماشا نمی‌کند. اگر این کادر خالی باشد، فقط موافقت/مخالفت صریح با ویدئو قابل کدگذاری است و موارد وابسته به ادعای نامعلوم، `unclear` می‌شوند.

در کادر دوم، تعریف‌ها و دستور تحلیل را ویرایش کنید. مثلاً بنویسید با کنایه چگونه برخورد شود، یا چه زمانی برچسب `mixed` بدهد. **نام برچسب‌ها را عوض نکنید**؛ نیازی به نوشتن JSON نیست. متن فارسی یا انگلیسی قابل استفاده است.

| هدف | برچسب‌ها |
|---|---|
| نگاه به AI | `optimistic` خوش‌بین، `pessimistic` بدبین، `mixed` ترکیبی، `neutral` بدون ارزیابی، `unclear` نامشخص |
| هیجان غالب | `hope` امید، `joy` شادی، `fear` ترس، `anger` خشم، `sadness` اندوه، `disgust` انزجار، `surprise` تعجب، `neutral`، `mixed`، `unclear` |
| موضع نسبت به ویدئو | `agree` موافق، `disagree` مخالف، `mixed` ترکیبی، `not_addressed` بی‌ارتباط با ادعا، `unclear` نامشخص |

**آزمایش:** پیش از اجرای مدل، خودتان همان ۱۰ کامنت نمونه را برچسب بزنید. برای مقایسهٔ دو پرامپت، فقط یک بخش از پرامپت را عوض کنید و نمونه/مدل را ثابت نگه دارید. اختلاف خروجی لزوماً به‌معنای بهبود نیست.
""")
code('''#@title ۴) کادرهای قابل ویرایش — کد را تغییر ندهید
if "claims_widget" not in STATE:
    STATE["claims_widget"] = widgets.Textarea(value="", placeholder="ادعای اصلی ویدئو چیست؟ دو یا سه جمله؛ فقط لینک ننویسید.", layout=widgets.Layout(width="100%", height="130px"))
if "prompt_widget" not in STATE:
    STATE["prompt_widget"] = widgets.Textarea(value=DEFAULT_INSTRUCTIONS, layout=widgets.Layout(width="100%", height="480px"))
STATE["claims_widget"].add_class("yt-prompt-rtl")
STATE["prompt_widget"].add_class("yt-prompt-rtl")
display(HTML("<style>.yt-prompt-rtl textarea{direction:rtl;text-align:right;font-family:Tahoma,sans-serif;line-height:1.7;font-size:15px}</style>"))
display(HTML("<b>خلاصهٔ ادعاهای ویدئو / Video claims</b>"), STATE["claims_widget"])
display(HTML("<br><b>پرامپت قابل ویرایش / Editable prompt</b>"), STATE["prompt_widget"])
print("بعد از ویرایش این کادرها، بخش ۵ را اجرا کنید. لازم نیست دوباره بخش ۴ را اجرا کنید.")
try:
    if STATE.get("df") is not None:
        preview_frame = prepare_frame(STATE["df"], STATE["text_widget"].value, STATE["parent_widget"].value)
        pilot_rows = [row for row in ordered_rows(preview_frame) if input_issue(row) is None][:10]
        human_template = pd.DataFrame(pilot_rows)
        for task in LABELS:
            human_template["human_" + task] = ""
        display(HTML("<hr><b>همین نمونه را قبل از دیدن جواب مدل، خودتان برچسب بزنید:</b>"), human_template)
        template_button = widgets.Button(description="دانلود نمونه برای برچسب انسانی", layout=widgets.Layout(width="320px"))
        def download_template(_):
            path = Path("human_annotation_pilot.csv")
            human_template.apply(lambda col: col.map(_csv_cell)).to_csv(path, index=False, encoding="utf-8-sig")
            files.download(str(path))
        template_button.on_click(download_template)
        display(template_button)
        print("این جدول خالی هنوز استاندارد طلایی نیست؛ ابتدا خودتان برچسب بزنید و اختلاف‌ها را بررسی کنید.")
except Exception:
    print("برای دیدن نمونهٔ انسانی، اول فایل و ستون متن را در بخش ۲ مشخص کنید و بخش ۴ را دوباره اجرا کنید.")
''', "prompt-ui")

markdown("""
## ۵. پایلوتِ ۱۰ کامنت را اجرا و بررسی کنید

▶ را بزنید. همان نمونه با بذر ثابت ۴۲ در همهٔ پرامپت‌ها استفاده می‌شود. **هر کامنت یک درخواست** برای هر سه هدف است؛ خطاهای موقت ممکن است تا دو بار دیگر تلاش شوند.

جدول، دلیل کوتاه و عبارت شاهد را بخوانید. `needs_review=True` یعنی بررسی انسانی لازم است. `unclear` با خطای API فرق دارد؛ ردیف‌های `api_error` و `invalid_output` برچسب معتبر ندارند. نمودارها فراوانی برچسب‌های مدل‌اند، نه دقت و نه نظر نمایندهٔ کل مردم.

برای پرامپت دوم، کادر بخش ۴ را ویرایش و **فقط بخش ۵** را دوباره اجرا کنید. نتایج قبلی در حافظه می‌مانند. اگر تنظیمات هیچ تغییری نکند، پاسخ‌های قبلی دوباره استفاده می‌شوند؛ این یک آزمایش مستقل تازه نیست.
""")
code('''#@title ۵) اجرای پایلوت و نمایش نتایج
def current_inputs():
    if STATE.get("df") is None:
        raise ValueError("ابتدا فایل را در بخش ۲ بارگذاری کنید.")
    if STATE.get("connection") is None:
        raise ValueError("ابتدا اتصال بخش ۳ را تنظیم کنید.")
    if "prompt_widget" not in STATE:
        raise ValueError("ابتدا کادرهای بخش ۴ را باز کنید.")
    frame = prepare_frame(STATE["df"], STATE["text_widget"].value, STATE["parent_widget"].value)
    meta = {"file_name": STATE["file_name"], "sheet": STATE["sheet_widget"].value if STATE.get("sheet_widget") else None, "text_column": STATE["text_widget"].value, "parent_column": STATE["parent_widget"].value, "dataset_hash": fingerprint(frame.to_dict("records"))}
    config = make_config(STATE["connection"], STATE["prompt_widget"].value, STATE["claims_widget"].value, meta)
    return frame, config

def show_run(run):
    valid = [r for r in run["records"] if r["status"] == "ok"]
    errors = sum(r["status"] in ["api_error", "invalid_output"] for r in run["records"])
    print(f"Run: {run['run_id']} | {run['config']['provider']} / {run['config']['requested_model']}")
    print(f"وضعیت: {run['status']}؛ پردازش {len(run['records'])}/{len(run['jobs'])}؛ پاسخ معتبر {len(valid)}؛ خطا/خروجی نامعتبر {errors}")
    print(f"درخواست‌های تازه: {run['new_calls']}؛ پاسخ‌های استفاده‌شده از اجرای قبلی: {run['cache_hits']}")
    if not run["config"]["video_claims"]:
        print("خلاصهٔ ادعاهای ویدئو خالی است؛ موضع‌گیری‌های وابسته به ادعای نامعلوم را دستی بررسی کنید.")
    display(results_frame(run).head(20))
    if valid:
        summary = summary_frame(run)
        fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
        for ax, (task, labels) in zip(axes, LABELS.items()):
            part = summary[summary["task"] == task]
            counts = part["count"].to_list()
            ax.barh(labels, counts, color="#785ef0")
            ax.invert_yaxis()
            ax.set_xlim(0, max(1, max(counts)) * 1.4)
            ax.set_title(task + f" (valid n={len(valid)})")
            ax.set_xlabel("Comments (model labels)")
            for y, n in enumerate(counts):
                ax.text(n + 0.02 * max(1, max(counts)), y, f"{n} ({100*n/len(valid):.0f}%)", va="center")
        plt.tight_layout()
        plt.show()
        print("درصدها از پاسخ‌های معتبر محاسبه شده‌اند؛ mixed و unclear حذف نشده‌اند. این نمودار accuracy نیست.")
    else:
        print("پاسخ معتبر نداریم؛ نمودار درصدی ساخته نمی‌شود. خطاها و تنظیمات را بررسی کنید.")
    download = widgets.Button(description="دانلود نتیجهٔ این اجرا (ZIP)", layout=widgets.Layout(width="300px"))
    def download_run(_):
        files.download(str(export_bundle(run)))
    download.on_click(download_run)
    display(download)
    print("ZIP شامل Excel، CSV و run.json با پرامپت دقیق و پاسخ خام است؛ کلید API ندارد.")

def run_current(limit=10, scope="pilot", reviewed=False):
    try:
        frame, config = current_inputs()
        if scope != "pilot":
            tested = [r for r in STATE["runs"] if r["scope"] == "pilot" and r["config_hash"] == fingerprint(config) and r["status"] == "complete" and r["records"] and all(x["status"] == "ok" for x in r["records"])]
            if not reviewed or not tested:
                print("اجرای بزرگ‌تر متوقف شد: ابتدا پایلوتِ همین پرامپت/مدل/داده را بدون خطای فنی اجرا و دستی بررسی کنید؛ سپس تیک تأیید را بزنید.")
                return
        run = prepare_run(frame, config, STATE["cache"], limit=limit, scope=scope)
        print(f"{len(run['jobs'])} ردیف انتخاب شده؛ حداکثر {run['planned_new_calls']} درخواست تازه، به‌علاوهٔ تلاش مجدد خطاهای موقت. هزینه به سرویس و مدل بستگی دارد.")
        if not run["planned_new_calls"]:
            print("پاسخ‌های این تنظیمات در حافظه موجود است؛ درخواست تازه لازم نیست.")
        STATE["runs"].append(run)
        progress = widgets.IntProgress(value=0, min=0, max=len(run["jobs"]), description="Progress:")
        text = widgets.HTML()
        display(progress, text)
        def update(current):
            progress.value = len(current["records"])
            text.value = f"{len(current['records'])} / {len(current['jobs'])}"
        process_run(run, STATE["connection"], STATE["cache"], progress=update, checkpoint_dir="lab_outputs")
        show_run(run)
    except Exception as exc:
        print("اجرا انجام نشد:", str(exc))

run_current(limit=10, scope="pilot")
''', "pilot-ui")

markdown("""
## ۶. اختیاری: اجرای بزرگ‌تر

ابتدا خطاهای فنی را رفع و نتیجهٔ پایلوت را **با برچسب‌گذاری انسانی** مقایسه کنید. تیک زیر به معنی ارزیابی خودکار کیفیت نیست؛ مسئولیت بررسی با شماست. برای ارزیابی نهایی از نمونهٔ انسانی تازه‌ای استفاده کنید که برای تنظیم پرامپت ندیده‌اید.

حد اولیه ۱۰۰ کامنتِ تصادفی است. تیک `RUN_ALL_ROWS` همهٔ ردیف‌ها را انتخاب می‌کند و ممکن است زمان و هزینهٔ زیادی داشته باشد. نتیجه‌های همان تنظیمات از پایلوت دوباره استفاده می‌شوند تا دوباره هزینه نداشته باشند. بعد از تغییر مدل یا پرامپت باید پایلوت را دوباره انجام دهید.

با دکمهٔ توقف Colab یا Runtime → Interrupt execution می‌توانید اجرا را قطع کنید. نتیجهٔ تکمیل‌شدهٔ هر ردیف در پوشهٔ `lab_outputs` ذخیره می‌شود و از بخش ۷ قابل دانلود است. قطع کردن ممکن است درخواستِ درحال‌پردازش را نزد سرویس لغو نکند. قبل از پایان نشست نتیجه را دانلود کنید؛ راه‌اندازی مجدد Runtime حافظه و فایل‌های موقت را از بین می‌برد.
""")
code('''#@title ۶) اجرای بزرگ‌تر — در حالت پیش‌فرض خاموش است
I_REVIEWED_THE_PILOT_AND_COST = False #@param {type:"boolean"}
MAX_COMMENTS = 100 #@param {type:"integer"}
RUN_ALL_ROWS = False #@param {type:"boolean"}
if not I_REVIEWED_THE_PILOT_AND_COST:
    print("خاموش است. فقط پس از بررسی پایلوت و هزینه، تیک تأیید را بزنید و این بخش را اجرا کنید.")
elif not isinstance(MAX_COMMENTS, int) or MAX_COMMENTS < 1:
    print("MAX_COMMENTS باید عدد صحیح مثبت باشد.")
else:
    run_current(limit=None if RUN_ALL_ROWS else MAX_COMMENTS, scope="all_rows" if RUN_ALL_ROWS else "larger_sample", reviewed=True)
''', "full-run-ui")

markdown("""
## ۷. مرور، دانلود و مقایسهٔ دو پرامپت

پس از هر آزمایش تازه، این بخش را دوباره ▶ کنید تا فهرست اجراها به‌روز شود. یک اجرا را برای دیدن و دانلود انتخاب کنید. برای مقایسه، دو اجرای مربوط به **همان فایل و ستون‌ها** را انتخاب کنید. جدول می‌گوید برچسب چند کامنت مشترک عوض شده است؛ **نمی‌گوید کدام پرامپت درست‌تر است**. خطاها از مقایسهٔ برچسب‌ها کنار گذاشته می‌شوند و تعداد کامنت‌های مشترک معتبر مشخص است.

برای تحویل: Excel نتیجه، دو نسخهٔ پرامپت (در `run.json`)، و توضیح کوتاهی دربارهٔ چند اختلاف مهم را ارسال کنید. فراوانی کامنت‌های این ویدئو را به همهٔ مردم تعمیم ندهید؛ رأی‌های کاربران یوتیوب نمونهٔ تصادفی جمعیت نیست.
""")
code('''#@title ۷) مرور اجراها و مقایسهٔ تغییر برچسب‌ها
if not STATE["runs"]:
    print("هنوز اجرایی ثبت نشده است. بخش ۵ را اجرا کنید.")
else:
    options = [(f"{i+1}: {r['scope']} · {r['config']['provider']} · {r['config']['requested_model']} · {r['config_hash'][:8]}", i) for i, r in enumerate(STATE["runs"])]
    review = widgets.Dropdown(options=options, value=len(options)-1, description="Review:", layout=widgets.Layout(width="95%"))
    review_output = widgets.Output()
    def review_selected(*_):
        with review_output:
            clear_output(wait=True)
            show_run(STATE["runs"][review.value])
    review.observe(review_selected, names="value")
    display(review, review_output)
    review_selected()
    left = widgets.Dropdown(options=options, value=0, description="Run A:", layout=widgets.Layout(width="95%"))
    right = widgets.Dropdown(options=options, value=len(options)-1, description="Run B:", layout=widgets.Layout(width="95%"))
    compare = widgets.Button(description="مقایسهٔ A و B", disabled=len(options)<2)
    comparison = widgets.Output()
    def compare_selected(_):
        with comparison:
            clear_output(wait=True)
            try:
                a, b = STATE["runs"][left.value], STATE["runs"][right.value]
                if a is b:
                    print("دو اجرای متفاوت انتخاب کنید.")
                    return
                counts, changed = compare_runs(a, b)
                if a["config_hash"] == b["config_hash"]:
                    print("تنظیمات دو اجرا یکسان است؛ پاسخ‌های cache آزمایش مستقل تازه محسوب نمی‌شوند.")
                display(counts)
                display(changed.head(30))
                print("این جدول تغییر خروجی را نشان می‌دهد، نه accuracy یا برتری پرامپت.")
            except ValueError as exc:
                print(str(exc))
    compare.on_click(compare_selected)
    display(HTML("<hr><b>مقایسهٔ دو اجرا</b>"), left, right, compare, comparison)
''', "comparison-ui")

markdown("""
## اگر اجرا نشد

- **کلید یا اعتبار حساب:** خطای 401/403 یعنی کلید یا دسترسی مشکل دارد؛ 402 معمولاً به اعتبار/محدودیت هزینه مربوط است. حساب را بررسی و بخش ۳ و سپس پایلوت را اجرا کنید.
- **مدل پیدا نشد:** شناسهٔ دقیق مدل را از سرویس بردارید. OpenRouter به پیشوند شرکت نیاز دارد، مانند `openai/gpt-4o-mini`. مدل بدون اجازه به سرویس یا شرکت دیگری عوض نمی‌شود.
- **429 یا وقفهٔ سرویس:** برنامه چند بار محدود تلاش می‌کند. اگر حل نشد، کمی بعد دوباره اجرا کنید.
- **`invalid_output`:** مدل از نام برچسب‌ها یا قالب پیروی نکرده، یا پاسخ ناقص بوده است. پاسخ خام را در `run.json` ببینید؛ پرامپت را اصلاح و دوباره پایلوت بگیرید. این ردیف رأیِ «خنثی» محسوب نمی‌شود.
- **متن فارسی نامفهوم:** Encoding فایل CSV را در بخش ۲ عوض کنید یا از Excel خروجی UTF-8 CSV بگیرید.
- **کادرها دیده نمی‌شوند:** بخش ۱ و سپس بخش موردنظر را دوباره اجرا کنید. برای شروع کاملاً تازه: Runtime → Restart session؛ پس از آن همهٔ مراحل را به‌ترتیب انجام دهید.
- **توقف وسط اجرا:** بخش ۷ را اجرا کنید و نتیجهٔ جزئی را دانلود کنید. تا وقتی نشست زنده است، پاسخ‌های تکمیل‌شدهٔ همان تنظیمات دوباره مصرف نمی‌شوند.

راهنمای API: [OpenRouter Chat Completions](https://openrouter.ai/docs/api/reference/overview)، [فهرست مدل‌ها](https://openrouter.ai/models)، [GapGPT](https://gapgpt.app/). در این دفتر از نقطهٔ پایانی OpenAI-compatible گپ‌جی‌پی‌تی در `https://api.gapgpt.app/v1/chat/completions` استفاده می‌شود. دسترسی و موجودبودن مدل‌ها به حساب شما بستگی دارد.
""")

notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {"colab": {"name": "YouTube_AI_Comments_Analysis.ipynb", "provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}}, "cells": cells}
path = ROOT / "YouTube_AI_Comments_Analysis.ipynb"
path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"Built {path.name}: {len(cells)} cells, no outputs or API keys")
