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

st.title("議会見える化＠江東区")


logs = pd.read_csv(
    "./koto_gijiroku2015-2022.9.csv", encoding="UTF-8"
)  # dataframeとしてcsvを読み込み
giin_list_temp = pd.read_csv("./koto_giin2015-2021.csv", encoding="UTF-8")
giin_list = giin_list_temp["氏名"]

iinkai_list_temp = pd.read_csv("./koto_iinkai2015-2021.csv", encoding="UTF-8")
iinkai_list = iinkai_list_temp["委員会"]


option_selected_g = st.radio(
    # "初回読み込み時は「議席番号1番議員」のワードクラウド」を生成。表示完了後、リストボックスより他の議員を選択できます。（表示は議席番号順）",
    "議員を選択してください。（初回は自動でサンプルを表示）",
    giin_list,
    # index=0,
)
st.write(
    "<style>div.row-widget.stRadio > div{flex-direction:row;}</style>",
    unsafe_allow_html=True,
)

# 委員会選択
with st.expander("「会議体」を選択できます。", False):
    option_selected_i = st.multiselect(
        "初期値は全ての会議体が選択されてます。",
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
with st.expander("「期間」を選択できます。", False):
    # 年度選択
    start_year, end_year = st.select_slider(
        "初期値は検索可能な全ての年度が選択されてます。",
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

my_bar = st.progress(0)
time.sleep(0.01)
for percent_complete in range(100):
    time.sleep(0.01)
    my_bar.progress(percent_complete + 1)


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
    "**【分析した議員名】**",
    option_selected_g,
    "**【分析期間】**",
    str(start_year),
    "-",
    str(end_year),
    "**【作成日】**",
    dt_now,
)

stpwds = [
    "視点",
    "視点",
    "認識",
    "取組",
    "辺り",
    "具体",
    "面",
    "令和",
    "様",
    "辺",
    "なし",
    "分",
    "款",
    "皆",
    "さん",
    "議会",
    "文",
    "場所",
    "現在",
    "ら",
    "方々",
    "こちら",
    "性",
    "化",
    "場合",
    "対象",
    "一方",
    "皆様",
    "考え",
    "それぞれ",
    "意味",
    "とも",
    "内容",
    "とおり",
    "目",
    "事業",
    "つ",
    "見解",
    "検討",
    "本当",
    "議論",
    "民",
    "地域",
    "万",
    "確認",
    "実際",
    "先ほど",
    "前",
    "後",
    "利用",
    "説明",
    "次",
    "あたり",
    "部分",
    "状況",
    "わけ",
    "話",
    "答弁",
    "資料",
    "半ば",
    "とき",
    "支援",
    "形",
    "今回",
    "中",
    "対応",
    "必要",
    "今後",
    "質問",
    "取り組み",
    "終了",
    "暫時",
    "午前",
    "たち",
    "九十",
    "八十",
    "七十",
    "六十",
    "五十",
    "四十",
    "三十",
    "問題",
    "提出",
    "進行",
    "付託",
    "議案",
    "動議",
    "以上",
    "程度",
    "異議",
    "開会",
    "午後",
    "者",
    "賛成",
    "投票",
    "再開",
    "休憩",
    "質疑",
    "ただいま",
    "議事",
    "号",
    "二十",
    "平成",
    "等",
    "会",
    "日",
    "月",
    "年",
    "年度",
    "委員",
    "江東",
    "点",
    "区",
    "委員会",
    "賛成者",
    "今",
    "江東区",
    "もの",
    "こと",
    "ふう",
    "ところ",
    "ほう",
    "これ",
    "私",
    "わたし",
    "僕",
    "あなた",
    "みんな",
    "ただ",
    "ほか",
    "それ",
    "もの",
    "これ",
    "ところ",
    "ため",
    "うち",
    "ここ",
    "そう",
    "どこ",
    "つもり",
    "いつ",
    "あと",
    "もん",
    "はず",
    "こと",
    "そこ",
    "あれ",
    "なに",
    "傍点",
    "まま",
    "事",
    "人",
    "方",
    "何",
    "時",
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "十",
    "的",
    "よう",
    "ん",
    "の",
    "名",
    "件数",
    "円",
    "お答え",
    "本",
    "非常",
    "令和３年度",
    "令和3年度",
    "以降",
    "どれ",
    "現状",
    "平成30年度",
    "平成３０年度",
    "令和２年度",
    "令和2年度",
    "お願い",
    "皆さん",
    "実施",
    "要望",
    "理事者",
    "理事",
    "点目",
    "影響",
    "大変",
    "区長",
    "施設",
    "区民",
    "対策",
    "相談",
    "先",
    "先日",
    "先程",
    "重要",
    "東京都",
    "いかが",
    "伺い",
    "お尋ね",
    "限り",
    "１点",
    "２点",
    "３点",
    "整備",
    "推進",
    "評価",
    "課題",
    "予定",
    "計画",
    "活用",
    "課題",
    "お話",
    "意見",
    "提案",
    "時間",
    "数",
    "最後",
    "お話",
    "近年",
    "確か",
    "さまざま",
    "いろいろ",
    "我々",
    "理由",
    "気",
    "十分",
    "心配",
    "事業者",
    "結果",
    "自分",
    "新た",
    "今度",
    "１つ",
    "大事",
    "この間",
    "たくさん",
    "内",
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
    prefer_horizontal=0.92,
    include_numbers=False,
    max_words=1000,
)
wc.generate(words)
wc.to_file("wc.png")
st.image("wc.png")

# 最後尾に追加
t2 = time.time()
min, sec = sec_to_min_sec(t2 - t1)
st.info(f"ワードクラウド描画完了までの時間 : {sec} sec")

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
            },
            {
                "headerName": "会議名",
                "field": "会議",
                "suppressSizeToFit": True,
                "wrapText": True,
                "autoHeight": True,
                "maxWidth": 100,
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

st.markdown("20221013　ver. 0.9.3")
