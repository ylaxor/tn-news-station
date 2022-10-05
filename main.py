import streamlit as st
from scrapping import *
from utils import *
import jaro

local_css("style.css")

if 'articles' not in st.session_state:
    st.session_state['articles'] = []

if 'meaning_sim' not in st.session_state:
    with st.spinner('Setting up application environment. This might take few seconds...'):
        st.session_state['meaning_sim'] = MeaningSim()
    st.success('Everything was successfully set up. Application ready to use! Start by fetching some articles.')
    st.snow()

with st.sidebar:
    st.markdown("# TN 🇹🇳 News Point")
    st.write("Quick access to news articles fetched from various tunisian newspapers.")
    st.markdown("### Articles")
    
    with st.expander("🛎 Select newspapers"):
        sources = st.multiselect('What are your favorite news channels?', ['ShemsFM', 'MosaiqueFM', 'Jomhouria', 'Assarih'], ['ShemsFM', 'MosaiqueFM', 'Jomhouria', 'Assarih'], disabled=True)
        
    with st.expander("📥 Fetch articles"):
        nb_pages = st.slider("Pages to inspect in each newspaper", 1, 25)
        grab = st.button("Fetch articles")

    with st.expander("🗓 Filter articles by date"):
        start_date = st.date_input(label="Filter articles newer than")
        filter_date = st.button("Filter articles", disabled=True)

    st.markdown("### Search")
    lookup_words = st.text_input("keyword.s, or query string ..", "وباء كورونا, تونس")

    with st.expander("🔎 Search by exact keyword.s"):
        regex_find = st.button("Find matching articles", key="exact")
    with st.expander("🔎 Search by similar keyword.s"):
        temperature = st.slider("Similarity threshold", 0.0, 1.0)
        jaro_find = st.button("Find matching articles", key="jaro")
    with st.expander("🔎 Search by query meaning"):
        ai_find = st.button("Find matching articles", disabled=False, key="ai")
    
if regex_find:
    if st.session_state['articles'] == []:
        st.write("Please fetch some articles before.")
    else:
        
        lookup_words = lookup_words.replace(",","").split(" ")
        if "" in lookup_words: lookup_words.remove("") 
        st.markdown("#### Search results for keyword.s: {}".format(", ".join(lookup_words)))
        result  = filter(lambda article: len(set(lookup_words).intersection(set(article[0].split(" ")))) > 0, st.session_state['articles'])
        result = list(result)
        st.markdown("**{}** *articles contain keyword.s in their* **title**".format(len(result)))
        if len(result):
            with st.expander("Result.s"):
                for i, article in enumerate(result):
                    title = article[0]
                    link = article[1]
                    st.markdown("["+title+"]("+link+") 📰 ")

if jaro_find:
    if st.session_state['articles'] == []:
        st.write("Please fetch some articles before.")
    else:
        
        lookup_words = lookup_words.replace(",","").split(" ")
        if "" in lookup_words: lookup_words.remove("") 
        st.markdown("#### Search results for keyword.s: {}".format(", ".join(lookup_words)))
        result  = list(map(lambda article: article[0].split(" "), st.session_state['articles']))
        result  = list(map(lambda article: [jaro.jaro_winkler_metric(x, y) for x in lookup_words for y in article], result))
        result  = list(map(lambda article: max(article) >= temperature, result))
        result = [i for i in range(len(result)) if result[i]]
        result = [st.session_state['articles'][i] for i in result]
        st.markdown("**{}** *articles contain words similiar to keyword.s in their* **title**".format(len(result)))
        if len(result):
            with st.expander("Result.s"):
                for i, article in enumerate(result):
                    title = article[0]
                    link = article[1]
                    st.markdown("["+title+"]("+link+") 📰 ")
      
if ai_find:
    if st.session_state['articles'] == []:
        st.write("Please fetch some articles before.")
    else:
        prob_threshold = .45
        query = lookup_words.replace(",","")
        st.markdown("#### Search results for query: {}".format(query))
        with st.spinner('ِQuerying for articles that have title meaning similar to query: {}. This might take few minutes'.format(query)):
            result  = list(map(lambda article: st.session_state['meaning_sim'].predict(article[0], [query, 'غير معروف'])['labels'][0], st.session_state['articles']))
        result = [i for i in range(len(result)) if result[i]!='Unknown']
        result = [st.session_state['articles'][i] for i in result]
        st.markdown("**{}** *articles contain meaning similiar to query in their* **title**".format(len(result)))
        if len(result):
            with st.expander("Result.s"):
                for i, article in enumerate(result):
                    title = article[0]
                    link = article[1]
                    st.markdown("["+title+"]("+link+") 📰 ")

if grab:
    articles = fetch_pages(nb_pages=nb_pages)
    st.session_state['articles'] = articles['Shems FM']+articles['Mosaique FM']+articles['Jomhouria']+articles['Assarih']
    st.markdown("📮 **{}** *articles loaded from the first* **{}** *page.s of each selected source*".format(len(st.session_state['articles']), nb_pages))
    st.balloons()
    with st.expander("ShemsFM: {} articles ..".format(len(articles["Shems FM"]))):
        for i, article in enumerate(articles["Shems FM"]):
            title = article[0]
            link = article[1]
            st.markdown("["+title+"]("+link+") 📰 ")
    with st.expander("MosaiqueFM: {} articles ..".format(len(articles["Mosaique FM"]))):
        for i, article in enumerate(articles["Mosaique FM"]):
            title = article[0]
            link = article[1]
            st.markdown("["+title+"]("+link+") 📰 ")
    with st.expander("Jomhouria: {} articles ..".format(len(articles["Jomhouria"]))):
        for i, article in enumerate(articles["Jomhouria"]):
            title = article[0]
            link = article[1]
            st.markdown("["+title+"]("+link+") 📰 ")
    with st.expander("Assarih: {} articles ..".format(len(articles["Assarih"]))):
        for i, article in enumerate(articles["Assarih"]):
            title = article[0]
            link = article[1]
            st.markdown("["+title+"]("+link+") 📰 ")
