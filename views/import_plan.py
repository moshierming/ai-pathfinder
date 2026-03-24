"""Import plan view."""

import json

import streamlit as st

from i18n import t
from utils import encode_profile
from views import _lang


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
            raw = uploaded.read()
            if len(raw) > 2 * 1024 * 1024:  # 2 MB
                st.error(t("import_too_large", L))
                return
            data = json.loads(raw.decode("utf-8"))
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

            # Show progress info if present
            done_data = data.get("done", {})
            chat_data = data.get("chat_messages", [])
            if done_data or chat_data:
                st.info(t("progress_import_restored", L, done=len(done_data), chat=len(chat_data)))

            with st.expander(t("import_path_preview", L)):
                st.write(f"**总结**: {path_data.get('summary', '-')}")
                st.write(f"**周数**: {path_data.get('estimated_weeks', '?')}")
                for week in path_data.get("weeks", [])[:3]:
                    st.caption(f"第 {week['week']} 周: {week['goal']}")

            if st.button(t("import_load", L), type="primary", use_container_width=True):
                st.session_state.path = path_data
                st.session_state.profile = profile
                st.query_params["p"] = encode_profile(profile)
                # Restore progress data if present
                for k, v in done_data.items():
                    if isinstance(k, str) and k.startswith("done_"):
                        st.session_state[k] = v
                if chat_data:
                    st.session_state.chat_messages = chat_data
                st.rerun()

        except json.JSONDecodeError:
            st.error(t("import_json_error", L))
        except Exception as e:
            st.error(f"{t('import_parse_error', L)}{e}")
