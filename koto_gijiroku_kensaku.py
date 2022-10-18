import time

import MeCab
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid

mecab = MeCab.Tagger()
import matplotlib.pyplot as plt
from wordcloud import WordCloud

font_path = "Corporate-Logo-Bold-ver2.otf"
# import datetime
from datetime import datetime, timedelta, timezone

import altair as alt
import numpy as np
import plotly.express as px
from PIL import Image

# st.set_page_config(layout="wide")
st.set_page_config(layout="centered", initial_sidebar_state="auto")
st.title("議事録けんさく＠江東区")

logs = pd.read_csv(
    "./koto_gijiroku2015-2022.9.csv", encoding="UTF-8", low_memory=False
)  # dataframeとしてcsvを読み込み

logs2 = logs[["年月日", "人分類", "内容分類", "質問", "回答", "会議", "内容", "年度", "文字数"]]

option_selected_l = st.text_input(
    "検索キーワード（初期値は「児童手当」、英数字は「ＰＴＡ」のように全角で入力。）", "児童手当"
)
# st.markdown(' ##### :date:「年度」での絞り込み')
with st.expander("「期間」を選択（初期値は2019年から）", True):
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

# 文字列の抽出
# selected_l = logs2 [(logs2['内容'].str.contains(option_selected_l))]
selected_l = logs2[
    (logs2["内容"].str.contains(option_selected_l))
    & (logs2["年度"] >= start_year)
    & (logs2["年度"] <= end_year)
]

# selected_l['内容'] = [i[:2000] for i in selected_l['内容']]


def sec_to_min_sec(t):
    min = int(t / 60)
    sec = int(t - min * 60)
    return min, sec


t1 = time.time()

# ワードクラウド作成
logs_contents = selected_l["内容"]
f = open("temp.txt", "w")  # textに書き込み
f.writelines(logs_contents)
f.close()

text = open("temp.txt", encoding="utf8").read()


with open(
    "temp.txt",
    mode="rt",
    encoding="utf-8",
) as fi:
    source_text = fi.read()

tagger = MeCab.Tagger()
tagger.parse("")
node = tagger.parseToNode(source_text)

# 名詞を取り出す
word_list = []
while node:
    word_type = node.feature.split(",")[0]
    # if word_type == '名詞':
    # if word_type in ["名詞", "固有名詞", "地域", "組織", "人名", "一般"]:
    if word_type in [
        "名詞",
        "固有名詞",
        "地域",
        "組織",
        "人名",
        "一般",
        (not "非自立"),
        (not "代名詞"),
        (not "数"),
    ]:
        # if word_type in ["名詞", "代名詞"]:
        # if word_type in ["動詞", "形容詞", "名詞"]:
        # if word_type in ["名詞", "代名詞", "形容詞"]:
        word_list.append(node.surface)
    node = node.next

# リストを文字列に変換
words = " ".join(word_list)

# results = mecab.parse(text)
# result = results.split("\n")[:-2][0]

# nouns = []
# for result in results.split("\n")[:-2]:
#     if "名詞" in result.split("\t")[4]:
#         nouns.append(result.split("\t")[0])
# words = " ".join(nouns)

# st.markdown('　#### :face_with_monocle: 文字解析の結果')
JST = timezone(timedelta(hours=+9), "JST")
# dt_now = datetime.datetime.now()
dt_now = datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")

st.write(
    "【キーワード】",
    option_selected_l,
    "【期間】",
    str(start_year),
    "-",
    str(end_year),
    # "**[作成日時]**",
    # dt_now,
)

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

# wc= WordCloud(
#     # width=5120,
#     width=2880,
#     # width=1920,
#     # height=2880,
#     height=5120,
#     # height=2560,
#     background_color=bg_color,
#     colormap=c_map,
#     # font_path="/home/jun/Documents/projects/twitter/trends/ipadic-neologd/ipaexm00401/ipaexm.ttf",
#     font_path="/home/jun/Documents/projects/twitter/trends/ipadic-neologd/ShipporiMincho-ExtraBold.ttf",
#     stopwords=words,
#     max_words=20000,
#     prefer_horizontal=0.94,
#     include_numbers=False,
# ).generate(word_chain)

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

# wc = WordCloud(
#     stopwords=stpwds,
#     width=1080,
#     height=1080,
#     background_color="white",
#     font_path=font_path,
# )
wc.generate(words)
wc.to_file("wc.png")
st.image("wc.png")
# 最後尾に追加
t2 = time.time()
min, sec = sec_to_min_sec(t2 - t1)
st.info(f"ワードクラウド描画完了までの時間 : {sec} 秒")


selected_l_moji = selected_l[["年月日", "人分類", "内容分類", "質問", "回答", "内容", "文字数"]]

# 発言文字数ランキング
# st.subheader("発言文字数ランキング")
# st.markdown(
#     "キーワードが含まれる発言内容の文字列をカウントして、ランキング化したものです。ざっくりどの議員がそのテーマに熱心なのかを測るのに使えるかも。"
# )
# st.markdown(
#     "カテゴリとしては以下の3つに分かれています「質問」「回答」キーワードが含まれる発言内容の文字列をカウントして、ランキング化したものです。"
# )
# st.markdown("・「質問」：議員による質問内容")
# st.markdown("・「回答」：議員の質問に対する区長などの回答")
# st.markdown("・「議長/委員長」：会議での議長や委員長としての発言")
logs_contents_temp_moji = selected_l_moji.groupby(
    ["人分類", "内容分類"], as_index=False
).sum()  # 年度ごとの文字数
# st.bar_chart(logs_contents_temp_moji)
fig = px.bar(
    logs_contents_temp_moji,
    x="文字数",
    y="人分類",
    color="内容分類",
    text="文字数",
    # height=800,
    width=640,
    orientation="h",
)
# fig.update_layout(barmode='stack', xaxis={'文字数':'category ascending'})
fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
fig


# 発言内容
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
        {
            "headerName": "内容分類",
            "field": "内容分類",
            "suppressSizeToFit": True,
            "autoHeight": True,
            "maxWidth": 80,
        },
        {
            "headerName": "質問者",
            "field": "質問",
            "suppressSizeToFit": True,
            "wrapText": True,
            "maxWidth": 80,
            "autoHeight": True,
        },
        {
            "headerName": "回答者",
            "field": "回答",
            "suppressSizeToFit": True,
            "wrapText": True,
            "maxWidth": 80,
            "autoHeight": True,
        },
        {
            "headerName": "発言内容",
            "field": "内容",
            "wrapText": True,
            "autoHeight": True,
            "suppressSizeToFit": True,
            "maxWidth": 450,
        },
        # {
        #     "headerName": "人分類",
        #     "field": "人分類",
        #     "suppressSizeToFit": True,
        #     "wrapText": True,
        #     "autoHeight": True,
        # },
    ],
}

AgGrid(selected_l, grid_options, use_container_width=True)


st.subheader("感謝")
st.markdown(
    "プログラムソースは、-議員見える化プロジェクト@東京都中央区 https://bit.ly/3Bqfcy0 を作られた[ほづみゆうき](https://twitter.com/ninofku)さんにご提供いただきました。GlideやStreamlitを駆使して華麗にWEBアプリで可視化する、その技術力と行動力に敬服します。ありがとうございます。"
)

st.caption("【更新履歴】20221017　ver.0.9.32　使用帯域を調整、20221016　ver.0.9.9　ベータ版リリース")
