"""Internationalization (i18n) support for AI Pathfinder."""
from __future__ import annotations

TRANSLATIONS = {
    # ─── Navigation ───
    "nav_path": {"zh": "🗺️ 路径规划", "en": "🗺️ Path Planner"},
    "nav_chat": {"zh": "🧠 智能对话", "en": "🧠 AI Chat"},
    "nav_browser": {"zh": "📚 资源浏览", "en": "📚 Resources"},
    "nav_radar": {"zh": "🔥 趋势雷达", "en": "🔥 Trend Radar"},
    "nav_import": {"zh": "📤 导入计划", "en": "📤 Import Plan"},
    # ─── Sidebar ───
    "sidebar_title": {"zh": "🧭 AI Pathfinder", "en": "🧭 AI Pathfinder"},
    "sidebar_caption": {"zh": "个性化AI学习路径规划", "en": "Personalized AI Learning Paths"},
    "sidebar_profile": {"zh": "📋 当前画像", "en": "📋 Current Profile"},
    "sidebar_level": {"zh": "**水平**", "en": "**Level**"},
    "sidebar_direction": {"zh": "**方向**", "en": "**Direction**"},
    "sidebar_focus": {"zh": "**重心**", "en": "**Focus**"},
    "sidebar_goal": {"zh": "**目标**", "en": "**Goal**"},
    "sidebar_time": {"zh": "**时间**", "en": "**Time**"},
    "sidebar_share_hint": {"zh": "🔗 路径已编码到地址栏，可直接复制分享", "en": "🔗 Path encoded in URL — copy to share"},
    "sidebar_replan": {"zh": "🔄 重新规划", "en": "🔄 Re-plan"},
    "sidebar_footer": {"zh": "开源免费 · 社区驱动", "en": "Open Source · Community Driven"},
    # ─── Form Page ───
    "form_title": {"zh": "🧭 AI Pathfinder", "en": "🧭 AI Pathfinder"},
    "form_subtitle": {
        "zh": "> 告诉我你的**现在**和**目标**，我来帮你规划最短最有效的AI学习路径——完全免费，开源。",
        "en": "> Tell me **where you are** and **where you want to go** — I'll plan the most effective AI learning path for you. Free & open source.",
    },
    "form_stats": {
        "zh": "📊 90 条精选资源 · 📡 15 个持续信息源 · 🧱 基础→🔧 实战全覆盖",
        "en": "📊 90 curated resources · 📡 15 ongoing channels · 🧱 foundations → 🔧 hands-on",
    },
    "form_quick_start": {"zh": "⚡ 快速开始", "en": "⚡ Quick Start"},
    "form_quick_hint": {
        "zh": "选一个最接近你方向的模板，一键填入表单，之后仍可修改",
        "en": "Pick the template closest to your goals — auto-fills the form, still editable",
    },
    "form_select": {"zh": "选择", "en": "Select"},
    "form_restored": {
        "zh": "📎 已从分享链接恢复用户画像，确认无误后点击下方生成按钮",
        "en": "📎 Profile restored from shared link. Review and click Generate below.",
    },
    "form_level": {"zh": "📊 当前水平", "en": "📊 Current Level"},
    "form_hours": {"zh": "⏰ 每周可投入（小时）", "en": "⏰ Hours per Week"},
    "form_goal": {"zh": "🎯 你的目标（越具体越好）", "en": "🎯 Your Goal (be specific)"},
    "form_goal_placeholder": {
        "zh": "例：3个月内能搭建一个RAG问答系统并部署上线，已有Python基础",
        "en": "e.g., Build and deploy a RAG Q&A system within 3 months. I know Python.",
    },
    "form_preference": {"zh": "🎨 偏好学习方式", "en": "🎨 Learning Style"},
    "form_direction": {"zh": "🎯 目标方向", "en": "🎯 Target Direction"},
    "form_language": {"zh": "🌐 语言偏好", "en": "🌐 Language Preference"},
    "form_focus": {"zh": "🎓 学习重心", "en": "🎓 Learning Focus"},
    "form_focus_hint": {
        "zh": "打基础：侧重数学原理和论文理解\n重实战：侧重项目实操和工具使用",
        "en": "Foundational: math, theory & papers\nApplied: projects, tools & deployment",
    },
    "form_skills": {"zh": "💼 当前技能/项目经历（可选，填写后推荐更精准）", "en": "💼 Skills & Experience (optional, improves recommendations)"},
    "form_skills_placeholder": {
        "zh": "例：做过 3 年 Web 后端开发，用过 Spring Boot 和 Python，写过自动化测试脚本，没接触过机器学习",
        "en": "e.g., 3 years of web backend dev with Spring Boot & Python. Wrote test automation scripts. No ML experience.",
    },
    "form_submit": {"zh": "🚀 生成我的学习路径", "en": "🚀 Generate My Learning Path"},
    "form_empty_goal": {"zh": "请填写学习目标", "en": "Please enter a learning goal"},
    "form_goal_too_long": {"zh": "学习目标最长 1000 字", "en": "Goal text must be under 1000 characters"},
    "form_generating": {
        "zh": "🤔 正在为你规划学习路径，约需 10-20 秒...",
        "en": "🤔 Planning your learning path, ~10-20 seconds...",
    },
    # ─── Path Page ───
    "path_weeks": {"zh": "预计完成：约", "en": "Estimated completion: ~"},
    "path_weeks_unit": {"zh": "周", "en": "weeks"},
    "path_week": {"zh": "📅 第 {n} 周 — ", "en": "📅 Week {n} — "},
    "path_ongoing": {"zh": "持续关注", "en": "ongoing"},
    "path_progress": {"zh": "学习进度：{done}/{total} 个资源已完成", "en": "Progress: {done}/{total} resources completed"},
    "path_progress_warn": {
        "zh": "⚠️ 进度仅在当前会话有效，刷新页面后重置。建议使用下方「导出」保存学习计划。",
        "en": "⚠️ Progress is session-only and resets on refresh. Use Export below to save.",
    },
    "path_no_resources": {"zh": "暂无可追踪的资源", "en": "No trackable resources"},
    "path_save_title": {"zh": "💾 保存学习计划", "en": "💾 Save Learning Plan"},
    "path_save_hint": {
        "zh": "导出后可离线查看、打印、或下次导入恢复",
        "en": "Export for offline viewing, printing, or re-importing later",
    },
    "path_export_md": {"zh": "📄 导出为 Markdown", "en": "📄 Export as Markdown"},
    "path_export_json": {"zh": "📦 导出为 JSON（可导入）", "en": "📦 Export as JSON (importable)"},
    # ─── Analytics ───
    "analytics_title": {"zh": "📊 学习路径分析", "en": "📊 Path Analytics"},
    "analytics_hint": {"zh": "自动从你的学习路径中提取统计数据", "en": "Auto-generated stats from your learning path"},
    "analytics_total": {"zh": "📚 总资源", "en": "📚 Resources"},
    "analytics_hours": {"zh": "⏱ 总学时", "en": "⏱ Total Hours"},
    "analytics_weeks": {"zh": "📅 周数", "en": "📅 Weeks"},
    "analytics_lang": {"zh": "🌐 语言", "en": "🌐 Languages"},
    "analytics_tab_dist": {"zh": "📊 资源分布", "en": "📊 Distribution"},
    "analytics_tab_pace": {"zh": "📈 每周节奏", "en": "📈 Weekly Pace"},
    "analytics_tab_topics": {"zh": "🏷️ 话题覆盖", "en": "🏷️ Topic Coverage"},
    "analytics_type_comp": {"zh": "**资源类型构成**", "en": "**Resource Types**"},
    "analytics_focus_dist": {"zh": "**学习侧重分布**", "en": "**Focus Distribution**"},
    "analytics_weekly_pace": {"zh": "**每周学习节奏**", "en": "**Weekly Learning Pace**"},
    "analytics_top_topics": {"zh": "**话题覆盖 Top 15**", "en": "**Top 15 Topics**"},
    # ─── Feedback ───
    "fb_title": {"zh": "📝 学习反馈", "en": "📝 Feedback"},
    "fb_hint": {"zh": "你的反馈会帮助我们持续优化推荐质量", "en": "Your feedback helps us improve recommendations"},
    "fb_rating": {"zh": "满意度", "en": "Satisfaction"},
    "fb_comment": {"zh": "💬 意见或建议（可选）", "en": "💬 Comments (optional)"},
    "fb_comment_placeholder": {
        "zh": "哪些推荐很好？哪些可以改进？",
        "en": "What worked well? What could be improved?",
    },
    "fb_submit": {"zh": "提交反馈", "en": "Submit Feedback"},
    "fb_thanks_github": {"zh": "感谢反馈！已记录到 GitHub Issues 🙏", "en": "Thanks! Recorded as GitHub Issue 🙏"},
    "fb_thanks_local": {"zh": "感谢反馈！🙏", "en": "Thanks for your feedback! 🙏"},
    # ─── Resource Browser ───
    "browser_title": {"zh": "📚 资源库", "en": "📚 Resource Library"},
    "browser_hint": {"zh": "浏览全部资源 · 5 维筛选 · 关键词搜索", "en": "Browse all resources · 5 filters · keyword search"},
    "browser_total": {"zh": "总资源", "en": "Total"},
    "browser_chinese": {"zh": "🇨🇳 中文", "en": "🇨🇳 Chinese"},
    "browser_channels": {"zh": "📡 信息源", "en": "📡 Channels"},
    "browser_repos": {"zh": "💻 实战项目", "en": "💻 Repos"},
    "browser_builders": {"zh": "👤 大牛", "en": "👤 Builders"},
    "browser_foundational": {"zh": "🧱 打基础", "en": "🧱 Foundational"},
    "browser_applied": {"zh": "🔧 重实战", "en": "🔧 Applied"},
    "browser_search": {"zh": "🔍 搜索资源", "en": "🔍 Search resources"},
    "browser_search_placeholder": {
        "zh": "输入关键词搜索标题、描述或主题（如：RAG、Agent、微调...）",
        "en": "Search titles, descriptions or topics (e.g., RAG, Agent, fine-tuning...)",
    },
    "browser_topic": {"zh": "主题", "en": "Topics"},
    "browser_type": {"zh": "类型", "en": "Types"},
    "browser_level": {"zh": "难度", "en": "Levels"},
    "browser_domain": {"zh": "方向领域", "en": "Domains"},
    "browser_focus_filter": {"zh": "学习重心", "en": "Focus"},
    "browser_showing": {"zh": "显示 {shown} / {total} 条", "en": "Showing {shown} / {total}"},
    # ─── Trend Radar ───
    "radar_title": {"zh": "🔥 趋势雷达", "en": "🔥 Trend Radar"},
    "radar_subtitle": {
        "zh": "> AI 领域变化极快——学完基础后，**持续跟踪趋势**和学完一门课一样重要。",
        "en": "> AI moves fast — **tracking trends** is just as important as finishing a course.",
    },
    "radar_sources": {"zh": "📡 推荐信息源", "en": "📡 Recommended Sources"},
    "radar_insights_title": {"zh": "🔮 今日 AI 趋势洞察", "en": "🔮 Today's AI Trend Insights"},
    "radar_insights_refresh": {"zh": "🔄 刷新", "en": "🔄 Refresh"},
    "radar_insights_loading": {"zh": "正在分析 AI 趋势...", "en": "Analyzing AI trends..."},
    "radar_insights_empty": {"zh": "暂无洞察数据，请配置 API Key 后点击刷新", "en": "No insights yet. Configure API Key and click Refresh."},
    "radar_insights_overview": {"zh": "趋势总览", "en": "Trend Overview"},
    "radar_insights_date": {"zh": "📅 洞察生成日期：{date}（每日自动更新）", "en": "📅 Generated: {date} (daily auto-refresh)"},
    "radar_sources_hint": {
        "zh": "这些是经过筛选的高质量持续学习渠道，建议每周花 1-2 小时浏览",
        "en": "Curated high-quality channels — spend 1-2 hours per week browsing",
    },
    "radar_zh_sources": {"zh": "**🇨🇳 中文信息源**", "en": "**🇨🇳 Chinese Sources**"},
    "radar_en_sources": {"zh": "**🇬🇧 英文信息源**", "en": "**🇬🇧 English Sources**"},
    "radar_newbie": {"zh": "🧭 新手？从这里开始", "en": "🧭 New here? Start here"},
    "radar_newbie_intro": {
        "zh": "**不知道从哪里学？按你的状态选一条路：**",
        "en": "**Not sure where to start? Pick a path based on your level:**",
    },
    "radar_links": {"zh": "🔗 快速跳转", "en": "🔗 Quick Links"},
    # ─── Radar – Builders / 行业大牛 ───
    "radar_builders_title": {"zh": "👤 行业大牛", "en": "👤 AI Builders"},
    "radar_builders_hint": {
        "zh": "关注**实际在做事的建设者**，而非转述信息的博主。参考 [follow-builders](https://github.com/zarazhangrui/follow-builders) 理念。",
        "en": "Follow **builders who ship**, not influencers who retweet. Inspired by [follow-builders](https://github.com/zarazhangrui/follow-builders).",
    },
    "radar_for_you": {"zh": "🎯 为你推荐", "en": "🎯 Recommended for You"},
    "radar_for_you_hint": {
        "zh": "基于你的学习方向 **{direction}**，以下是最相关的信息源和大牛",
        "en": "Based on your direction **{direction}**, here are the most relevant sources and builders",
    },
    "radar_all_builders": {"zh": "👥 所有大牛", "en": "👥 All Builders"},
    "radar_role_researcher": {"zh": "🔬 研究员", "en": "🔬 Researcher"},
    "radar_role_engineer": {"zh": "🛠️ 工程师", "en": "🛠️ Engineer"},
    "radar_role_founder": {"zh": "🚀 创始人", "en": "🚀 Founder"},
    "radar_role_educator": {"zh": "📖 教育者", "en": "📖 Educator"},
    # ─── Import Plan ───
    "import_title": {"zh": "📤 导入学习计划", "en": "📤 Import Learning Plan"},
    "import_subtitle": {
        "zh": "> 上传之前导出的 JSON 文件，恢复你的学习路径和个人画像。",
        "en": "> Upload a previously exported JSON file to restore your learning path.",
    },
    "import_upload": {"zh": "选择 JSON 文件", "en": "Choose JSON file"},
    "import_upload_help": {
        "zh": "支持通过「导出为 JSON」按钮生成的文件",
        "en": "Supports files generated by the Export as JSON button",
    },
    "import_invalid": {"zh": "文件格式无效：缺少 profile 或 path 字段", "en": "Invalid format: missing profile or path field"},
    "import_success": {"zh": "✅ 文件解析成功！", "en": "✅ File parsed successfully!"},
    "import_profile_preview": {"zh": "📋 画像预览", "en": "📋 Profile Preview"},
    "import_path_preview": {"zh": "📊 路径预览", "en": "📊 Path Preview"},
    "import_load": {"zh": "🚀 加载此计划", "en": "🚀 Load This Plan"},
    "import_json_error": {"zh": "文件不是有效的 JSON 格式", "en": "File is not valid JSON"},
    "import_too_large": {"zh": "文件过大，请上传 2MB 以内的文件", "en": "File too large, max 2MB"},
    "import_parse_error": {"zh": "解析失败：", "en": "Parse error: "},
    # ─── Chat ───
    "chat_title": {"zh": "🧠 智能对话", "en": "🧠 AI Chat"},
    "chat_subtitle": {
        "zh": "> 学习过程中遇到问题？随时问我。我了解你的学习画像和路径。",
        "en": "> Got questions while learning? Ask me anytime. I know your profile and path.",
    },
    "chat_no_profile": {
        "zh": "💡 还没有生成学习路径？先去「路径规划」生成一个，对话会更有针对性。",
        "en": "💡 No learning path yet? Generate one in Path Planner for more relevant answers.",
    },
    "chat_input": {
        "zh": "输入你的问题，例如「RAG 和 Fine-tuning 有什么区别？」",
        "en": "Ask a question, e.g., \"What's the difference between RAG and fine-tuning?\"",
    },
    "chat_no_key": {"zh": "请先在左侧边栏配置 API Key", "en": "Please configure your API Key in the sidebar first"},
    "chat_error": {"zh": "请求失败：", "en": "Request failed: "},
    "chat_clear": {"zh": "🗑️ 清空对话", "en": "🗑️ Clear Chat"},
    "chat_thinking": {"zh": "思考中...", "en": "Thinking..."},
    # ─── Settings ───
    "settings_title": {"zh": "⚙️ API 设置", "en": "⚙️ API Settings"},
    "settings_provider": {"zh": "模型供应商", "en": "Model Provider"},
    "settings_model": {"zh": "模型", "en": "Model"},
    "settings_custom_url": {"zh": "API Base URL", "en": "API Base URL"},
    "settings_custom_model": {"zh": "模型名称", "en": "Model Name"},
    "settings_key": {"zh": "API Key", "en": "API Key"},
    # ─── Progress Persistence ───
    "progress_save_title": {"zh": "💾 保存学习进度", "en": "💾 Save Learning Progress"},
    "progress_save_hint": {
        "zh": "保存后刷新页面或下次打开可恢复进度（含勾选状态和对话记录）",
        "en": "Save to restore progress after refresh or next visit (includes checkboxes & chat)",
    },
    "progress_save_server": {"zh": "💾 保存到服务器", "en": "💾 Save to Server"},
    "progress_download": {"zh": "⬇️ 下载进度文件", "en": "⬇️ Download Progress"},
    "progress_saved_ok": {"zh": "✅ 进度已保存！下次打开时可恢复", "en": "✅ Progress saved! Restorable on next visit"},
    "progress_save_empty": {"zh": "⚠️ 还没有可保存的学习进度", "en": "⚠️ No progress to save yet"},
    "progress_found": {
        "zh": "💾 发现上次进度（{time}，{direction}，已完成 {done} 项）",
        "en": "💾 Saved progress found ({time}, {direction}, {done} done)",
    },
    "progress_restore": {"zh": "🔄 恢复上次进度", "en": "🔄 Restore Progress"},
    "progress_import_restored": {"zh": "✅ 已恢复 {done} 项完成记录和 {chat} 条对话", "en": "✅ Restored {done} completed items and {chat} chat messages"},
    # ─── Errors ───
    "error_generate": {"zh": "生成失败：", "en": "Generation failed: "},
    "error_no_resources": {
        "zh": "未找到匹配的资源，将使用全部资源生成路径。",
        "en": "No matching resources found. Using all resources to generate the path.",
    },
    "error_api_hint": {
        "zh": "💡 请在左侧边栏的 **⚙️ API 设置** 中输入你的 API Key，或在 `.streamlit/secrets.toml` 中配置 `DASHSCOPE_API_KEY`",
        "en": "💡 Enter your API Key in **⚙️ API Settings** in the sidebar, or set `DASHSCOPE_API_KEY` in `.streamlit/secrets.toml`",
    },
    "error_model_hint": {
        "zh": "💡 模型名称可能有误，请在左侧边栏的 **⚙️ API 设置** 中检查模型名称",
        "en": "💡 Model name might be wrong — check it in **⚙️ API Settings** in the sidebar",
    },
    "path_week_no_resources": {
        "zh": "本周规划的资源未能匹配到资源库，请尝试重新规划。",
        "en": "The planned resources for this week couldn't be matched. Try re-planning.",
    },
    # ─── Inline i18n consolidation (Round 18) ───
    "path_finish_label": {"zh": "预计完成", "en": "Target"},
    "path_share_label": {"zh": "📋 复制分享链接", "en": "📋 Copy share link"},
    "path_follow_label": {"zh": "👤 推荐关注", "en": "👤 Follow"},
    "chat_current_profile": {"zh": "当前画像", "en": "Profile"},
    "browser_sort": {"zh": "排序", "en": "Sort"},
    "chat_export": {"zh": "📥 导出对话", "en": "📥 Export Chat"},
    "freshness_just_now": {"zh": "刚刚生成", "en": "Just generated"},
    "freshness_min_ago": {"zh": "分钟前", "en": "min ago"},
    "freshness_hour_ago": {"zh": "小时前", "en": "h ago"},
    "freshness_over_day": {"zh": "超过1天", "en": ">1 day old"},
    "retry_label": {"zh": "🔄 重试生成", "en": "🔄 Retry"},
}


def t(key: str, lang: str = "zh", **kwargs) -> str:
    """Translate a key to the given language. Falls back to zh if key not found."""
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang, entry.get("zh", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
