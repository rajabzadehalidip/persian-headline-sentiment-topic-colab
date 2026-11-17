"""Build the Persian, screenshot-rich beginner guide for the Colab comments lab.

Requires reportlab, arabic-reshaper, python-bidi, and Pillow. The PDF is written
to output/pdf/youtube-comments-guide-fa.pdf and uses captured real Colab screens.
"""

from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "youtube-comments-guide-fa.pdf"
SHOTS = ROOT / "docs" / "real-colab"
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")

pdfmetrics.registerFont(TTFont("Arial", str(FONT)))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_BOLD)))

NAVY = colors.HexColor("#172A46")
BLUE = colors.HexColor("#245DA8")
TEAL = colors.HexColor("#178A83")
INK = colors.HexColor("#243247")
MUTED = colors.HexColor("#63738A")
PALE = colors.HexColor("#EEF4FA")
PALE_TEAL = colors.HexColor("#EAF6F4")
GOLD = colors.HexColor("#F3C969")
WHITE = colors.white


def rtl(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text), base_dir="R")


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(rtl(text)), style)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="Arial-Bold", fontSize=25, leading=34,
    alignment=TA_RIGHT, textColor=NAVY, spaceAfter=7 * mm,
))
styles.add(ParagraphStyle(
    name="CoverSub", fontName="Arial", fontSize=13, leading=21,
    alignment=TA_RIGHT, textColor=MUTED, spaceAfter=5 * mm,
))
styles.add(ParagraphStyle(
    name="Section", fontName="Arial-Bold", fontSize=17, leading=24,
    alignment=TA_RIGHT, textColor=BLUE, spaceBefore=1 * mm, spaceAfter=4 * mm,
))
styles.add(ParagraphStyle(
    name="BodyFa", fontName="Arial", fontSize=11.1, leading=18,
    alignment=TA_RIGHT, textColor=INK, spaceAfter=3 * mm,
))
styles.add(ParagraphStyle(
    name="SmallFa", fontName="Arial", fontSize=9.4, leading=14,
    alignment=TA_RIGHT, textColor=MUTED, spaceAfter=2 * mm,
))
styles.add(ParagraphStyle(
    name="Callout", fontName="Arial-Bold", fontSize=12, leading=19,
    alignment=TA_RIGHT, textColor=NAVY,
))
styles.add(ParagraphStyle(
    name="CellFa", fontName="Arial", fontSize=9.2, leading=14,
    alignment=TA_RIGHT, textColor=INK,
))
styles.add(ParagraphStyle(
    name="Caption", fontName="Arial", fontSize=8.8, leading=13,
    alignment=TA_CENTER, textColor=MUTED, spaceBefore=2 * mm,
))
styles.add(ParagraphStyle(
    name="NotebookLink", fontName="Arial-Bold", fontSize=10.5, leading=16,
    alignment=TA_CENTER, textColor=BLUE, spaceBefore=3 * mm,
))


class GuideDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=19 * mm,
            bottomMargin=18 * mm,
            title="راهنمای آزمایش کامنت‌های یوتیوب در Google Colab",
            author="Text Analysis Classroom Lab",
        )
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height, id="main", leftPadding=0,
            rightPadding=0, topPadding=0, bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="guide", frames=frame, onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 9 * mm, width, 9 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, height - 10.3 * mm, width, 1.3 * mm, fill=1, stroke=0)
        canvas.setFont("Arial", 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(width - 18 * mm, 10 * mm, rtl("راهنمای دانشجو | آزمایش کامنت‌های یوتیوب"))
        canvas.drawString(18 * mm, 10 * mm, str(doc.page))
        canvas.restoreState()


def bullet(text: str):
    return p("• " + text, styles["BodyFa"])


def numbered(n: int, text: str):
    return p(f"{n}. {text}", styles["BodyFa"])


def box(text: str, fill=PALE):
    t = Table([[p(text, styles["Callout"])]], colWidths=[174 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#CAD7E5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
    ]))
    return t


def screen(filename: str, caption: str, width=170 * mm):
    path = SHOTS / filename
    im = Image(str(path))
    im.drawWidth = width
    im.drawHeight = width * 720 / 1280
    return [im, p(caption, styles["Caption"])]


def task_page(title: str, items, screenshot=None):
    result = [p(title, styles["Section"]), Spacer(1, 1.5 * mm)]
    for item in items:
        result.append(item)
    if screenshot:
        result += [Spacer(1, 3 * mm)] + screen(*screenshot)
    return result


OUT.parent.mkdir(parents=True, exist_ok=True)
story = []

# Cover: plainly answer whether the student data is inside the notebook.
story += [Spacer(1, 8 * mm)]
story.append(p("راهنمای قدم‌به‌قدم آزمایش کامنت‌های یوتیوب", styles["CoverTitle"]))
story.append(p("تحلیل خوش‌بینی یا بدبینی به AI، هیجان بیان‌شده و موضع نسبت به ادعاهای ویدئو؛ بدون نیاز به برنامه‌نویسی", styles["CoverSub"]))
story.append(box("نکتهٔ اصلی: فایل کامنت‌ها داخل Colab یا GitHub نیست. QR یا لینک فقط دفتر را باز می‌کند. برای آزمایش، فایل مجاز کامنت را جداگانه تهیه و در Colab بارگذاری کنید.", PALE_TEAL))
story.append(Spacer(1, 5 * mm))
story.append(p("در این راهنما می‌بینید چگونه نسخهٔ شخصی دفتر را بسازید، سلول‌ها را به‌ترتیب اجرا کنید، فایل را بارگذاری کنید، کلید API را محرمانه وارد کنید، یک پایلوت ۱۰تایی بگیرید، پرامپت را تغییر دهید و خروجی را با برچسب انسانی بسنجید.", styles["BodyFa"]))
story.append(p("تصاویر این دفترچه از رابط واقعی Google Colab گرفته شده‌اند. هنگام تهیهٔ تصاویر، Google به این محیط اجرای متصل اختصاص نداد؛ بنابراین هیچ تصویر ساختگی از آپلود یا نتیجهٔ موفق مدل در این راهنما نیست.", styles["SmallFa"]))
story += screen("01-open-comments.png", "تصویر ۱. دفتر واقعی آزمایش کامنت‌ها در Google Colab")
story.append(PageBreak())

# Prepare account copy and runtime.
story += task_page("۱. دفتر را باز کنید و نسخهٔ شخصی بسازید", [
    p("از لینک Colab یا QR روی اسلاید وارد دفتر شوید. این لینک یک دفتر عمومی ذخیره‌شده در GitHub را در رابط Colab باز می‌کند؛ فایل کامنت شما را بارگذاری نمی‌کند.", styles["BodyFa"]),
    numbered(1, "از منوی بالای صفحه، File را باز کنید."),
    numbered(2, "گزینهٔ Save a copy in Drive را انتخاب کنید."),
    numbered(3, "نسخهٔ ساخته‌شده در Google Drive خودتان را ادامه دهید. این نسخه را می‌توانید اجرا کنید و پرامپت آن را برای آزمایش تغییر دهید."),
    p("اگر Google درخواست ورود کرد، با حساب خود وارد شوید. کلید API را هنوز جایی ننویسید.", styles["SmallFa"]),
], ("02-save-copy-menu.png", "تصویر ۲. منوی واقعی File و گزینهٔ Save a copy in Drive"))
story.append(PageBreak())

story += task_page("۲. به محیط اجرای Colab وصل شوید", [
    numbered(1, "دکمهٔ Connect را در گوشهٔ بالا سمت راست بزنید."),
    numbered(2, "چند لحظه صبر کنید. پس از اتصال، Colab وضعیت محیط اجرا یا مصرف RAM را نشان می‌دهد."),
    p("برای این آزمایش GPU لازم نیست. گاهی Colab به‌دلیل محدودیت دسترسی شبکه یا منطقه محیط اجرا نمی‌دهد. هنگام ثبت تصویر واقعی این راهنما، پیام Failed to assign a backend نمایش داده شد. این پیام خطای کد، فایل یا API key نیست؛ تا وقتی runtime وصل نشده، سلول‌ها اجرا نمی‌شوند. بعداً دوباره امتحان کنید یا از مدرس راهنمایی بگیرید.", styles["BodyFa"]),
    box("اگر همین پیام را می‌بینید، ابتدا اتصال Colab را حل کنید. اجرای دوبارهٔ سلول‌ها به‌تنهایی محیط اجرا ایجاد نمی‌کند."),
], ("03-connect-runtime.png", "تصویر ۳. خطای واقعی Colab هنگام تلاش برای اختصاص محیط اجرا"))
story.append(PageBreak())

story += task_page("۳. سلول‌های آماده‌سازی و بارگذاری فایل", [
    p("در دفتر، بخش‌های شماره‌دار را از بالا به پایین پیش ببرید. هر سلول کد یک دکمهٔ گرد ▶ در سمت چپ دارد. روی ▶ کلیک کنید و صبر کنید تا اجرای همان سلول تمام شود. کد را تغییر ندهید. متن‌های راهنما سلول متنی هستند و دکمهٔ اجرا ندارند.", styles["BodyFa"]),
    numbered(1, "در بخش ۱، آماده‌سازی را اجرا کنید. اجرای اول ممکن است چند دقیقه بسته‌ها را آماده کند. پیام آماده‌شدن را زیر سلول بخوانید."),
    numbered(2, "در بخش ۲، دکمهٔ ▶ را بزنید تا کنترل بارگذاری فایل ظاهر شود."),
    numbered(3, "فایل CSV، TSV، Excel با پسوند xlsx، JSON، JSONL یا TXT را از رایانه انتخاب کنید."),
    numbered(4, "پیش‌نمایش را بخوانید. برای Excel شیت درست را انتخاب کنید؛ سپس فهرست ستون متن را روی ستونی بگذارید که خود کامنت‌ها در آن هستند."),
    numbered(5, "اگر از کامنت والد استفاده می‌کنید، ستون اختیاری باید متن کامنت والد باشد، نه شناسهٔ آن. نام کاربری و ستون‌های دیگر خودکار برای مدل فرستاده نمی‌شوند."),
    box("برای TXT هر خط یک کامنت است. برای متن‌های چندخطی از CSV یا Excel استفاده کنید.", PALE_TEAL),
    p("فایل کامنت‌های این آزمایش عمومی نیست و در مخزن GitHub قرار نگرفته است. فقط داده‌ای را بارگذاری کنید که اجازهٔ تحلیل آن را دارید.", styles["SmallFa"]),
])
story.append(PageBreak())

story += task_page("۴. سرویس مدل را انتخاب کنید و کلید را محرمانه وارد کنید", [
    p("در بخش ۳، در فهرست PROVIDER سرویس GapGPT یا OpenRouter را انتخاب کنید و ▶ همان سلول را بزنید.", styles["BodyFa"]),
    numbered(1, "شناسهٔ مدل را می‌توانید خالی بگذارید تا پیش‌فرض سرویس استفاده شود. GapGPT از gpt-4o-mini استفاده می‌کند؛ OpenRouter از openai/gpt-4o-mini."),
    numbered(2, "کلید API را فقط در کادر رمز مخفی وارد کنید و Enter بزنید. آن را در کد، متن پرامپت، فایل خروجی، اسلاید یا گروه کلاس ننویسید و از کادر عکس نگیرید."),
    numbered(3, "گزینهٔ USE_COLAB_SECRET اختیاری است. اگر Secrets را از قبل تنظیم نکرده‌اید، برای شروع از کادر رمز پیش‌فرض استفاده کنید."),
    p("کلید در فایل خروجی ذخیره نمی‌شود و فقط در حافظهٔ همین نشست می‌ماند. درخواست‌ها متن کامنت و در صورت انتخاب متن والد را به سرویس انتخابی می‌فرستند. استفاده از API ممکن است هزینه داشته باشد یا به محدودیت حساب برسد.", styles["BodyFa"]),
], ("04-provider-form-real-colab.png", "تصویر ۴. فرم واقعی Colab برای انتخاب سرویس و شناسهٔ مدل"))
story.append(PageBreak())

story += task_page("۵. ادعاهای ویدئو و پرامپت را تنظیم کنید", [
    p("در بخش ۴، ▶ را بزنید. دو کادر قابل ویرایش ظاهر می‌شود:", styles["BodyFa"]),
    numbered(1, "در کادر اول، دو یا سه جمله دربارهٔ ادعاهای واقعی و اصلی ویدئو بنویسید. موضوع کلی «اثر AI بر تکامل انسان» به‌تنهایی برای تشخیص موافقت یا مخالفت کافی نیست. دفتر ویدئو را از روی لینک تماشا نمی‌کند."),
    numbered(2, "در کادر دوم، دستور تحلیل مدل را ویرایش کنید. مثلاً تعریف کنایه یا شرایط استفاده از برچسب mixed را روشن‌تر کنید. نام برچسب‌های مجاز را تغییر ندهید."),
    numbered(3, "پیش از دیدن پاسخ مدل، دکمهٔ دانلود نمونه برای برچسب انسانی را بزنید و خودتان همان نمونهٔ ۱۰تایی را برچسب‌گذاری کنید."),
    p("این برچسب‌های انسانی مرجع کوچکی برای بررسی مدل می‌شوند. آن‌ها را پیش از دیدن پاسخ مدل کامل کنید تا از تأثیر جواب مدل بر قضاوت خودتان کم شود.", styles["BodyFa"]),
], ("05-prompt-widgets-real-colab.png", "تصویر ۵. محیط واقعی Colab در بخش تنظیم سرویس و دستورهای قابل ویرایش"))
story.append(PageBreak())

# Targets and pilot table.
story.append(p("۶. سه سؤال جداگانه را روی پایلوت اجرا کنید", styles["Section"]))
story.append(p("در بخش ۵، دکمهٔ ▶ را بزنید. دفتر روی نمونهٔ ثابت ۱۰ کامنتی کار می‌کند و برای هر کامنت سه برچسب می‌گیرد. درخواست API ممکن است چند لحظه طول بکشد.", styles["BodyFa"]))
rows = [
    [p("پرسش", styles["CellFa"]), p("چه چیزی بررسی می‌شود؟", styles["CellFa"]), p("برچسب‌ها", styles["CellFa"])],
    [p("نگاه به AI", styles["CellFa"]), p("خوش‌بینی یا بدبینی نسبت به اثر AI بر آیندهٔ انسان", styles["CellFa"]), p("optimistic، pessimistic، mixed، neutral، unclear", styles["CellFa"])],
    [p("هیجان", styles["CellFa"]), p("هیجانی که در متن کامنت بیان شده است", styles["CellFa"]), p("hope، joy، fear، anger، sadness، disgust، surprise، neutral، mixed، unclear", styles["CellFa"])],
    [p("موضع نسبت به ویدئو", styles["CellFa"]), p("موافقت یا مخالفت با ادعاهای واقعی ویدئو", styles["CellFa"]), p("agree، disagree، mixed، not_addressed، unclear", styles["CellFa"])],
]
tbl = Table(rows, colWidths=[34 * mm, 65 * mm, 75 * mm], repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), PALE),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D5E3")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
    ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
    ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_TEAL]),
]))
story += [tbl, Spacer(1, 4 * mm)]
story.append(box("این سه بُعد را با هم اشتباه نگیرید: ممکن است یک نفر از AI بترسد، ولی با هشدار ویدئو موافق باشد.", PALE_TEAL))
story.append(Spacer(1, 4 * mm))
story.append(p("جدول خروجی، برچسب، دلیل کوتاه، عبارت شاهد و پرچم needs_review را نشان می‌دهد. unclear یعنی متن برای تصمیم مطمئن کافی نیست. api_error یا invalid_output پاسخ معتبر نیست. نمودارها فراوانی برچسب‌های مدل‌اند، نه دقت مدل و نه نظر همهٔ مردم.", styles["BodyFa"]))
story.append(PageBreak())

story += task_page("۷. پرامپت را تغییر دهید و آزمایش A/B انجام دهید", [
    numbered(1, "فقط یک بخش از پرامپت را تغییر دهید؛ مثلاً تعریف mixed یا نحوهٔ تفسیر کنایه."),
    numbered(2, "مدل، فایل، ستون و نمونه را ثابت نگه دارید تا اثر همان تغییر را ببینید."),
    numbered(3, "فقط سلول بخش ۵ را دوباره اجرا کنید. نمونه با بذر ثابت انتخاب می‌شود و همان ۱۰ کامنت را می‌سنجد."),
    numbered(4, "در بخش ۷، دو اجرا را انتخاب و مقایسهٔ A و B را بزنید. جدول تعداد برچسب‌های تغییرکرده را نشان می‌دهد."),
    box("تغییر برچسب به‌تنهایی نشان نمی‌دهد کدام پرامپت درست‌تر است. آن را با برچسب انسانی و متن واقعی کامنت بسنجید."),
    p("اگر مدل، پرامپت و ورودی یکسان باشند، دفتر پاسخ قبلی همان نشست را دوباره استفاده می‌کند تا هزینهٔ دوباره ایجاد نشود. پاسخ ذخیره‌شده، اجرای مستقلی نیست.", styles["BodyFa"]),
])
story.append(PageBreak())

story += task_page("۸. نتیجه را مرور و دانلود کنید", [
    numbered(1, "پس از اجرای تازه، سلول بخش ۷ را اجرا کنید تا فهرست اجراها تازه شود."),
    numbered(2, "اجرای موردنظر را انتخاب کنید و ردیف‌های needs_review، شاهدها و خطاهای فنی را بخوانید."),
    numbered(3, "دکمهٔ دانلود نتیجهٔ این اجرا (ZIP) را بزنید. فایل ZIP شامل نتیجه‌ها و گزارش JSON اجرای مدل است."),
    numbered(4, "فایل را پیش از بستن یا راه‌اندازی دوبارهٔ نشست ذخیره کنید. راه‌اندازی مجدد حافظه و فایل‌های موقت نشست را پاک می‌کند."),
    p("گزارش JSON، پرامپت و تنظیمات اجرا و پاسخ‌های خام را برای بازبینی حفظ می‌کند. کلید API را به اشتراک نگذارید. تعداد برچسب‌ها را به همهٔ مردم یا حتی همهٔ بینندگان ویدئو تعمیم ندهید؛ این نمونه، نظرسنجی نماینده نیست.", styles["BodyFa"]),
])
story.append(PageBreak())

story += task_page("۹. فقط پس از بررسی، اجرای بزرگ‌تر را فعال کنید", [
    numbered(1, "خطاهای فنی پایلوت را برطرف کنید."),
    numbered(2, "پاسخ‌های پایلوت را با برچسب‌های انسانی مقایسه و موارد اختلاف را بررسی کنید."),
    numbered(3, "اگر لازم است پرامپت یا مدل را اصلاح کنید و دوباره پایلوت بگیرید."),
    numbered(4, "برای سنجش نهایی، نمونهٔ انسانی تازه‌ای به‌کار ببرید که برای تنظیم پرامپت ندیده‌اید."),
    numbered(5, "هزینه و محدودیت حساب را بررسی کنید. سپس در بخش ۶ گزینهٔ بازبینی انسانی/هزینه را تأیید کنید."),
    p("اجرای بزرگ‌تر با حداکثر اولیهٔ ۱۰۰ کامنت و RUN_ALL_ROWS خاموش شروع می‌شود. اجرای همهٔ ردیف‌ها می‌تواند زمان و هزینهٔ زیادی داشته باشد. تغییر پرامپت یا مدل یعنی پایلوت تازه. کیفیت هیچ‌وقت تضمین‌شده نیست؛ نتیجه را انسان باید بازبینی کند.", styles["BodyFa"]),
    box("مسیر درست: نمونهٔ کوچک ← بررسی انسان ← اصلاح پرامپت ← آزمون تازه ← گسترش مرحله‌ای.", PALE_TEAL),
])
story.append(PageBreak())

story.append(p("۱۰. اگر مشکلی پیش آمد", styles["Section"]))
for text in [
    "Failed to assign a backend: Colab محیط اجرا اختصاص نداده است. این خطای کد یا کلید نیست؛ بعداً دوباره تلاش کنید یا از مدرس کمک بگیرید.",
    "401 یا 403: کلید، سرویس انتخابی یا دسترسی به مدل را بررسی کنید.",
    "402: اعتبار یا محدودیت هزینهٔ حساب را بررسی کنید.",
    "مدل پیدا نشد: شناسهٔ مدل را از سرویس خود بررسی کنید. شناسهٔ OpenRouter معمولاً پیشوند شرکت دارد.",
    "429 یا وقفهٔ موقت: کمی صبر کنید و بعد دوباره اجرا کنید.",
    "فارسی ناخوانا: CSV را با UTF-8 ذخیره کنید یا فایل Excel را انتخاب کنید.",
    "فهرست‌ها ظاهر نشدند: اجرای سلول قبلی را کامل کنید، سپس همان بخش را دوباره اجرا کنید.",
    "توقف وسط اجرا: اجرا را متوقف کنید، خروجی‌های کامل‌شده را از بخش ۷ بازبینی و ZIP را پیش از پایان نشست دانلود کنید.",
]:
    story.append(bullet(text))
story.append(Spacer(1, 2 * mm))
story.append(p("پرسش پرتکرار: آیا دادهٔ ۲٬۰۰۰ تیتر فارسی هم داخل Colab است؟", styles["Section"]))
story.append(p("این داده مربوط به آزمایش جداگانهٔ تیترهاست. فایل ۲٬۰۰۰ تیتر و الگوی خالی ۱۰۰تایی در مخزن GitHub موجودند، اما دفتر آن‌ها را خودکار دریافت نمی‌کند؛ دانشجو باید هر دو فایل را دانلود و در بخش بارگذاری Colab انتخاب کند. الگوی ۱۰۰تایی خالی است: ابتدا دو نفر مستقل برچسب می‌زنند و سپس دربارهٔ اختلاف‌ها به اجماع می‌رسند.", styles["BodyFa"]))
story.append(box("خلاصه: فایل کامنت‌ها در این مخزن نیست و باید جداگانه تهیه شود. فایل تیترها در مخزن هست، اما باید دانلود و در دفتر بارگذاری شود. QR فقط دفتر را باز می‌کند."))
story.append(Spacer(1, 4 * mm))
story.append(Paragraph(
    '<link href="https://colab.research.google.com/github/rajabzadehalidip/persian-headline-sentiment-topic-colab/blob/main/YouTube_AI_Comments_Analysis.ipynb" color="#245DA8">Open the YouTube comments notebook in Google Colab</link>',
    styles["NotebookLink"],
))

doc = GuideDoc(str(OUT))
doc.build(story)
print(f"Created {OUT}")
