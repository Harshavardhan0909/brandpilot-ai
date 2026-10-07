import streamlit as st
import requests

st.set_page_config(page_title="BrandPilot AI", page_icon="🎨", layout="wide")
st.title("🎨 BrandPilot AI")
st.caption("Agentic branded-content workflow — learning MVP")

api_url = st.sidebar.text_input("API URL", "http://127.0.0.1:8000")

with st.form("brand_form"):
    st.subheader("1. Create a brand")
    name = st.text_input("Brand name", "Aura Coffee")
    description = st.text_area("Description", "Premium coffee for modern daily rituals")
    industry = st.text_input("Industry", "Food and beverage")
    audience = st.text_input("Target audience", "Young professionals")
    tones = st.text_input("Tone of voice", "friendly, modern, confident")
    colors = st.text_input("Primary colors", "#3B2418, #F5E8D0, #E97932")
    forbidden = st.text_input("Forbidden words", "the best coffee in the world, cure")
    submitted = st.form_submit_button("Create brand")

if submitted:
    response = requests.post(f"{api_url}/brands", json={
        "name": name,
        "description": description,
        "industry": industry,
        "target_audience": audience,
        "tone_of_voice": [x.strip() for x in tones.split(",") if x.strip()],
        "primary_colors": [x.strip() for x in colors.split(",") if x.strip()],
        "forbidden_words": [x.strip() for x in forbidden.split(",") if x.strip()],
        "preferred_words": [],
    }, timeout=30)
    if response.ok:
        st.session_state.brand = response.json()
        st.success(f"Created brand: {st.session_state.brand['id']}")
    else:
        st.error(response.text)

brand = st.session_state.get("brand")
if brand:
    st.divider()
    st.subheader("2. Add guidelines")
    guidelines = st.text_area("Guideline text", "Use dark brown, cream and orange. Be friendly and modern. Do not make fake health claims.")
    if st.button("Save guidelines"):
        response = requests.post(f"{api_url}/brands/{brand['id']}/guidelines", params={"content": guidelines}, timeout=30)
        st.success(response.json() if response.ok else response.text)

    st.subheader("3. Generate campaign")
    with st.form("campaign_form"):
        objective = st.text_input("Objective", "Launch our new cold brew")
        product = st.text_input("Product", "Cold Brew")
        campaign_audience = st.text_input("Campaign audience", audience)
        platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Facebook"])
        run = st.form_submit_button("Generate campaign")
    if run:
        created = requests.post(f"{api_url}/campaigns", json={"brand_id": brand["id"], "objective": objective, "product": product, "audience": campaign_audience, "platform": platform}, timeout=30)
        if created.ok:
            campaign = created.json()
            result = requests.post(f"{api_url}/campaigns/{campaign['id']}/run", timeout=60)
            if result.ok:
                data = result.json()
                st.success(f"Campaign status: {data['status']}")
                st.json(data)
            else:
                st.error(result.text)
        else:
            st.error(created.text)
