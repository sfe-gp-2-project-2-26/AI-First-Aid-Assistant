from enum import Enum

class FirstAidTopic(str, Enum):
    # General
    GENERAL_APPROACH = "general_approach"
    PSYCHOLOGICAL_FIRST_AID = "psychological_first_aid"
    HAND_HYGIENE = "hand_hygiene"
    OXYGEN_ADMINISTRATION = "oxygen_administration"
    
    # Resuscitation
    UNRESPONSIVE_BREATHING = "unresponsive_and_breathing_normally"
    CPR_ADULT = "unresponsive_abnormal_breathing_adult"
    CPR_CHILD = "unresponsive_abnormal_breathing_child"
    AED = "defibrillator_aed"
    OPIOID_OVERDOSE = "opioid_overdose"
    DROWNING = "drowning"
    
    # Breathing
    BREATHING_DIFFICULTIES = "breathing_difficulties"
    CHOKING = "choking"
    ASTHMA_ATTACK = "asthma_attack"
    CROUP = "croup"
    
    # Trauma
    SEVERE_BLEEDING = "severe_bleeding"
    CHEST_ABDOMEN_INJURIES = "chest_and_abdomen_injuries"
    AMPUTATION = "amputation"
    CUTS_AND_GRAZES = "cuts_and_grazes"
    DENTAL_AVULSION = "dental_avulsion"
    FRICTION_BLISTERS = "friction_blisters"
    BURNS = "burns"
    FLASH_EYE = "flash_eye"
    FRACTURES_SPRAINS_STRAINS = "fractures_sprains_strains"
    SPINAL_INJURY = "spinal_injury"
    HEAD_INJURY_CONCUSSION = "head_injury_and_concussion"
    LOWER_BACK_PAIN = "acute_lower_back_pain"
    MAMMAL_BITES = "mammal_bites"
    INSECT_BITES_STINGS = "insect_bites_or_stings"
    AQUATIC_ANIMAL_INJURIES = "aquatic_animal_injuries"
    SNAKEBITES = "snakebites"
    POISONING = "poisoning"
    NOSEBLEEDS = "nosebleeds"
    
    # Medical Conditions
    CHEST_PAIN_CARDIAC = "chest_pain_cardiac"
    STROKE = "stroke"
    ALLERGIC_REACTION_ANAPHYLAXIS = "allergic_reaction_and_anaphylaxis"
    SHOCK = "shock"
    DIABETIC_EMERGENCY = "diabetic_emergency_hypoglycemia"
    SEIZURE = "seizure"
    FEELING_FAINT = "feeling_faint"
    FEVER = "fever"
    ABDOMINAL_PAIN = "abdominal_pain"
    EMERGENCY_CHILDBIRTH = "emergency_childbirth"
    SORE_THROAT = "sore_throat"
    EARACHE = "earache"
    HEADACHE = "headache"
    HICCUPS = "hiccups"
    
    # Environmental
    HYPERTHERMIA = "hyperthermia"
    DEHYDRATION = "dehydration"
    HYPOTHERMIA = "hypothermia"
    FROSTBITE = "frostbite"
    ALTITUDE_SICKNESS = "altitude_sickness"
    DECOMPRESSION_ILLNESS = "decompression_illness"
    MOTION_SICKNESS = "motion_sickness"
    
    # Mental Distress
    TRAUMATIC_EVENT = "traumatic_event"
    SUICIDAL_IDEATION = "suicidal_ideation"
    ACUTE_GRIEF = "acute_grief"
    ANXIETY_AND_PANIC = "anxiety_and_panic"
    
    # Education & Context
    FIRST_AID_EDUCATION = "first_aid_education"
    
    # Out of Scope
    OUT_OF_SCOPE = "out_of_scope"

