import streamlit as st

LANGUAGES = {
    "English": "en",
    "Arabic": "ar"
}

TRANSLATIONS = {
    "en": {
        # General
        "app_title": "YouTube Learning Assistant",
        "welcome": "Welcome to the YouTube Learning Assistant. Use the sidebar to navigate between different features.",
        "select_language": "Select Language",

        # Navigation
        "navigation": "Navigation",
        "nav_instructions": "Use the menu below to navigate through the app:",
        "home": "Home: You are here",
        "summary": "Summary: Process videos and view summaries",
        "chat": "Chat: Interact with video content",
        "quiz": "Quiz: Take quizzes on processed videos",
        "notes": "Notes: Generate and view in-depth notes",

        # Goals
        "learning_goals": "Learning Goals",
        "delete": "Delete",
        "add_new_goal": "Add a new goal",
        "add_goal": "Add Goal",
        "current_goals": "Your Current Learning Goals",
        "no_goals": "You haven't set any learning goals yet. Use the sidebar to add some!",

        # Getting Started
        "getting_started": "Getting Started",
        "getting_started_instructions": "Follow these steps to make the most of the YouTube Learning Assistant:\n\n1. Set Your Goals\n2. Process a Video\n3. Chat About the Video\n4. Test Your Knowledge\n5. Review In-Depth Notes",
        
        # Tips
        "tips": "Tips",
        "tips_content": "- Keep your learning goals specific and actionable for best results.\n- You can process multiple videos and switch between them in the Chat, Quiz, and Notes sections.\n- Don't forget to download your notes for offline study!",

        # Summary Page
        "summary_title": "Video Summary",
        "process_new_video": "Process New Video",
        "enter_youtube_url": "Enter YouTube Video URL",
        "process_video": "Process Video",
        "processing_video": "Processing video...",
        "video_title": "Video Title",
        "invalid_url": "Invalid YouTube URL. Please try again.",
        "view_processed_summaries": "View Processed Video Summaries",
        "choose_processed_video": "Choose a processed video:",
        "view_summary": "View Summary",
        "retrieving_summary": "Retrieving summary...",
        "summary_for": "Summary for",
        "no_videos_processed": "No videos processed yet.",
        "all_processed_videos": "All Processed Videos",

        # Chat Page
        "chat_title": "Chat with Video Content",
        "select_video_chat": "Select a video to chat about:",
        "chatting_about": "Chatting about:",
        "ask_about_video": "Ask about the video content",
        "clear_chat": "Clear Chat History",

        # Quiz Page
        "quiz_title": "Quiz",
        "select_video_quiz": "Select a video for the quiz:",
        "generate_quiz": "Generate Quiz",
        "generating_quiz": "Generating quiz...",
        "quiz_for": "Quiz for",
        "submit_answers": "Submit Answers",
        "correct_answer": "Correct Answer:",
        "explanation": "Explanation:",
        "your_score": "Your Score:",

        # Notes Page
        "notes_title": "In-depth Notes",
        "select_video_notes": "Choose a video for notes:",
        "generate_notes": "Generate Notes",
        "generating_notes": "Generating notes...",
        "notes_for": "Notes for",
        "download_notes": "Download Notes",

        "page_home": "Home",
        "page_summary": "Summary",
        "page_chat": "Chat",
        "page_quiz": "Quiz",
        "page_notes": "Notes",
    },
    "ar": {
        "page_home": "الرئيسية",
        "page_summary": "الملخص",
        "page_chat": "الدردشة",
        "page_quiz": "الاختبار",
        "page_notes": "الملاحظات",

        # General
        "app_title": "مساعد التعلم على يوتيوب",
        "welcome": "مرحبًا بك في مساعد التعلم على يوتيوب. استخدم الشريط الجانبي للتنقل بين الميزات المختلفة.",
        "select_language": "اختر اللغة",

        # Navigation
        "navigation": "التنقل",
        "nav_instructions": "استخدم القائمة أدناه للتنقل عبر التطبيق:",
        "home": "الرئيسية: أنت هنا",
        "summary": "الملخص: معالجة مقاطع الفيديو وعرض الملخصات",
        "chat": "الدردشة: التفاعل مع محتوى الفيديو",
        "quiz": "الاختبار: إجراء اختبارات على مقاطع الفيديو المعالجة",
        "notes": "الملاحظات: إنشاء وعرض ملاحظات مفصلة",

        # Goals
        "learning_goals": "أهداف التعلم",
        "delete": "حذف",
        "add_new_goal": "أضف هدفًا جديدًا",
        "add_goal": "إضافة هدف",
        "current_goals": "أهداف التعلم الحالية",
        "no_goals": "لم تقم بتعيين أي أهداف تعليمية بعد. استخدم الشريط الجانبي لإضافة بعض الأهداف!",

        # Getting Started
        "getting_started": "البدء",
        "getting_started_instructions": "اتبع هذه الخطوات للاستفادة القصوى من مساعد التعلم على يوتيوب:\n\n1. حدد أهدافك\n2. قم بمعالجة فيديو\n3. تحدث عن الفيديو\n4. اختبر معرفتك\n5. راجع الملاحظات المفصلة",
        
        # Tips
        "tips": "نصائح",
        "tips_content": "- احرص على أن تكون أهداف التعلم محددة وقابلة للتنفيذ للحصول على أفضل النتائج.\n- يمكنك معالجة مقاطع فيديو متعددة والتبديل بينها في أقسام الدردشة والاختبار والملاحظات.\n- لا تنس تنزيل ملاحظاتك للدراسة دون اتصال بالإنترنت!",

        # Summary Page
        "summary_title": "ملخص الفيديو",
        "process_new_video": "معالجة فيديو جديد",
        "enter_youtube_url": "أدخل رابط فيديو يوتيوب",
        "process_video": "معالجة الفيديو",
        "processing_video": "جاري معالجة الفيديو...",
        "video_title": "عنوان الفيديو",
        "invalid_url": "رابط يوتيوب غير صالح. يرجى المحاولة مرة أخرى.",
        "view_processed_summaries": "عرض ملخصات الفيديوهات المعالجة",
        "choose_processed_video": "اختر فيديو معالج:",
        "view_summary": "عرض الملخص",
        "retrieving_summary": "جاري استرجاع الملخص...",
        "summary_for": "ملخص لـ",
        "no_videos_processed": "لم تتم معالجة أي فيديوهات بعد.",
        "all_processed_videos": "جميع الفيديوهات المعالجة",

        # Chat Page
        "chat_title": "الدردشة مع محتوى الفيديو",
        "select_video_chat": "اختر فيديو للدردشة عنه:",
        "chatting_about": "الدردشة عن:",
        "ask_about_video": "اسأل عن محتوى الفيديو",
        "clear_chat": "مسح سجل الدردشة",

        # Quiz Page
        "quiz_title": "الاختبار",
        "select_video_quiz": "اختر فيديو للاختبار:",
        "generate_quiz": "إنشاء اختبار",
        "generating_quiz": "جاري إنشاء الاختبار...",
        "quiz_for": "اختبار لـ",
        "submit_answers": "إرسال الإجابات",
        "correct_answer": "الإجابة الصحيحة:",
        "explanation": "التفسير:",
        "your_score": "نتيجتك:",

        # Notes Page
        "notes_title": "ملاحظات مفصلة",
        "select_video_notes": "اختر فيديو للملاحظات:",
        "generate_notes": "إنشاء ملاحظات",
        "generating_notes": "جاري إنشاء الملاحظات...",
        "notes_for": "ملاحظات لـ",
        "download_notes": "تنزيل الملاحظات",
    }
}

def get_translation(key):
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS[lang].get(key, key)

def initialize_language_selection():
    if "language" not in st.session_state:
        st.session_state.language = "en"

    selected_language = st.sidebar.selectbox(
        "Select Language / اختر اللغة",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: x,
        index=list(LANGUAGES.values()).index(st.session_state.language),
        key="language_selector"
    )
    st.session_state.language = LANGUAGES[selected_language]

def set_rtl_style():
    if st.session_state.language == "ar":
        st.markdown(
            """
            <style>
            .stApp {
                direction: rtl;
                text-align: right;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .stApp {
                direction: ltr;
                text-align: left;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

def get_translated_page_names():
    return {
        "Home": get_translation("page_home"),
        "1_Summary": get_translation("page_summary"),
        "2_Chat": get_translation("page_chat"),
        "3_Quiz": get_translation("page_quiz"),
        "4_Notes": get_translation("page_notes"),
    }