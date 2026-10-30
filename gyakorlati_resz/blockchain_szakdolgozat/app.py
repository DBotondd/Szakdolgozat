"""Futtatás: streamlit run app.py"""
import pandas as pd
import streamlit as st
from blockchain import Blockchain, hash_text

st.set_page_config(page_title='Blockchain Lab', page_icon='🔗', layout='wide')
st.markdown('''<style>
.block-container {padding-top: 2rem; max-width: 1250px}
.blockcard {background: #172335; border: 1px solid #3b526d; border-radius: 13px; padding: 16px; margin: 8px 0; color: #f4f7fc}
.smallmono {font-family: monospace; font-size: .80rem; word-break: break-all}
</style>''', unsafe_allow_html=True)

if 'chain' not in st.session_state:
    st.session_state.chain = Blockchain(2)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_mining' not in st.session_state:
    st.session_state.last_mining = None

chain = st.session_state.chain
st.title('🔗 Blockchain Lab')
st.caption('Interaktív, oktatási célú SHA-256 és blokklánc-szimulátor – szakdolgozati demonstráció')

with st.sidebar:
    st.header('⚙️ Beállítások')
    difficulty = st.slider('Proof of Work nehézség (kezdő nullák)', 0, 5, chain.difficulty,
                           help='A magasabb érték sokkal több hash-számítást igényelhet.')
    if difficulty != chain.difficulty:
        st.info('Az új nehézség új lánc indításakor érvényesül.')
    if st.button('🔄 Új blokklánc létrehozása', use_container_width=True):
        st.session_state.chain = Blockchain(difficulty)
        st.session_state.history = []
        st.session_state.last_mining = None
        st.rerun()
    st.warning('A program nem használ hálózatot, digitális aláírásokat vagy decentralizált konszenzust. Nem alkalmas éles felhasználásra.')

valid, message, invalid_index = chain.validate()
a, b, c = st.columns(3)
a.metric('Blokkok száma', len(chain.blocks))
b.metric('PoW nehézség', chain.difficulty)
c.metric('Lánc állapota', '✅ Érvényes' if valid else '❌ Sérült')
if valid:
    st.success(message)
else:
    st.error(message)

tab1, tab2, tab3, tab4 = st.tabs(['🧱 Blokklánc', '🧪 Adatmanipuláció', '🔐 SHA-256 labor', '⛏️ PoW mérések'])

with tab1:
    left, right = st.columns([2, 1])
    with right:
        st.subheader('Új blokk készítése')
        with st.form('new_block', clear_on_submit=True):
            data = st.text_area('Blokk adatai', placeholder='Pl. Alice 5 tokent küld Bobnak (szemléltető szöveg)')
            submitted = st.form_submit_button('➕ Blokk hozzáadása', use_container_width=True)
        if submitted:
            if not data.strip():
                st.warning('Adj meg valamilyen adatot.')
            elif not valid:
                st.error('A lánc sérült. Előbb indíts új láncot.')
            else:
                block, tries, elapsed = chain.add_block(data.strip())
                st.session_state.history.append({'Blokk': block.index, 'Nehézség': chain.difficulty,
                                                  'Próbálkozások': tries, 'Másodperc': elapsed})
                st.session_state.last_mining = (tries, elapsed)
                st.rerun()
        if st.session_state.last_mining:
            tries, elapsed = st.session_state.last_mining
            st.info(f'Legutóbbi bányászat: {tries:,} próbálkozás · {elapsed:.4f} s')
    with left:
        st.subheader('Blokkok és hash-kapcsolatok')
        for i, block in enumerate(chain.blocks):
            st.markdown(f'''<div class="blockcard"><b>#{block.index} {'🌱 Genesis blokk' if i == 0 else '🧱 Blokk'}</b>
            <p>Adat: {__import__('html').escape(block.data)}</p>
            <div class="smallmono">Előző hash: {block.previous_hash}<br>Saját hash: {block.hash}</div>
            <small>Nonce: {block.nonce} · UTC időbélyeg: {block.timestamp}</small></div>''', unsafe_allow_html=True)
            if i < len(chain.blocks) - 1:
                st.markdown('<div style="text-align:center;font-size:1.6rem">⬇️ 🔗</div>', unsafe_allow_html=True)
    with st.expander('Blokklánc adatai (JSON)'):
        st.json([vars(x) for x in chain.blocks])

with tab2:
    st.subheader('Mi történik, ha egy blokk adata megváltozik?')
    st.write('A módosítás nem számolja újra automatikusan a tárolt hash-t, így az ellenőrzés felismeri az eltérést.')
    chosen = st.selectbox('Módosítandó blokk', range(len(chain.blocks)), format_func=lambda i: f'#{i} – {chain.blocks[i].data[:45]}')
    altered = st.text_input('Új adat', value=chain.blocks[chosen].data + ' [módosítva]')
    before = chain.blocks[chosen].hash
    after = chain.blocks[chosen].__class__(**{**vars(chain.blocks[chosen]), 'data': altered}).calculate_hash()
    st.code(f'Tárolt hash:      {before}\nMódosított adat hash-e: {after}', language='text')
    if st.button('⚠️ Manipuláció végrehajtása'):
        chain.tamper(chosen, altered)
        st.rerun()
    st.caption('Megjegyzés: egyszerű újrahash-eléssel a valódi hálózati konszenzus nem kerülhető meg. Ez a modell a lokális integritásellenőrzést szemlélteti.')

with tab3:
    st.subheader('A lavinahatás bemutatása')
    original = st.text_input('Első szöveg', 'Blokklánc')
    modified = st.text_input('Második szöveg', 'blokklánc')
    h1, h2 = hash_text(original), hash_text(modified)
    st.code(f'A: {h1}\nB: {h2}', language='text')
    changed_bits = sum((int(h1[i:i+2], 16) ^ int(h2[i:i+2], 16)).bit_count() for i in range(0, 64, 2))
    st.metric('Eltérő bitek száma a 256-ból', changed_bits)
    st.progress(changed_bits / 256)
    st.caption('Egyetlen karakter megváltoztatása is jelentős, előre nem jósolható hash-változással járhat.')

with tab4:
    st.subheader('Proof of Work: próbálkozások és futásidő')
    st.write('A bányász algoritmus addig növeli a nonce értékét, amíg a hash a megadott számú nullával nem kezdődik.')
    st.caption('A mérések az aktuális lánc blokkjaira vonatkoznak; a futási idő számítógépenként eltérhet. A nehézséget az oldalsávban, új lánc indításával változtathatod.')
    if st.session_state.history:
        frame = pd.DataFrame(st.session_state.history)
        st.dataframe(frame, hide_index=True, use_container_width=True)
        st.markdown('**Próbálkozások blokkonként**')
        st.bar_chart(frame.set_index('Blokk')['Próbálkozások'])
        st.markdown('**Futásidő blokkonként (másodperc)**')
        st.bar_chart(frame.set_index('Blokk')['Másodperc'])
        st.download_button('⬇️ Mérések letöltése CSV-ként', frame.to_csv(index=False).encode('utf-8-sig'),
                           file_name='pow_meresek.csv', mime='text/csv')
    else:
        st.info('Hozz létre néhány blokkot a Blokklánc fülön a mérésekhez.')
