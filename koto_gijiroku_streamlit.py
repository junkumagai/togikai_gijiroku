import os
import random
import subprocess
import time
from datetime import datetime, timedelta, timezone
from time import sleep

import MeCab
import pandas as pd
import streamlit as st
from PIL import Image
from st_aggrid import AgGrid
from wordcloud import WordCloud

mecab = MeCab.Tagger()
font_path = "ShipporiMinchoB1-ExtraBold.ttf"

st.set_page_config(layout="centered", initial_sidebar_state="auto")

st.title("発言見える化＠江東区")


logs = pd.read_csv(
    "./koto_gijiroku2015-2022.9.csv", encoding="UTF-8", low_memory=False
)  # dataframeとしてcsvを読み込み
giin_list_temp = pd.read_csv("./koto_giin2015-2021.csv", encoding="UTF-8")
giin_list = giin_list_temp["氏名"]

iinkai_list_temp = pd.read_csv("./koto_iinkai2015-2021.csv", encoding="UTF-8")
iinkai_list = iinkai_list_temp["委員会"]


option_selected_g = st.radio(
    # "初回読み込み時は「議席番号1番議員」のワードクラウド」を生成。表示完了後、リストボックスより他の議員を選択できます。（表示は議席番号順）",
    "議員を選択（初回は冒頭議員をサンプル表示）",
    giin_list,
    # index=0,
)
st.write(
    "<style>div.row-widget.stRadio > div{flex-direction:row;}</style>",
    unsafe_allow_html=True,
)

# st.button("選択した議員の発言を分析する！")

# 委員会選択
with st.expander("「会議体」を選択（初期値は全て）", False):
    option_selected_i = st.multiselect(
        "会議体を選択して絞り込むことができます。",
        iinkai_list,
        [
            "オリンピック・パラリンピック対策特別委員会",
            "オリンピック・パラリンピック推進特別委員会",
            "まちづくり・南北交通対策特別委員会",
            "予算審査特別委員会",
            "企画総務委員会",
            "区民環境委員会",
            "医療・介護・高齢者支援特別委員会",
            "医療・介護保険制度特別委員会",
            "厚生委員会",
            "地下鉄８号線延伸・交通対策推進特別委員会",
            "定例会",
            "建設委員会",
            "文教委員会",
            "決算審査特別委員会",
            "清掃港湾・臨海部対策特別委員会",
            "臨時会",
            "議会運営委員会",
            "防災・まちづくり・交通対策特別委員会",
            "防災・まちづくり対策特別委員会",
            "防災対策特別委員会",
            "高齢者支援・介護保険制度特別委員会",
        ],
    )
    option_selected_i = "|".join(option_selected_i)

# 委員会選択のテキスト化（後の条件付けのため
f = open("temp_iinkai.txt", "w")  # textに書き込み
f.writelines(option_selected_i)
f.close()
option_selected_i_txt = open("temp_iinkai.txt", encoding="utf8").read()

# st.markdown(' ##### :date:「年度」での絞り込み')
with st.expander("「期間」を選択（初期値は2019年から）", False):
    # 年度選択
    start_year, end_year = st.select_slider(
        "分析対象期間をスライダーで絞り込むことができます。",
        options=[
            "2003",
            "2004",
            "2005",
            "2006",
            "2007",
            "2008",
            "2009",
            "2010",
            "2011",
            "2012",
            "2013",
            "2014",
            "2015",
            "2016",
            "2017",
            "2018",
            "2019",
            "2020",
            "2021",
            "2022",
        ],
        value=("2019", "2022"),
    )

    start_year = int(start_year)
    end_year = int(end_year)

logs_contents_temp = logs[
    (logs["人分類"].str.contains(option_selected_g))
    & (logs["委員会"].str.contains(option_selected_i_txt))
    & (logs["年度"] >= start_year)
    & (logs["年度"] <= end_year)
]

logs_contents_temp_show = logs_contents_temp[
    ["年月日", "人分類", "内容分類", "質問", "回答", "会議", "内容", "年度", "文字数"]
]

logs_contents_temp_moji = logs_contents_temp.groupby("年度").sum()  # 年度ごとの文字数

# 文字カウント
logs_contents_temp_moji = logs_contents_temp_moji["文字数"]

# my_bar = st.progress(0)
# time.sleep(0.01)
# for percent_complete in range(100):
#     time.sleep(0.01)
#     my_bar.progress(percent_complete + 1)

# status_text = st.empty()
# # プログレスバー
# progress_bar = st.progress(0)

# for i in range(100):
#     status_text.text(f"Progress: {i}%")
#     # for ループ内でプログレスバーの状態を更新する
#     progress_bar.progress(i + 1)
#     time.sleep(0.1)

# status_text.text("Done!")
# st.balloons()


def sec_to_min_sec(t):
    min = int(t / 60)
    sec = int(t - min * 60)
    return min, sec


t1 = time.time()

# ワードクラウド作成
logs_contents = logs_contents_temp["内容"]

f = open("temp.txt", "w")  # textに書き込み
f.writelines(logs_contents)
f.close()

text = open("temp.txt", encoding="utf8").read()

results = mecab.parse(text)
result = results.split("\n")[:-2][0]

nouns = []
for result in results.split("\n")[:-2]:
    if "名詞" in result.split("\t")[4]:
        nouns.append(result.split("\t")[0])
words = " ".join(nouns)

# st.markdown('　#### :face_with_monocle: 文字解析の結果')
JST = timezone(timedelta(hours=+9), "JST")
# dt_now = datetime.datetime.now()
dt_now = datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")

st.write(
    "【分析中の議員】",
    option_selected_g,
    "【期間】",
    str(start_year),
    "-",
    str(end_year),
)

#     "**【作成日】**",
#     dt_now,
# )

stpwds = [
    "１つ",
    "１点",
    "２点",
    "３点",
    "あたり",
    "あと",
    "あなた",
    "あれ",
    "いかが",
    "いつ",
    "いろいろ",
    "うち",
    "お尋ね",
    "お答え",
    "お話",
    "お願い",
    "ここ",
    "こちら",
    "こと",
    "これ",
    "さまざま",
    "さん",
    "そう",
    "そこ",
    "それ",
    "それぞれ",
    "ただ",
    "ただいま",
    "たち",
    "ため",
    "つ",
    "つもり",
    "とおり",
    "とき",
    "どこ",
    "ところ",
    "とも",
    "どれ",
    "なし",
    "なに",
    "の",
    "はず",
    "ふう",
    "ほう",
    "ほか",
    "まま",
    "みんな",
    "もの",
    "もん",
    "よう",
    "ら",
    "わけ",
    "わたし",
    "ん",
    "一",
    "一方",
    "七",
    "七十",
    "万",
    "三",
    "三十",
    "中",
    "九",
    "九十",
    "予定",
    "事",
    "事業",
    "事業者",
    "二",
    "二十",
    "五",
    "五十",
    "人",
    "今",
    "今回",
    "今度",
    "今後",
    "付託",
    "令和",
    "令和２年度",
    "令和2年度",
    "令和３年度",
    "令和3年度",
    "以上",
    "以降",
    "件数",
    "休憩",
    "会",
    "伺い",
    "何",
    "傍点",
    "僕",
    "先",
    "先ほど",
    "先日",
    "先程",
    "八",
    "八十",
    "六",
    "六十",
    "具体",
    "内容",
    "円",
    "再開",
    "最後",
    "分",
    "利用",
    "前",
    "動議",
    "化",
    "区",
    "区民",
    "区長",
    "十",
    "十分",
    "午前",
    "午後",
    "半ば",
    "取り組み",
    "取組",
    "号",
    "名",
    "問題",
    "四",
    "四十",
    "地域",
    "場合",
    "場所",
    "大変",
    "委員",
    "委員会",
    "実施",
    "実際",
    "対応",
    "対策",
    "対象",
    "平成",
    "平成30年度",
    "平成３０年度",
    "年",
    "年度",
    "形",
    "影響",
    "後",
    "心配",
    "必要",
    "性",
    "意味",
    "意見",
    "我々",
    "投票",
    "推進",
    "提出",
    "提案",
    "支援",
    "数",
    "整備",
    "文",
    "新た",
    "方",
    "方々",
    "施設",
    "日",
    "時",
    "時間",
    "暫時",
    "月",
    "本",
    "本当",
    "東京都",
    "検討",
    "様",
    "次",
    "款",
    "民",
    "気",
    "江東",
    "江東区",
    "活用",
    "点",
    "点目",
    "状況",
    "現在",
    "現状",
    "理事",
    "理事者",
    "理由",
    "異議",
    "的",
    "皆",
    "皆さん",
    "皆様",
    "目",
    "相談",
    "確か",
    "確認",
    "視点",
    "私",
    "程度",
    "等",
    "答弁",
    "終了",
    "結果",
    "考え",
    "者",
    "自分",
    "要望",
    "見解",
    "計画",
    "評価",
    "話",
    "認識",
    "説明",
    "課題",
    "議事",
    "議会",
    "議案",
    "議論",
    "資料",
    "賛成",
    "賛成者",
    "質問",
    "質疑",
    "辺",
    "辺り",
    "近年",
    "進行",
    "部分",
    "重要",
    "開会",
    "限り",
    "非常",
    "面",
    "大事",
    "この間",
    "たくさん",
    "内",
    "]",
    "あそこ",
    "あちら",
    "あっち",
    "あな",
    "いくつ",
    "いま",
    "いや",
    "おおまか",
    "おまえ",
    "おれ",
    "がい",
    "かく",
    "かたち",
    "かやの",
    "から",
    "がら",
    "きた",
    "くせ",
    "こっち",
    "ごと",
    "ごっちゃ",
    "これら",
    "ごろ",
    "さらい",
    "しかた",
    "しよう",
    "すか",
    "ずつ",
    "すね",
    "すべて",
    "ぜんぶ",
    "そちら",
    "そっち",
    "そで",
    "それなり",
    "たび",
    "だめ",
    "ちゃ",
    "ちゃん",
    "てん",
    "どこか",
    "どちら",
    "どっか",
    "どっち",
    "なか",
    "なかば",
    "など",
    "なん",
    "はじめ",
    "はるか",
    "ひと",
    "ひとつ",
    "ふく",
    "ぶり",
    "べつ",
    "へん",
    "ぺん",
    "まさ",
    "まし",
    "まとも",
    "みたい",
    "みつ",
    "みなさん",
    "もと",
    "やつ",
    "よそ",
    "ハイ",
    "上",
    "下",
    "字",
    "秒",
    "週",
    "火",
    "水",
    "木",
    "金",
    "土",
    "国",
    "都",
    "道",
    "府",
    "県",
    "市",
    "町",
    "村",
    "各",
    "第",
    "度",
    "体",
    "他",
    "部",
    "課",
    "係",
    "外",
    "類",
    "達",
    "室",
    "口",
    "誰",
    "用",
    "界",
    "首",
    "男",
    "女",
    "別",
    "屋",
    "店",
    "家",
    "場",
    "見",
    "際",
    "観",
    "段",
    "略",
    "例",
    "系",
    "論",
    "間",
    "地",
    "員",
    "線",
    "書",
    "品",
    "力",
    "法",
    "感",
    "作",
    "元",
    "手",
    "彼",
    "彼女",
    "子",
    "楽",
    "喜",
    "怒",
    "哀",
    "輪",
    "頃",
    "境",
    "俺",
    "奴",
    "高",
    "校",
    "婦",
    "伸",
    "紀",
    "誌",
    "レ",
    "行",
    "列",
    "士",
    "台",
    "集",
    "所",
    "歴",
    "器",
    "情",
    "連",
    "毎",
    "式",
    "簿",
    "回",
    "匹",
    "個",
    "席",
    "束",
    "歳",
    "通",
    "玉",
    "枚",
    "左",
    "右",
    "春",
    "夏",
    "秋",
    "冬",
    "百",
    "千",
    "億",
    "兆",
    "下記",
    "上記",
    "前回",
    "一つ",
    "年生",
    "ヶ所",
    "ヵ所",
    "カ所",
    "箇所",
    "ヶ月",
    "ヵ月",
    "カ月",
    "箇月",
    "名前",
    "時点",
    "全部",
    "関係",
    "近く",
    "方法",
    "違い",
    "多く",
    "扱い",
    "その後",
    "結局",
    "様々",
    "以前",
    "以後",
    "未満",
    "以下",
    "幾つ",
    "毎日",
    "自体",
    "向こう",
    "何人",
    "手段",
    "同じ",
    "感じ",
    "ア",
    "イ",
    "ウ",
    "可決",
    "一部",
    "改正",
    "エ",
    "件",
    "cid",
    "策",
    "制度",
    "更",
    "オ",
    "区議会",
    "取組み",
    "条例",
    "向上",
    "連携",
    "体制",
    "効果",
    "設置",
    "□",
    "〇",
    "契約",
    "協議",
    "答",
    "問",
    "強化",
    "相手方",
    "陳情",
    "審議",
    "確保",
    "補正予算",
    "職員",
    "開催",
    "回答",
    "君",
    "番",
    "事項",
    "令和4年",
    "令和4年度",
    "東京",
    "知事",
    "都民",
    "議長",
    "三宅",
    "しげき君",
    "審査",
    "報告書",
    "旨",
    "〇〇",
    "条項",
    "運営",
    "項",
    "規定",
    "報告",
    "周知",
]


# カラーマップをランダムに要素選択
bg_color = random.choice(
    [
        "AliceBlue",
        "AntiqueWhite",
        "Aqua",
        "Aquamarine",
        "Azure",
        "Beige",
        "Bisque",
        "Black",
        "BlanchedAlmond",
        "Blue",
        "BlueViolet",
        "Brown",
        "BurlyWood",
        "CadetBlue",
        "Chartreuse",
        "Chocolate",
        "Coral",
        "CornflowerBlue",
        "Cornsilk",
        "Crimson",
        "Cyan",
        "DarkBlue",
        "DarkCyan",
        "DarkGoldenrod",
        "DarkGray",
        "DarkGreen",
        "DarkKhaki",
        "DarkMagenta",
        "DarkOliveGreen",
        "DarkOrange",
        "DarkOrchid",
        "DarkRed",
        "DarkSalmon",
        "DarkSeaGreen",
        "DarkSlateBlue",
        "DarkSlateGray",
        "DarkTurquoise",
        "DarkViolet",
        "DeepPink",
        "DeepSkyBlue",
        "DimGray",
        "DodgerBlue",
        "FireBrick",
        "FloralWhite",
        "ForestGreen",
        "Fuchsia",
        "Gainsboro",
        "GhostWhite",
        "Gold",
        "Goldenrod",
        "Gray",
        "Green",
        "GreenYellow",
        "Honeydew",
        "HotPink",
        "IndianRed",
        "Indigo",
        "Ivory",
        "Khaki",
        "Lavender",
        "LavenderBlush",
        "LawnGreen",
        "LemonChiffon",
        "LightBlue",
        "LightCoral",
        "LightCyan",
        "LightGoldenrodYellow",
        "LightGreen",
        "LightGrey",
        "LightPink",
        "LightSalmon",
        "LightSeaGreen",
        "LightSkyBlue",
        "LightSlateGray",
        "LightSteelBlue",
        "LightYellow",
        "Lime",
        "LimeGreen",
        "Linen",
        "Magenta",
        "Maroon",
        "MediumAquamarine",
        "MediumBlue",
        "MediumOrchid",
        "MediumPurple",
        "MediumSeaGreen",
        "MediumSlateBlue",
        "MediumSpringGreen",
        "MediumTurquoise",
        "MediumVioletRed",
        "MidnightBlue",
        "MintCream",
        "MistyRose",
        "Moccasin",
        "NavajoWhite",
        "Navy",
        "OldLace",
        "Olive",
        "OliveDrab",
        "Orange",
        "OrangeRed",
        "Orchid",
        "PaleGoldenrod",
        "PaleGreen",
        "PaleTurquoise",
        "PaleVioletRed",
        "PapayaWhip",
        "PeachPuff",
        "Peru",
        "Pink",
        "Plum",
        "PowderBlue",
        "Purple",
        "Red",
        "RosyBrown",
        "RoyalBlue",
        "SaddleBrown",
        "Salmon",
        "SandyBrown",
        "SeaGreen",
        "Seashell",
        "Sienna",
        "Silver",
        "SkyBlue",
        "SlateBlue",
        "SlateGray",
        "Snow",
        "SpringGreen",
        "SteelBlue",
        "Tan",
        "Teal",
        "Thistle",
        "Tomato",
        "Turquoise",
        "Violet",
        "Wheat",
        "White",
        "WhiteSmoke",
        "Yellow",
        "YellowGreen",
    ]
)

c_map = random.choice(
    [
        "Accent_r",
        "Accent",
        "afmhot_r",
        "afmhot",
        "autumn_r",
        "autumn",
        "binary_r",
        "binary",
        "Blues_r",
        "Blues",
        "bone_r",
        "bone",
        "BrBG_r",
        "BrBG",
        "brg_r",
        "brg",
        "BuGn_r",
        "BuGn",
        "BuPu_r",
        "BuPu",
        "bwr_r",
        "bwr",
        "cividis_r",
        "cividis",
        "CMRmap_r",
        "CMRmap",
        "cool_r",
        "cool",
        "coolwarm_r",
        "coolwarm",
        "copper_r",
        "copper",
        "cubehelix_r",
        "cubehelix",
        "Dark2_r",
        "Dark2",
        "flag_r",
        "flag",
        "gist_earth_r",
        "gist_earth",
        "gist_gray_r",
        "gist_gray",
        "gist_heat_r",
        "gist_heat",
        "gist_ncar_r",
        "gist_ncar",
        "gist_rainbow_r",
        "gist_rainbow",
        "gist_stern_r",
        "gist_stern",
        "gist_yarg_r",
        "gist_yarg",
        "GnBu_r",
        "GnBu",
        "gnuplot_r",
        "gnuplot",
        "gnuplot2_r",
        "gnuplot2",
        "gray_r",
        "gray",
        "Greens_r",
        "Greens",
        "Greys_r",
        "Greys",
        "hot_r",
        "hot",
        "hsv_r",
        "hsv",
        "inferno_r",
        "inferno",
        "jet_r",
        "jet",
        "magma_r",
        "magma",
        "nipy_spectral_r",
        "nipy_spectral",
        "ocean_r",
        "ocean",
        "Oranges_r",
        "Oranges",
        "OrRd_r",
        "OrRd",
        "Paired_r",
        "Paired",
        "Pastel1_r",
        "Pastel1",
        "Pastel2_r",
        "Pastel2",
        "pink_r",
        "pink",
        "PiYG_r",
        "PiYG",
        "plasma_r",
        "plasma",
        "PRGn_r",
        "PRGn",
        "prism_r",
        "prism",
        "PuBu_r",
        "PuBu",
        "PuBuGn_r",
        "PuBuGn",
        "PuOr_r",
        "PuOr",
        "PuRd_r",
        "PuRd",
        "Purples_r",
        "Purples",
        "rainbow_r",
        "rainbow",
        "RdBu_r",
        "RdBu",
        "RdGy_r",
        "RdGy",
        "RdPu_r",
        "RdPu",
        "RdYlBu_r",
        "RdYlBu",
        "RdYlGn_r",
        "RdYlGn",
        "Reds_r",
        "Reds",
        "seismic_r",
        "seismic",
        "Set1_r",
        "Set1",
        "Set2_r",
        "Set2",
        "Set3_r",
        "Set3",
        "Spectral_r",
        "Spectral",
        "spring_r",
        "spring",
        "summer_r",
        "summer",
        "tab10_r",
        "tab10",
        "tab20_r",
        "tab20",
        "tab20b_r",
        "tab20b",
        "tab20c_r",
        "tab20c",
        "terrain_r",
        "terrain",
        "turbo_r",
        "turbo",
        "twilight_r",
        "twilight_shifted_r",
        "twilight_shifted",
        "twilight",
        "viridis_r",
        "viridis",
        "winter_r",
        "winter",
        "Wistia_r",
        "Wistia",
        "YlGn_r",
        "YlGn",
        "YlGnBu_r",
        "YlGnBu",
        "YlOrBr_r",
        "YlOrBr",
        "YlOrRd_r",
        "YlOrRd",
    ]
)

wc = WordCloud(
    stopwords=stpwds,
    width=720,
    height=1280,
    background_color="white",
    colormap="Dark2",
    # background_color=bg_color,
    # colormap=c_map,
    # colormap='coolwarm',
    font_path=font_path,
    prefer_horizontal=0.94,
    # include_numbers=False,
    max_words=300,
)
wc.generate(words)
wc.to_file("wc.png")
st.image("wc.png")

# 最後尾に追加
t2 = time.time()
min, sec = sec_to_min_sec(t2 - t1)
st.info(f"ワードクラウド描画完了までの時間 : {sec} 秒")

# b0 = time()
# st.subheader("Not using st.cache")

# st.write(load_data_b())
# b1 = time()
# st.info(b1 - b0)

# 集計文字数表示
st.metric(label="計測した発言文字数", value=f"{len(text)} 文字")

with st.expander("発言文字数の推移", True):
    # チャート作成
    st.bar_chart(logs_contents_temp_moji, width=0, use_container_width=True)
    # table作成
with st.expander("解析対象のテキスト", True):

    grid_options = {
        "columnDefs": [
            {
                "headerName": "年月日",
                "field": "年月日",
                "suppressSizeToFit": True,
                "autoHeight": True,
                "maxWidth": 100,
            },
            {
                "headerName": "会議名",
                "field": "会議",
                "suppressSizeToFit": True,
                "wrapText": True,
                "autoHeight": True,
                "maxWidth": 80,
            },
            # {
            #     "headerName": "内容分類",
            #     "field": "内容分類",
            #     "suppressSizeToFit": True,
            #     "autoHeight": True,
            # },
            # {
            #     "headerName": "質問者",
            #     "field": "質問",
            #     "suppressSizeToFit": True,
            #     "wrapText": True,
            #     "maxWidth": 100,
            #     "autoHeight": True,
            # },
            # {
            #     "headerName": "回答者",
            #     "field": "回答",
            #     "suppressSizeToFit": True,
            #     "wrapText": True,
            #     "maxWidth": 100,
            #     "autoHeight": True,
            # },
            # {
            #     "headerName": "人分類",
            #     "field": "人分類",
            #     "suppressSizeToFit": True,
            #     "wrapText": True,
            #     "autoHeight": True,
            # },
            {
                "headerName": "発言内容",
                "field": "内容",
                "wrapText": True,
                "autoHeight": True,
                "suppressSizeToFit": True,
                "maxWidth": 450,
            },
        ],
    }
    AgGrid(logs_contents_temp_show, grid_options)

print("occurrence of substring ats:", words.count("ats"))

st.subheader("感謝")
st.markdown(
    "プログラムソースは、-議員見える化プロジェクト@東京都中央区 https://bit.ly/3Bqfcy0 を作られた[ほづみゆうき](https://twitter.com/ninofku)さんにご提供いただきました。GlideやStreamlitを駆使して華麗にWEBアプリで可視化する、その技術力と行動力に敬服します。ありがとうございます。"
)

st.caption(
    "【更新履歴】20221017　ver.0.9.32　使用帯域を調整、20221015　ver.0.9.31　分析ボタン（処理中断）追加"
)
