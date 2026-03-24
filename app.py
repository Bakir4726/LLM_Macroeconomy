from __future__ import annotations

import html
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from euromacro_copilot import EuroMacroCopilot


st.set_page_config(page_title="EuroMacro Copilot", page_icon="€", layout="wide", initial_sidebar_state="expanded")

INDICATOR_LABELS = {
    "hicp": "Inflation IPCH",
    "core_inflation": "Inflation sous-jacente",
    "borrowing_cost": "Coût du financement",
    "unemployment_rate": "Taux de chômage",
    "gdp_growth": "Croissance du PIB",
    "wage_growth": "Progression des salaires",
}
TREND_LABELS = {"up": "en hausse", "down": "en baisse", "flat": "stable"}
EXAMPLE_QUESTIONS = [
    "Que signifie le durcissement du crédit pour mes coûts de financement ?",
    "Le risque inflationniste vient-il surtout des salaires ou de la demande ?",
    "Dois-je ralentir mes embauches sur les deux prochains trimestres ?",
]


@st.cache_resource(show_spinner=False)
def load_copilot() -> EuroMacroCopilot:
    return EuroMacroCopilot.from_project_root(PROJECT_ROOT)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#17231f; --muted:#5f6a65; --line:rgba(23,35,31,.1); --accent:#295847; --gold:#b28a47; }
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 10% 8%, rgba(178,138,71,.16), transparent 22%),
                radial-gradient(circle at 92% 4%, rgba(41,88,71,.14), transparent 22%),
                linear-gradient(180deg, #f8f3ea 0%, #f4ede0 48%, #efe6d7 100%);
        }
        .main .block-container { max-width:1280px; padding-top:2rem; padding-bottom:3rem; }
        h1,h2,h3,h4,p,li,div,span,label,small { color:var(--ink) !important; }
        h1,h2,h3,h4 { font-family:Georgia,"Times New Roman",serif; letter-spacing:-.02em; }
        p,li,div,span,label,small { font-family:"Aptos","Segoe UI","Trebuchet MS",sans-serif; }
        section[data-testid="stSidebar"] > div { background:linear-gradient(180deg, rgba(247,241,231,.96), rgba(240,230,214,.96)); }
        .hero,.panel,.metric,.source,.sidebar-card,.spotlight {
            border:1px solid var(--line); border-radius:24px; box-shadow:0 18px 46px rgba(34,45,40,.08);
        }
        .hero { padding:2rem 2.2rem; margin-bottom:1rem; background:linear-gradient(135deg, rgba(255,251,245,.98), rgba(245,236,221,.98)); }
        .hero-grid { display:grid; grid-template-columns:minmax(0,2.2fr) minmax(250px,1fr); gap:1.2rem; align-items:start; }
        .kicker,.label { color:var(--gold) !important; text-transform:uppercase; letter-spacing:.16em; font-size:.76rem; }
        .hero-title { margin:0; font-size:2.8rem; line-height:1; }
        .copy { color:var(--muted) !important; line-height:1.7; }
        .tags { display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1rem; }
        .tag { padding:.44rem .8rem; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.75); font-size:.88rem; }
        .spotlight { padding:1rem 1.1rem; background:linear-gradient(180deg, rgba(43,73,61,.96), rgba(28,51,43,.96)); }
        .spotlight * { color:#f7f1e8 !important; }
        .spotlight-value { margin:.3rem 0; font-size:2rem; font-weight:700; line-height:1; }
        .section { margin:1rem 0 .75rem; }
        .section-title { margin:0; font-size:1.5rem; }
        .metric { min-height:176px; padding:1.1rem 1.2rem; background:linear-gradient(180deg, rgba(255,252,247,.98), rgba(247,241,231,.96)); }
        .metric-label { color:var(--muted) !important; font-size:.84rem; text-transform:uppercase; letter-spacing:.1em; }
        .metric-value { margin-top:.45rem; font-size:2rem; font-weight:700; line-height:1.04; }
        .metric-delta { margin-top:.6rem; display:inline-flex; padding:.28rem .55rem; border-radius:999px; font-size:.84rem; font-weight:700; background:rgba(23,35,31,.06); }
        .metric-meta { margin-top:.7rem; color:var(--muted) !important; font-size:.84rem; }
        .panel,.sidebar-card,.source { padding:1rem 1.1rem; background:rgba(255,251,245,.94); margin-bottom:1rem; }
        .panel-copy,.meta,.chat-intro { color:var(--muted) !important; line-height:1.6; }
        .highlights { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; margin-top:.9rem; }
        .highlight { padding:.85rem .95rem; border:1px solid rgba(23,35,31,.08); border-radius:18px; background:linear-gradient(180deg, rgba(244,238,227,.88), rgba(255,255,255,.72)); }
        .highlight-label { color:var(--muted) !important; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; }
        .highlight-value { margin-top:.25rem; font-size:1.26rem; font-weight:700; }
        .highlight-meta { margin-top:.25rem; color:var(--muted) !important; font-size:.84rem; }
        .source-title { margin:0 0 .22rem; font-size:1rem; font-weight:700; }
        .library-item { padding:.8rem 0; border-bottom:1px solid rgba(23,35,31,.08); }
        .library-item:last-child { border-bottom:none; padding-bottom:0; }
        .stTabs [data-baseweb="tab"] { border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.72); padding:.4rem .9rem; }
        .stTabs [aria-selected="true"] { background:rgba(41,88,71,.12); color:var(--accent) !important; border-color:rgba(41,88,71,.24); }
        .stButton > button,.stChatInput button { border-radius:999px; border:1px solid var(--line); background:linear-gradient(180deg, rgba(255,252,247,.98), rgba(244,238,227,.96)); }
        div[data-testid="stChatMessage"] { background:rgba(255,252,247,.92); border:1px solid rgba(23,35,31,.09); border-radius:22px; padding:.35rem .35rem .7rem; box-shadow:0 10px 28px rgba(32,41,37,.05); }
        div[data-testid="stChatMessage"] h3 { margin-top:1rem; margin-bottom:.4rem; padding-top:.7rem; border-top:1px solid rgba(23,35,31,.08); font-size:1rem; }
        div[data-testid="stChatMessage"] h3:first-of-type { margin-top:.2rem; padding-top:0; border-top:none; }
        div[data-testid="stExpander"] { border-radius:18px; border:1px solid rgba(23,35,31,.08); background:rgba(247,243,236,.88); }
        @media (max-width: 980px) { .hero-grid,.highlights { grid-template-columns:1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fr_number(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def format_date_fr(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def indicator_label(indicator: str, fallback: str) -> str:
    return INDICATOR_LABELS.get(indicator, fallback)


def metric_value(snapshot: dict, indicator: str) -> tuple[str, str, str]:
    item = snapshot.get(indicator)
    if not item:
        return "n/a", "Aucune donnée", ""
    value = f"{fr_number(item.latest_value)} %"
    delta = "Pas d'historique pour calculer la variation"
    if item.delta is not None:
        delta = f"{TREND_LABELS.get(item.trend, 'stable')} de {fr_number(abs(item.delta))} pt"
    return value, delta, f"Dernière observation : {format_date_fr(item.latest_date)}"


def render_section_header(label: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section">
            <div class="label">{html.escape(label)}</div>
            <h2 class="section-title">{html.escape(title)}</h2>
            <div class="copy">{html.escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(column, snapshot: dict, indicator: str) -> None:
    item = snapshot.get(indicator)
    label = indicator_label(indicator, item.label if item else indicator)
    value, delta, meta = metric_value(snapshot, indicator)
    column.markdown(
        f"""
        <div class="metric">
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-value">{html.escape(value)}</div>
            <div class="metric-delta">{html.escape(delta)}</div>
            <div class="metric-meta">{html.escape(meta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_spotlight(snapshot: dict) -> None:
    hicp = snapshot.get("hicp")
    borrowing = snapshot.get("borrowing_cost")
    unemployment = snapshot.get("unemployment_rate")
    hicp_value = f"{fr_number(hicp.latest_value)} %" if hicp else "n/a"
    borrowing_value = f"{fr_number(borrowing.latest_value)} %" if borrowing else "n/a"
    unemployment_value = f"{fr_number(unemployment.latest_value)} %" if unemployment else "n/a"
    hicp_meta = format_date_fr(hicp.latest_date) if hicp else "Pas de données"
    borrowing_meta = format_date_fr(borrowing.latest_date) if borrowing else "Pas de données"
    unemployment_meta = format_date_fr(unemployment.latest_date) if unemployment else "Pas de données"
    st.markdown(
        f"""
        <div class="panel">
            <h3>Tableau de bord express</h3>
            <div class="panel-copy">Trois signaux pour cadrer rapidement le régime macro avant de lancer une question.</div>
            <div class="highlights">
                <div class="highlight">
                    <div class="highlight-label">Signal prix</div>
                    <div class="highlight-value">{html.escape(hicp_value)}</div>
                    <div class="highlight-meta">Inflation IPCH au {html.escape(hicp_meta)}</div>
                </div>
                <div class="highlight">
                    <div class="highlight-label">Signal crédit</div>
                    <div class="highlight-value">{html.escape(borrowing_value)}</div>
                    <div class="highlight-meta">Coût du financement au {html.escape(borrowing_meta)}</div>
                </div>
                <div class="highlight">
                    <div class="highlight-label">Signal emploi</div>
                    <div class="highlight-value">{html.escape(unemployment_value)}</div>
                    <div class="highlight-meta">Taux de chômage au {html.escape(unemployment_meta)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_indicator_focus(snapshot: dict, selected_indicator: str) -> None:
    item = snapshot.get(selected_indicator)
    if not item:
        return
    delta_text = "Pas d'historique"
    if item.delta is not None:
        delta_text = f"{TREND_LABELS.get(item.trend, 'stable')} de {fr_number(abs(item.delta))} pt"
    st.markdown(
        f"""
        <div class="panel">
            <h3>{html.escape(indicator_label(selected_indicator, item.label))}</h3>
            <div class="panel-copy">
                Dernière lecture à {fr_number(item.latest_value)} % le {html.escape(format_date_fr(item.latest_date))}.
                Source locale : {html.escape(item.source)}.
            </div>
            <div class="meta" style="margin-top:.55rem;">Variation récente : {html.escape(delta_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(chunks) -> None:
    if not chunks:
        st.info("Aucune source documentaire n'a été mobilisée.")
        return
    for index, chunk in enumerate(chunks, start=1):
        source_name = Path(chunk.source).name if chunk.source else chunk.source_type
        excerpt = chunk.text[:420].strip()
        if len(chunk.text) > 420:
            excerpt += "..."
        meta_bits = [f"Score : {fr_number(chunk.score, 2)}", f"Type : {chunk.source_type}", f"Source : {source_name}"]
        if chunk.url:
            meta_bits.append(f'<a href="{html.escape(chunk.url, quote=True)}" target="_blank">Lien</a>')
        st.markdown(
            f"""
            <div class="source">
                <div class="source-title">[S{index}] {html.escape(chunk.title)}</div>
                <div class="meta">{' | '.join(meta_bits)}</div>
                <p>{html.escape(excerpt)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_documents(documents) -> None:
    if not documents:
        st.info("Aucun document complémentaire n'est disponible.")
        return
    for index, document in enumerate(documents, start=1):
        source_name = Path(document.source).name if document.source else document.source_type
        excerpt = (document.excerpt or "").strip()
        if len(excerpt) > 320:
            excerpt = excerpt[:320].rstrip() + "..."
        meta_bits = [f"Type : {document.source_type}", f"Source : {source_name}", f"Score : {fr_number(document.score, 2)}"]
        if document.url:
            meta_bits.append(f'<a href="{html.escape(document.url, quote=True)}" target="_blank">Ouvrir</a>')
        st.markdown(
            f"""
            <div class="source">
                <div class="source-title">[D{index}] {html.escape(document.title)}</div>
                <div class="meta">{' | '.join(meta_bits)}</div>
                <p>{html.escape(excerpt or 'Document indexé dans le corpus local.')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hero(state: dict[str, object], llm_enabled: bool, llm_provider: str) -> None:
    uncertainty = state["uncertainty_score"]
    regime = "Régime plutôt calme"
    if uncertainty >= 45:
        regime = "Régime de vigilance élevée"
    elif uncertainty >= 25:
        regime = "Régime de vigilance moyenne"
    st.markdown(
        f"""
        <section class="hero">
            <div class="kicker">Assistant macroéconomique pour la zone euro</div>
            <div class="hero-grid">
                <div>
                    <h1 class="hero-title">EuroMacro Copilot</h1>
                    <p class="copy">
                        Lisez rapidement les signaux d'inflation, de crédit, d'emploi et de demande,
                        puis passez à une question documentée avec sources et documents complémentaires.
                    </p>
                    <div class="tags">
                        <span class="tag">Corpus : {state["documents_indexed"]} segments</span>
                        <span class="tag">Documents : {state["documents_available"]}</span>
                        <span class="tag">Incertitude : {uncertainty}/100</span>
                        <span class="tag">LLM : {html.escape(llm_provider if llm_enabled else "mode heuristique")}</span>
                    </div>
                </div>
                <div class="spotlight">
            <div class="kicker" style="color:#f7f1e8 !important;">Lecture immédiate</div>
                    <div class="spotlight-value">{uncertainty}/100</div>
                    <div>{html.escape(regime)}</div>
                    <div class="meta" style="margin-top:.6rem;color:#f7f1e8 !important;">
                        Réponses structurées avec sources mobilisées et documents associés.
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(state: dict[str, object], llm_enabled: bool, llm_provider: str) -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-card">
                <h3>État du projet</h3>
                <p><strong>{state["documents_indexed"]}</strong> segments indexés</p>
                <p><strong>{state["documents_available"]}</strong> documents disponibles</p>
                <p><strong>{state["uncertainty_score"]}/100</strong> score d'incertitude</p>
                <p><strong>{html.escape(llm_provider if llm_enabled else "Heuristique")}</strong> moteur de réponse</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="sidebar-card">
                <h3>Alimenter le corpus</h3>
                <p>Déposez vos notes, exports HTML, fichiers texte et documents pré-traités dans
                <code>data/documents/</code> et <code>data/external/</code>.</p>
                <div class="meta">Les fichiers avec <code>title:</code> et <code>url:</code> exposent un lien source dans l'interface.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="sidebar-card">
                <h3>Sources recommandées</h3>
                <p><a href="https://www.ecb.europa.eu/press/key/html/downloads.en.html" target="_blank">ECB speeches dataset</a></p>
                <p><a href="https://www.ecb.europa.eu/press/accounts/html/index.en.html" target="_blank">ECB policy accounts</a></p>
                <p><a href="https://www.ecb.europa.eu/stats/ecb_surveys/bank_lending_survey/html/index.en.html" target="_blank">ECB Bank Lending Survey</a></p>
                <p><a href="https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction" target="_blank">Eurostat API</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_narratives(narratives) -> None:
    if narratives:
        body = "".join(f"<span class='tag'>{html.escape(item.name)} | {fr_number(item.score)}%</span>" for item in narratives)
        content = f"<div class='tags'>{body}</div>"
    else:
        content = "<p>Aucun narratif dominant détecté dans le corpus actuel.</p>"
    st.markdown(
        f"""
        <div class="panel">
            <h3>Narratifs détectés</h3>
            <div class="panel-copy">Les thèmes dominants du corpus servent à cadrer la lecture macro avant génération.</div>
            <div style="margin-top:.85rem;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_examples_panel() -> None:
    questions = "".join(f"<li>{html.escape(question)}</li>" for question in EXAMPLE_QUESTIONS)
    st.markdown(
        f"""
        <div class="panel">
            <h3>Questions utiles</h3>
            <div class="panel-copy">Quelques angles d'attaque pour interroger la politique monétaire et ses effets PME.</div>
            <ul style="margin-top:.8rem;padding-left:1.1rem;">{questions}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_to() -> None:
    st.markdown(
        """
        <div class="panel">
            <h3>Mode d'emploi rapide</h3>
            <ul style="margin-top:.8rem;padding-left:1.1rem;">
                <li>Lisez d'abord les cartes indicateurs pour fixer le régime macro.</li>
                <li>Utilisez le panneau central pour voir la trajectoire d'un indicateur clé.</li>
                <li>Passez ensuite au chat pour obtenir un diagnostic, des implications PME et des sources tracées.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_library(documents) -> None:
    items = []
    for document in documents:
        meta_bits = [html.escape(document.source_type)]
        if getattr(document, "url", None):
            meta_bits.append(f'<a href="{html.escape(document.url, quote=True)}" target="_blank">source</a>')
        items.append(
            f"""
            <div class="library-item">
                <div><strong>{html.escape(document.title)}</strong></div>
                <div class="meta">{' | '.join(meta_bits)}</div>
            </div>
            """
        )
    body = "".join(items) if items else "<p>Aucun document indexé.</p>"
    st.markdown(
        f"""
        <div class="panel">
            <h3>Bibliothèque documentaire</h3>
            <div class="panel-copy">Documents de référence actuellement injectés dans le corpus.</div>
            <div style="margin-top:.7rem;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ensure_messages() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Posez une question sur l'inflation, la croissance, le financement ou le recrutement.\n\n"
                    "Je réponds avec un diagnostic macro, des implications PME, des sources et des documents complémentaires."
                ),
            }
        ]


def submit_question(copilot: EuroMacroCopilot, question: str) -> None:
    question = question.strip()
    if not question:
        return
    st.session_state.messages.append({"role": "user", "content": question})
    conversation = [{"role": message["role"], "content": str(message.get("content", ""))} for message in st.session_state.messages]
    response = copilot.answer(question, conversation=conversation)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.answer,
            "sources": response.evidence,
            "documents": response.documents,
        }
    )
    st.rerun()


apply_theme()
copilot = load_copilot()
state = copilot.dashboard_state()
snapshot = state["snapshot"]
llm_provider = str(state.get("llm_provider") or copilot.llm_client.provider_name)
ensure_messages()

render_sidebar(state, llm_enabled=copilot.llm_client.is_configured, llm_provider=llm_provider)
render_hero(state, llm_enabled=copilot.llm_client.is_configured, llm_provider=llm_provider)
render_spotlight(snapshot)

metric_columns = st.columns(4)
for column, indicator in zip(metric_columns, ["hicp", "core_inflation", "borrowing_cost", "unemployment_rate"]):
    render_metric_card(column, snapshot, indicator)

chart_col, insight_col = st.columns([1.55, 1.0], gap="large")

with chart_col:
    render_section_header(
        label="Lecture des séries",
        title="Pilotage des indicateurs",
        copy="Passez d'un indicateur à l'autre pour lire la trajectoire, la dernière valeur et la variation récente.",
    )
    selected_indicator = st.selectbox(
        "Choisir un indicateur",
        copilot.macro_store.available_indicators(),
        format_func=lambda indicator: indicator_label(indicator, indicator),
    )
    render_indicator_focus(snapshot, selected_indicator)
    chart_df = pd.DataFrame(copilot.macro_store.chart_rows(selected_indicator))
    if not chart_df.empty:
        chart_df["date"] = pd.to_datetime(chart_df["date"])
        tabs = st.tabs(["Courbe", "Tableau"])
        with tabs[0]:
            st.line_chart(chart_df.set_index("date")["value"], use_container_width=True, height=370)
            st.caption(f"Lecture : {indicator_label(selected_indicator, selected_indicator)} sur données locales de démonstration.")
        with tabs[1]:
            table_df = chart_df.rename(columns={"date": "Date", "value": "Valeur", "label": "Libelle"})
            table_df["Date"] = table_df["Date"].dt.strftime("%d/%m/%Y")
            table_df["Valeur"] = table_df["Valeur"].map(lambda value: fr_number(value))
            st.dataframe(table_df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée de série n'est disponible pour cet indicateur.")

with insight_col:
    render_section_header(
        label="Repère documentaire",
        title="Lecture contextuelle",
        copy="Consultez les narratifs, la bibliothèque et les questions utiles sans quitter le tableau de bord.",
    )
    insight_tabs = st.tabs(["Narratifs", "Bibliothèque", "Guide"])
    with insight_tabs[0]:
        render_narratives(state["narratives"])
        render_examples_panel()
    with insight_tabs[1]:
        render_document_library(copilot.document_library(limit=8))
    with insight_tabs[2]:
        render_how_to()
        for index, example in enumerate(EXAMPLE_QUESTIONS):
            if st.button(example, key=f"example_{index}", use_container_width=True):
                submit_question(copilot, example)

render_section_header(
    label="Dialogue analytique",
    title="Conversation",
    copy="Interrogez directement le corpus pour obtenir une réponse structurée avec sources mobilisées et documents associés.",
)
st.markdown(
    '<div class="chat-intro">Exemple : "Que signifie le reflux de l\\\'inflation pour ma politique tarifaire ?"</div>',
    unsafe_allow_html=True,
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("Sources utilisées", expanded=False):
                render_sources(message["sources"])
        if "documents" in message:
            with st.expander("Documents complémentaires", expanded=False):
                render_documents(message["documents"])

question = st.chat_input("Ex. : Que signifie le reflux de l'inflation pour ma politique tarifaire ?")
if question:
    submit_question(copilot, question)
