import streamlit as st
import pandas as pd
import json
from helper import technique_information
# Mock function to simulate returned data from backend
def get_technique_data(technique_id, accuracy_threshold):
    data=technique_information(technique_id,accuracy_threshold)
    return data

# --- UI Layout ---

st.set_page_config(layout="wide")
st.title("🔍 MITRE ATT&CK Technique Insights")

# --- User Input ---
technique_id = st.text_input("🔑 Enter Technique ID (e.g., T1098):")
accuracy_threshold = st.slider("🎯 Accuracy Threshold (%)", 0, 100, 75)

if technique_id:
    st.success(f"Fetching data for Technique ID: `{technique_id}` with accuracy ≥ {accuracy_threshold}%...")
    output = get_technique_data(technique_id, accuracy_threshold)
    if "error" not in output:
        st.subheader("🧬 Technique Overview")
        st.metric("Technique ID", output.get("input_technique_id"))
        st.metric("Technique Name", output.get("input_technique_name"))
        st.metric("Stage", output.get("current_stage"))

        st.markdown("---")
        st.subheader("👥 Associated Groups")
        for group_id, group_name in output['groups_code'].items():
            group_info = next((g[group_name] for g in output["groups_info"] if group_name in g), None)
            if group_info:
                with st.expander(f"{group_name} ({group_id})"):
                    st.markdown(f"**🎯 Targets:** {', '.join(group_info['primary_targets'])}")
                    st.markdown(f"**🎯 Motives:** {', '.join(group_info['key_motives'])}")
                    st.markdown(f"**📅 Active:** {group_info['first_seen']} - {group_info['last_seen']}")
                    st.markdown("**📜 Campaign Timeline:**")
                    for line in group_info["campaign_timelines"]:
                        st.markdown(f"- {line}")
            else:
                st.warning(f"No detailed info for group: {group_name}")

        st.markdown("---")
        st.subheader("🛠️ Techniques Involved")

        # Convert techniques to DataFrame for better display
        df = pd.DataFrame(output["techniques_code"])
        df.fillna("N/A", inplace=True)
        df.columns = ["Technique ID", "Technique Name", "Tactic"]

        # Highlight input technique
        def highlight_input_technique(row):
            return ['background-color: #ffe0b3' if row["Technique ID"] == technique_id else '' for _ in row]

        st.dataframe(df.style.apply(highlight_input_technique, axis=1), use_container_width=True)

        st.markdown("---")
        st.subheader(f"🛠️ Techniques Involved with Accuracy <= {accuracy_threshold}")

        # Convert techniques to DataFrame for better display
        df = pd.DataFrame(output["filtered_technique_code"])
        df.fillna("N/A", inplace=True)
        df.columns = ["Technique ID", "Technique Name", "Tactic"]
        st.dataframe(df.style.apply(highlight_input_technique, axis=1), use_container_width=True)
    else:
        st.warning(f"No details present for given Technique ID , Please Try with some other valid Technique ID from MITRE")
    # st.markdown("---")
    # st.subheader("📦 Raw Output JSON")
    # st.code(json.dumps(output, indent=2), language="json")
