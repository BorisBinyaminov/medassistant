# bot/tests/cases_v3_extended.py
# -*- coding: utf-8 -*-

CASES = [
    # --- CARDIO / ED ACUTE ---
    {
        "name": "01_chest_pain_typical_angina_male55",
        "quoted": [
            "давящая боль в груди с отдачей в левую руку",
            "началось 30 минут назад, не проходит",
            "холодный пот",
            "одышка",
        ],
        "context": {
            "chief_complaint": "chest pain",
            "onset": "30 minutes ago",
            "duration": "persistent",
            "associated_symptoms": ["dyspnea", "cold sweat"],
            "severity_0_10": 8,
            "sex": "male",
            "age": 55,
            "negatives": ["no nausea"]
        },
        "expected_levels": ["ED now"]
    },
    {
        "name": "02_pericarditis_pleuritic_pain_young",
        "quoted": [
            "колющая боль в груди усиливается при глубоком вдохе",
            "облегчается сидя, хуже лежа",
            "температура 37.8",
            "началось два дня назад",
        ],
        "context": {
            "chief_complaint": "pleuritic chest pain",
            "duration": "2 days",
            "associated_symptoms": ["low-grade fever"],
            "age": 26,
            "sex": "male",
            "negatives": ["no dyspnea at rest", "no radiation to arm"]
        },
        "expected_levels": ["urgent care today", "see GP in 24-48h"]
    },
    {
        "name": "03_palpitations_afib_elderly",
        "quoted": [
            "сердцебиение",
            "одышка при нагрузке",
            "началось вчера вечером",
            "головокружение",
        ],
        "context": {
            "chief_complaint": "palpitations",
            "onset": "yesterday evening",
            "associated_symptoms": ["dyspnea on exertion", "dizziness"],
            "age": 74,
            "sex": "female",
            "negatives": ["no chest pain"]
        },
        "expected_levels": ["urgent care today"]
    },

    # --- NEURO ---
    {
        "name": "04_stroke_facial_droop_weakness",
        "quoted": [
            "вдруг перекосило лицо",
            "трудно говорить",
            "слабость в правой руке",
            "30 минут назад",
        ],
        "context": {
            "chief_complaint": "sudden neuro deficit",
            "onset": "30 minutes ago",
            "negatives": ["no seizures", "no head trauma"]
        },
        "expected_levels": ["ED now"]
    },
    {
        "name": "05_tension_headache_stress",
        "quoted": [
            "давящая головная боль как обруч",
            "началось к вечеру",
            "6/10",
            "фотофобии нет, рвоты нет",
        ],
        "context": {
            "chief_complaint": "headache",
            "onset": "this evening",
            "severity_0_10": 6,
            "negatives": ["no photophobia", "no vomiting", "no trauma"]
        },
        "expected_levels": ["see GP in 24-48h", "self-care"]
    },
    {
        "name": "06_migraine_with_aura_female",
        "quoted": [
            "мерцающие зигзаги перед глазами",
            "пульсирующая боль слева",
            "тошнота",
            "светобоязнь",
        ],
        "context": {
            "chief_complaint": "migraine with aura",
            "onset": "2 hours",
            "sex": "female",
            "age": 29,
            "negatives": ["no worst-ever", "no weakness"]
        },
        "expected_levels": ["see GP in 24-48h"]
    },

    # --- RESPIRATORY / INFECTIOUS ---
    {
        "name": "07_pneumonia_cough_fever",
        "quoted": [
            "кашель с мокротой, температура 38.5",
            "боль в груди при вдохе",
            "одышка при ходьбе",
            "началось 3 дня назад"
        ],
        "context": {
            "chief_complaint": "cough with fever",
            "duration": "3 days",
            "associated_symptoms": ["pleuritic chest pain", "dyspnea on exertion"],
            "age": 44,
            "sex": "female"
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "08_bronchitis_cough_no_fever",
        "quoted": [
            "сухой кашель",
            "температуры нет",
            "началось 5 дней назад",
            "слабость"
        ],
        "context": {
            "chief_complaint": "dry cough",
            "duration": "5 days",
            "negatives": ["no fever", "no chest pain"],
            "age": 37
        },
        "expected_levels": ["see GP in 24-48h", "self-care"]
    },
    {
        "name": "09_covid_like",
        "quoted": [
            "кашель, потеря запаха",
            "37.8",
            "началось 2 дня назад",
            "одышка при подъеме по лестнице"
        ],
        "context": {
            "chief_complaint": "cough anosmia",
            "duration": "2 days",
            "associated_symptoms": ["anosmia", "low-grade fever", "dyspnea on exertion"],
            "negatives": ["no chest pain"],
            "age": 31
        },
        "expected_levels": ["urgent care today", "see GP in 24-48h"]
    },

    # --- ENT ---
    {
        "name": "10_acute_otitis_media_child",
        "quoted": [
            "ребенок 3 года",
            "боль в ухе",
            "плачет по ночам",
            "температура 38.2"
        ],
        "context": {
            "chief_complaint": "ear pain child",
            "age": 3,
            "sex": "male",
            "associated_symptoms": ["fever 38.2", "night pain"],
            "duration": "1 day"
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "11_sinusitis_purulent",
        "quoted": [
            "заложенность носа",
            "гнойные выделения",
            "боль в области пазух",
            "10 дней не проходит"
        ],
        "context": {
            "chief_complaint": "sinus pain congestion",
            "duration": "10 days",
            "associated_symptoms": ["purulent discharge"],
            "negatives": ["no high fever"]
        },
        "expected_levels": ["see GP in 24-48h"]
    },
    {
        "name": "12_allergic_rhinitis_outdoor",
        "quoted": [
            "чихание",
            "зуд в глазах",
            "водянистый насморк на улице",
            "температуры нет"
        ],
        "context": {
            "chief_complaint": "allergic rhinitis",
            "onset": "this morning",
            "negatives": ["no fever"]
        },
        "expected_levels": ["self-care", "see GP in 24-48h"]
    },

    # --- GI / HEPATO ---
    {
        "name": "13_appendicitis_rlq_worsening",
        "quoted": [
            "боль внизу справа живота, усиливается при ходьбе",
            "8 часов назад, нарастает",
            "6/10",
            "тошнота, температуры нет"
        ],
        "context": {
            "chief_complaint": "right lower quadrant pain",
            "trajectory": "worsening",
            "severity_0_10": 6,
            "associated_symptoms": ["nausea"],
            "negatives": ["no fever"]
        },
        "expected_levels": ["urgent care today", "ED now"]
    },
    {
        "name": "14_cholecystitis_ruq_fever",
        "quoted": [
            "боль под правым ребром после жирной пищи",
            "температура 38.1",
            "тошнота",
            "началось вчера"
        ],
        "context": {
            "chief_complaint": "RUQ pain post-fatty meals",
            "duration": "1 day",
            "associated_symptoms": ["fever 38.1", "nausea"],
            "age": 40,
            "sex": "female"
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "15_pancreatitis_epigastric_to_back",
        "quoted": [
            "резкая боль вверху живота",
            "отдает в спину",
            "тошнота, рвота",
            "после алкоголя"
        ],
        "context": {
            "chief_complaint": "epigastric pain radiating to back",
            "associated_symptoms": ["nausea", "vomiting"],
            "triggers": ["alcohol"],
            "age": 45,
            "sex": "male"
        },
        "expected_levels": ["ED now", "urgent care today"]
    },
    {
        "name": "16_gastritis_epigastric_burning",
        "quoted": [
            "жжение вверху живота",
            "хуже натощак",
            "лучше после еды",
            "нет рвоты"
        ],
        "context": {
            "chief_complaint": "epigastric burning",
            "triggers": ["empty stomach", "relief after meal"],
            "negatives": ["no vomiting"],
            "age": 32
        },
        "expected_levels": ["see GP in 24-48h", "self-care"]
    },
    {
        "name": "17_upper_gi_bleed_melena",
        "quoted": [
            "черный стул",
            "слабость",
            "головокружение",
            "боль вверху живота"
        ],
        "context": {
            "chief_complaint": "black stools and epigastric pain",
            "associated_symptoms": ["dizziness", "weakness"],
            "age": 61
        },
        "expected_levels": ["ED now"]
    },

    # --- GU / URO / GYNE ---
    {
        "name": "18_cystitis_female_dysuria",
        "quoted": [
            "частое мочеиспускание",
            "жжение при мочеиспускании",
            "мутная моча",
            "37.5"
        ],
        "context": {
            "chief_complaint": "dysuria and frequency",
            "associated": ["cloudy urine", "low-grade fever"],
            "sex": "female",
            "age": 24
        },
        "expected_levels": ["see GP in 24-48h", "urgent care today"]
    },
    {
        "name": "19_pyelonephritis_flank_fever_female",
        "quoted": [
            "боль в пояснице слева",
            "озноб",
            "37.9, больно мочиться, моча мутная",
            "тошноты нет"
        ],
        "context": {
            "chief_complaint": "flank pain + urinary symptoms",
            "duration": "24h",
            "associated": ["chills", "dysuria", "cloudy urine", "37.9"],
            "sex": "female",
            "age": 26
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "20_ectopic_pregnancy_risk",
        "quoted": [
            "задержка месячных",
            "тянущая боль внизу живота справа",
            "слабое кровомазание",
            "головокружение"
        ],
        "context": {
            "chief_complaint": "pelvic pain with spotting",
            "sex": "female",
            "age": 30,
            "pregnant": True,
            "gestation": "6w"
        },
        "expected_levels": ["ED now"]
    },
    {
        "name": "21_early_preg_bleeding_8w",
        "quoted": [
            "беременность 8 недель",
            "тянущая боль внизу живота",
            "кровянистые выделения",
            "началось час назад"
        ],
        "context": {
            "chief_complaint": "first trimester bleeding",
            "gestation": "8w",
            "pregnant": True,
            "sex": "female",
            "age": 28
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "22_testicular_torsion",
        "quoted": [
            "внезапная сильная боль в мошонке",
            "тошнота",
            "началось час назад",
            "отек"
        ],
        "context": {
            "chief_complaint": "acute scrotal pain",
            "onset": "1h",
            "sex": "male",
            "age": 17
        },
        "expected_levels": ["ED now"]
    },

    # --- ENDO ---
    {
        "name": "23_dka_polyuria_polydipsia",
        "quoted": [
            "сильная жажда",
            "частое мочеиспускание",
            "тошнота",
            "слабость"
        ],
        "context": {
            "chief_complaint": "polyuria polydipsia with nausea",
            "age": 22,
            "sex": "male",
            "negatives": ["no fever"]
        },
        "expected_levels": ["ED now"]
    },
    {
        "name": "24_hypoglycemia_sweats_confusion",
        "quoted": [
            "холодный пот",
            "тремор",
            "путаюсь в словах",
            "улучшилось после сладкого"
        ],
        "context": {
            "chief_complaint": "possible hypoglycemia",
            "age": 36,
            "sex": "female"
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "25_thyrotoxicosis_tachy_heat",
        "quoted": [
            "сердцебиение",
            "не переносит жару",
            "похудение",
            "раздражительность"
        ],
        "context": {
            "chief_complaint": "palpitations and heat intolerance",
            "age": 34,
            "sex": "female"
        },
        "expected_levels": ["see GP in 24-48h", "urgent care today"]
    },

    # --- RHEUM / MSK ---
    {
        "name": "26_lumbar_strain_gym",
        "quoted": [
            "потянул поясницу в зале",
            "2 часа назад",
            "4/10",
            "онемения в ногах нет"
        ],
        "context": {
            "chief_complaint": "low back strain",
            "onset": "2h",
            "severity_0_10": 4,
            "negatives": ["no neuro deficits"],
            "age": 32,
            "sex": "male"
        },
        "expected_levels": ["self-care"]
    },
    {
        "name": "27_knee_swelling_trauma_twist",
        "quoted": [
            "подвернул колено",
            "припухлость",
            "боль при ходьбе",
            "щелчок в момент травмы"
        ],
        "context": {
            "chief_complaint": "knee injury",
            "age": 24,
            "negatives": ["no open wound"]
        },
        "expected_levels": ["see GP in 24-48h", "urgent care today"]
    },
    {
        "name": "28_gout_first_mtp",
        "quoted": [
            "внезапная боль в большом пальце ноги",
            "покраснение и отек",
            "ночью проснулся от боли",
            "пиво накануне"
        ],
        "context": {
            "chief_complaint": "acute first MTP pain",
            "age": 48,
            "sex": "male"
        },
        "expected_levels": ["see GP in 24-48h"]
    },

    # --- DERM ---
    {
        "name": "29_cellulitis_warm_erythema",
        "quoted": [
            "покраснение и тепло на голени",
            "боль",
            "37.8",
            "началось вчера"
        ],
        "context": {
            "chief_complaint": "leg redness warmth pain",
            "duration": "1 day",
            "age": 63
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "30_shingles_dermatomal_rash",
        "quoted": [
            "жгучая боль на одной стороне грудной клетки",
            "пузырьки по полоске",
            "началось два дня назад",
            "зуд"
        ],
        "context": {
            "chief_complaint": "unilateral dermatomal rash",
            "duration": "2 days",
            "age": 59
        },
        "expected_levels": ["see GP in 24-48h"]
    },
    {
        "name": "31_urticaria_pruritic_wheals",
        "quoted": [
            "крапивница",
            "зудящие пятна",
            "началось пару часов назад",
            "новый антибиотик"
        ],
        "context": {
            "chief_complaint": "hives pruritic",
            "onset": "few hours",
            "triggers": ["new antibiotic"],
            "negatives": ["no breathing difficulty"],
            "age": 27
        },
        "expected_levels": ["see GP in 24-48h"]
    },

    # --- PSYCH ---
    {
        "name": "32_panic_attack",
        "quoted": [
            "внезапная паника",
            "сердцебиение",
            "тремор",
            "страх умереть"
        ],
        "context": {
            "chief_complaint": "panic symptoms",
            "duration": "20 minutes",
            "age": 22,
            "negatives": ["no chest pain radiating", "no syncope"]
        },
        "expected_levels": ["see GP in 24-48h"]
    },
    {
        "name": "33_depression_anhedonia_sleep",
        "quoted": [
            "потеря интереса к любимым делам",
            "плохой сон",
            "усталость",
            "2 недели"
        ],
        "context": {
            "chief_complaint": "low mood",
            "duration": "2 weeks",
            "age": 35
        },
        "expected_levels": ["see GP in 24-48h"]
    },

    # --- HEME / ID / FEVER ---
    {
        "name": "34_fever_unknown_origin",
        "quoted": [
            "температура 38.2 держится 5 дней",
            "озноб",
            "боли нет",
            "кашля нет"
        ],
        "context": {
            "chief_complaint": "fever unknown origin",
            "duration": "5 days",
            "negatives": ["no cough", "no pain"],
            "age": 41
        },
        "expected_levels": ["see GP in 24-48h", "urgent care today"]
    },
    {
        "name": "35_meningitis_red_flags",
        "quoted": [
            "сильная головная боль",
            "скованность шеи",
            "температура 39.0",
            "вчера началось"
        ],
        "context": {
            "chief_complaint": "headache with neck stiffness and fever",
            "age": 19
        },
        "expected_levels": ["ED now"]
    },

    # --- PEDIATRICS ---
    {
        "name": "36_bronchiolitis_infant",
        "quoted": [
            "ребенок 8 месяцев",
            "свистящее дыхание",
            "затрудненное кормление",
            "началось вчера"
        ],
        "context": {
            "chief_complaint": "infant wheeze feeding difficulty",
            "age": 0,
            "sex": "male",
            "duration": "1 day"
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "37_croup_barking_cough",
        "quoted": [
            "лающий кашель",
            "осиплость голоса",
            "хуже ночью",
            "температура 37.6"
        ],
        "context": {
            "chief_complaint": "barking cough",
            "age": 3,
            "duration": "1 day"
        },
        "expected_levels": ["urgent care today", "see GP in 24-48h"]
    },
    {
        "name": "38_ear_foreign_body_child",
        "quoted": [
            "ребенок положил бусинку в ухо",
            "плач",
            "боль в ухе",
            "началось час назад"
        ],
        "context": {
            "chief_complaint": "foreign body in ear",
            "age": 4
        },
        "expected_levels": ["urgent care today"]
    },

    # --- TRAUMA / BURNS ---
    {
        "name": "39_head_injury_bleeding_nausea",
        "quoted": [
            "упал с велосипедом, ударился головой, идет кровь",
            "10 минут назад",
            "лоб, 7/10",
            "тошнота, один раз рвота"
        ],
        "context": {
            "chief_complaint": "head injury with bleeding",
            "onset": "10 minutes ago",
            "location": "forehead",
            "severity_0_10": 7,
            "associated_symptoms": ["nausea", "vomiting once"],
            "negatives": ["no loss of consciousness"],
            "age": 27,
            "sex": "male"
        },
        "expected_levels": ["ED now"]
    },
    {
        "name": "40_burn_partial_thickness_hand",
        "quoted": [
            "ошпарил руку кипятком",
            "пузырьки на коже",
            "сильная боль",
            "20 минут назад"
        ],
        "context": {
            "chief_complaint": "hand scald burn with blisters",
            "onset": "20 minutes ago",
            "age": 33
        },
        "expected_levels": ["urgent care today"]
    },

    # --- RENAL / STONE ---
    {
        "name": "41_nephrolithiasis_colicky_pain",
        "quoted": [
            "резкая волнообразная боль в боку",
            " irrad в пах",
            "тошнота",
            "нет температуры"
        ],
        "context": {
            "chief_complaint": "flank colicky pain",
            "negatives": ["no fever"],
            "age": 36,
            "sex": "male"
        },
        "expected_levels": ["urgent care today"]
    },

    # --- OPHTHALMO ---
    {
        "name": "42_conjunctivitis_purulent",
        "quoted": [
            "гнойные выделения из глаза",
            "склеиваются ресницы утром",
            "зуд",
            "началось вчера"
        ],
        "context": {
            "chief_complaint": "purulent conjunctivitis",
            "duration": "1 day",
            "negatives": ["no severe eye pain", "no photophobia"]
        },
        "expected_levels": ["see GP in 24-48h"]
    },
    {
        "name": "43_acute_angle_glaucoma",
        "quoted": [
            "сильная боль в глазу",
            "радужные круги при взгляде на свет",
            "тошнота",
            "внезапно"
        ],
        "context": {
            "chief_complaint": "acute eye pain and halos",
            "age": 62
        },
        "expected_levels": ["ED now"]
    },

    # --- ENT / THROAT ---
    {
        "name": "44_strep_pharyngitis",
        "quoted": [
            "сильная боль в горле",
            "температура 38.3",
            "гнойные налеты",
            "кашля нет"
        ],
        "context": {
            "chief_complaint": "sore throat",
            "associated_symptoms": ["fever 38.3", "tonsillar exudates"],
            "negatives": ["no cough"],
            "age": 19
        },
        "expected_levels": ["see GP in 24-48h", "urgent care today"]
    },
    {
        "name": "45_epiglottitis_red_flag",
        "quoted": [
            "сильная боль в горле",
            "трудно глотать, слюнотечение",
            "голос глухой",
            "высокая температура"
        ],
        "context": {
            "chief_complaint": "severe sore throat with drooling",
            "age": 6
        },
        "expected_levels": ["ED now"]
    },

    # --- HEPATO / JAUNDICE ---
    {
        "name": "46_hepatitis_jaundice_dark_urine",
        "quoted": [
            "желтушность кожи",
            "темная моча",
            "светлый стул",
            "слабость"
        ],
        "context": {
            "chief_complaint": "jaundice with dark urine",
            "age": 38
        },
        "expected_levels": ["urgent care today"]
    },

    # --- ONCO SYMPTOMS ---
    {
        "name": "47_unintentional_weight_loss_night_sweats",
        "quoted": [
            "похудел на 7 кг за 2 месяца",
            "ночные поты",
            "слабость",
            "аппетит снижен"
        ],
        "context": {
            "chief_complaint": "weight loss and night sweats",
            "duration": "2 months",
            "age": 52
        },
        "expected_levels": ["see GP in 24-48h", "urgent care today"]
    },

    # --- DVT / PE ---
    {
        "name": "48_dvt_unilateral_leg_swelling",
        "quoted": [
            "отек левой голени",
            "боль при надавливании",
            "после перелета",
            "покраснение"
        ],
        "context": {
            "chief_complaint": "unilateral leg swelling after flight",
            "age": 45
        },
        "expected_levels": ["urgent care today"]
    },
    {
        "name": "49_pulmonary_embolism_redflags",
        "quoted": [
            "внезапная одышка",
            "боль в груди при вдохе",
            "тревога",
            "недавно был перелом ноги"
        ],
        "context": {
            "chief_complaint": "sudden dyspnea with pleuritic pain",
            "age": 39
        },
        "expected_levels": ["ED now"]
    },

    # --- NEURO (EPILEPSY / SYNCOPE) ---
    {
        "name": "50_first_time_seizure",
        "quoted": [
            "впервые судороги на глазах у друзей",
            "прикус языка",
            "сонливость после",
            "алкоголь накануне"
        ],
        "context": {
            "chief_complaint": "first seizure",
            "age": 21,
            "negatives": ["no head injury"]
        },
        "expected_levels": ["ED now", "urgent care today"]
    },
    {
        "name": "51_syncope_vasovagal",
        "quoted": [
            "потемнело в глазах",
            "упал в душном помещении",
            "быстро пришел в себя",
            "тошноты нет"
        ],
        "context": {
            "chief_complaint": "fainting",
            "age": 23
        },
        "expected_levels": ["see GP in 24-48h"]
    },

    # --- NEPHRO / EDEMA ---
    {
        "name": "52_nephrotic_syndrome_edema_foam_urine",
        "quoted": [
            "отеки на ногах и вокруг глаз",
            "пенистая моча",
            "прибавка веса",
            "неделю"
        ],
        "context": {
            "chief_complaint": "edema with foamy urine",
            "duration": "1 week",
            "age": 36
        },
        "expected_levels": ["urgent care today"]
    },

    # --- SKIN / ALLERGY / ANAPHYLAXIS EDGE ---
    {
        "name": "53_anaphylaxis_peanut",
        "quoted": [
            "сыпь",
            "распухли губы",
            "тяжело дышать",
            "через 10 минут после арахиса"
        ],
        "context": {
            "chief_complaint": "posible anaphylaxis",
            "onset": "15 minutes",
            "age": 18,
            "negatives": ["no meds taken"]
        },
        "expected_levels": ["ED now"]
    },

    # --- OB/GYN NON-PREGNANT ---
    {
        "name": "54_dysmenorrhea_cramps",
        "quoted": [
            "сильные спазмы при месячных",
            "тошнота",
            "лучше с грелкой",
            "3/10 сейчас"
        ],
        "context": {
            "chief_complaint": "period cramps",
            "sex": "female",
            "age": 22
        },
        "expected_levels": ["self-care", "see GP in 24-48h"]
    },
    {
        "name": "55_pcos_irregular_periods_hirsutism",
        "quoted": [
            "нерегулярные месячные",
            "повышенный рост волос",
            "прибавка веса",
            "угри"
        ],
        "context": {
            "chief_complaint": "possible PCOS",
            "sex": "female",
            "age": 25
        },
        "expected_levels": ["see GP in 24-48h"]
    },

    # --- ORTHO ---
    {
        "name": "56_shoulder_dislocation_history",
        "quoted": [
            "упал на вытянутую руку",
            "плечо деформировано",
            "не могу поднять",
            "сильная боль"
        ],
        "context": {
            "chief_complaint": "shoulder trauma",
            "age": 28,
            "negatives": ["no open wound"]
        },
        "expected_levels": ["urgent care today"]
    },

    # --- TOX / POISON ---
    {
        "name": "57_food_poisoning_diarrhea",
        "quoted": [
            "тошнота и понос",
            "рвота два раза",
            "началось после ресторана",
            "температура 37.7"
        ],
        "context": {
            "chief_complaint": "acute gastroenteritis",
            "duration": "12h",
            "age": 30
        },
        "expected_levels": ["see GP in 24-48h"]
    },
    {
        "name": "58_alcohol_intoxication",
        "quoted": [
            "головная боль после вечеринки",
            "тошнота",
            "сухость во рту",
            "озноб"
        ],
        "context": {
            "chief_complaint": "hangover",
            "age": 27
        },
        "expected_levels": ["self-care"]
    },

    # --- VASCULAR ---
    {
        "name": "59_aortic_dissection_redflags",
        "quoted": [
            "внезапная разрывающая боль в груди",
            "отдает в спину",
            "холодный пот",
            "головокружение"
        ],
        "context": {
            "chief_complaint": "tearing chest pain radiating to back",
            "age": 60
        },
        "expected_levels": ["ED now"]
    },

    # --- MISC / GENERAL ---
    {
        "name": "60_lymphadenopathy_persistent",
        "quoted": [
            "увеличенные лимфоузлы на шее",
            "2 недели",
            "боли нет",
            "температуры нет"
        ],
        "context": {
            "chief_complaint": "neck lymph nodes enlarged",
            "duration": "2 weeks",
            "negatives": ["no pain", "no fever"],
            "age": 29
        },
        "expected_levels": ["see GP in 24-48h"]
    },
]
