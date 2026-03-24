"""Import plan view."""

import json

import streamlit as st

from i18n import t
from utils import encode_profile


def _lang():
    return st.session_state.get("ui_lang", "zh")


def render_import_plan(resources: list):
    L = _lang()
    st.title(t("import_title", L))
    st.markdown(t("import_subtitle", L))
    st.divider()

    uploaded = st.file_uploader(
        t("import_upload", L),
        type=["json"],
        help=t("import_upload_help", L),
    )

    if uploaded is not None:
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
            profile = data.get("profile")
            path_data = data.get("path")
            if not profile or not path_data:
                st.error(t("import_invalid", L))
                return

            st.success(t("import_success", L))

            with st.expander(t("import_profile_preview", L), expanded=True):
                st.write(f"**水平**: {profile.get('level', '-')}")
                st.write(f"**方向**: {profile.get('direction', '-')}")
                st.write(f"**学习重心**: {profile.get('focus', '-')}")
                st.write(f"**目标**: {profile.get('goal', '-')}")
                st.write(f"**时间**: {profile.get('hours_per_week', '-')}h/{'wk' if L == 'en' else '周'}")

            with st.expander(t("import_path_preview", L)):
                st.write(f"**总结**: {path_data.get('summary', '-')}")
                st.write(f"**周数**: {path_data.get('estimated_weeks', '?')}")
                for week in path_data.get("weeks", [])[:3]:
                    st.caption(f"第 {week['week']} 周: {week['goal']}")

            if st.button(t("import_load", L), type="primary", use_container_width=True):
                st.session_state.path = path_data
                st.session_state.profile = profile
                st.query_params["p"] = encode_profile(profile)
                st.rerun()

        except json.JSONDecodeError:
            st.error(t("import_json_error", L))
        except Exception as e:
            st.error(f"{t('import_parse_error', L)}{e}")
