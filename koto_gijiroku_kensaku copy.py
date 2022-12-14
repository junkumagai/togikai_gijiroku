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

st.set_page_config(layout="wide")
st.title(":thinking_face: 議会の議事録検索(β)@中央区")
st.subheader("「あの話題、どの議員さんが熱心に活動してるのかな？？」と思ったときに。")
st.markdown(
    "　区議会のwebサイトでもキーワードでの検索は可能なんですが会議体ごとで表示されて見にくいので、関連する部分だけを抜き出して表示するサービスを作ってみました。"
)
st.markdown("　対象はわたしの住んでる東京都中央区議会、期間は2022年3月時点で入手できた2015年5月から2021年10月まで。")
st.markdown(
    "　python + streamlitで作ってます。超初心者の習作なもので色々ツッコミどころはあるかと思います。こうすればもっと良いよ！とか教えてもらえると嬉しいです。一緒にやろうよ！という人がいてくれるともっと嬉しいです。コメント、ツッコミはお気軽に。"
)
image = Image.open("jigazo.png")

st.image(image, width=100)
st.markdown("**作った人：[ほづみゆうき](https://twitter.com/ninofku)**")

logs = pd.read_csv(
    "./gijiroku2015-2021_2.csv", encoding="UTF-8"
)  # dataframeとしてcsvを読み込み

st.header(":fork_and_knife: 検索条件")
logs2 = logs[["年月日", "人分類", "内容分類", "質問", "回答", "会議", "内容", "年度", "文字数"]]

option_selected_l = st.text_input("キーワード入力してね。初期値は「待機児童」になってます。", "待機児童")

# st.markdown(' ##### :date:「年度」での絞り込み')
with st.expander("■「年度」での絞り込み", False):
    # 年度選択
    start_year, end_year = st.select_slider(
        "最近の動向を知りたいとか過去はどうなってたかとか、年度で結果を絞りたい場合は使ってみてください。初期値では2019年から2021年が選択されてます。",
        options=["2015", "2016", "2017", "2018", "2019", "2020", "2021"],
        value=("2019", "2021"),
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

st.header(":cake: 結果表示")
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
            "maxWidth": 150,
        },
        {
            "headerName": "内容分類",
            "field": "内容分類",
            "suppressSizeToFit": True,
            "autoHeight": True,
        },
        {
            "headerName": "質問者",
            "field": "質問",
            "suppressSizeToFit": True,
            "wrapText": True,
            "maxWidth": 100,
            "autoHeight": True,
        },
        {
            "headerName": "回答者",
            "field": "回答",
            "suppressSizeToFit": True,
            "wrapText": True,
            "maxWidth": 100,
            "autoHeight": True,
        },
        {
            "headerName": "発言内容",
            "field": "内容",
            "wrapText": True,
            "autoHeight": True,
            "suppressSizeToFit": True,
            "maxWidth": 500,
        },
        {
            "headerName": "人分類",
            "field": "人分類",
            "suppressSizeToFit": True,
            "wrapText": True,
            "autoHeight": True,
        },
    ],
}

AgGrid(selected_l, grid_options)

selected_l_moji = selected_l[["年月日", "人分類", "内容分類", "質問", "回答", "内容", "文字数"]]

st.subheader(":coffee: 発言文字数ランキング")
st.markdown(
    "キーワードが含まれる発言内容の文字列をカウントして、ランキング化したものです。ざっくりどの議員がそのテーマに熱心なのかを測るのに使えるかも。"
)
st.markdown(
    "カテゴリとしては以下の3つに分かれています「質問」「回答」キーワードが含まれる発言内容の文字列をカウントして、ランキング化したものです。"
)
st.markdown("・「質問」：議員による質問内容")
st.markdown("・「回答」：議員の質問に対する区長などの回答")
st.markdown("・「議長/委員長」：会議での議長や委員長としての発言")
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
    height=800,
    width=1000,
    orientation="h",
)
# fig.update_layout(barmode='stack', xaxis={'文字数':'category ascending'})
fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
fig

st.subheader(":doughnut: テキスト解析結果")
st.markdown(
    "キーワードが含まれる発言内容のテキストを解析して、ざっくり1枚の画像にしてます。そのキーワードでどういう議論をされているのかを掴むのに役立つかも。"
)
# ワードクラウド作成
logs_contents = selected_l["内容"]
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
dt_now = datetime.now(JST)

st.write(
    "**[検索キーワード]**",
    option_selected_l,
    "**[対象年度]**",
    start_year,
    "-",
    end_year,
    "**[作成日時]**",
    dt_now,
)

stpwds = [
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
    "中央",
    "点",
    "区",
    "委員会",
    "賛成者",
    "今",
    "中央区",
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
]

wc = WordCloud(
    stopwords=stpwds,
    width=1080,
    height=1080,
    background_color="white",
    font_path=font_path,
)
wc.generate(words)
wc.to_file("wc.png")
st.image("wc.png")
st.markdown(
    "補足：更新するたびに表示位置などはビミョーに変わります。対象は名詞だけで、「それぞれ」や「問題」など、頻繁に使われるけど中身のないキーワードは除外してます。"
)


# dftest = pd.DataFrame(selected_l) # これでpdでの表示は可能
# st.dataframe(dftest)# 動くはずだが動かない

# st.write(
#    px.bar(selected_l, x='年度', y='文字数' ,title="発言数の推移",color='人分類'))

# selected_l
# selected_l.dtype

# selected_l_alt = alt.Chart(selected_l).mark_bar().encode(
#    x='sum(文字数):Q',
#    y=alt.Y('人分類:N', sort='文字数')
# )
# st.altair_chart(selected_l_alt, use_container_width=True)

# print(results2)

# selected_g = logs_moji[(logs_moji['人分類'].str.contains(option_select_g))]

# st.write(
#    px.line(selected_g, x='年度', y='文字数' ,title="sample figure",color='人分類')
# )

st.header(":paperclip: 情報参照元")
st.markdown(
    "分析の元になっているデータは、[中央区議会 Webサイト](https://www.kugikai.city.chuo.lg.jp/index.html)の「会議録検索」からHTMLファイルをごっそりダウンロードして、その上であれこれ苦心して加工して作成しました。注意して作業はしたつもりですが、一部のデータが欠損等している可能性もありますのでご承知おきください。もし不備等ありましたら[ほづみゆうき](https://twitter.com/ninofku)まで声掛けいただけるとありがたいです。"
)
