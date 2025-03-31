"""
Assessment scales for different animal species.

Each scale is defined as a dict with:
- title: The name of the scale
- description: Brief explanation of what the scale measures
- questions: List of assessment items, each with:
  - question: The text of the question
  - options: List of possible answers with associated scores
  - guidance: (optional) Additional information to help the user
- interpretation: Rules for interpreting the total score
"""

ASSESSMENT_SCALES = {
    "Rat": {
        "Body Condition Score": {
            "title": "Rat Body Condition Score (BCS)",
            "description": "Evaluates body fat and muscle mass on a 1-5 scale",
            "questions": [
                {
                    "question": "Visible bone structure",
                    "options": [
                        {"text": "Prominent, easily visible backbone and hipbones", "score": 1},
                        {"text": "Bones visible but not prominent", "score": 2},
                        {"text": "Bones palpable but not visible", "score": 3},
                        {"text": "Bones palpable with firm pressure only", "score": 4},
                        {"text": "Bones difficult to palpate under fat", "score": 5}
                    ],
                    "guidance": "Observe the rat from above and feel along the spine and hip bones"
                },
                {
                    "question": "Muscle mass",
                    "options": [
                        {"text": "Severely reduced muscle", "score": 1},
                        {"text": "Reduced muscle mass", "score": 2},
                        {"text": "Optimal muscle mass", "score": 3},
                        {"text": "Slightly excessive fat over muscle", "score": 4},
                        {"text": "Excessive fat obscuring muscle definition", "score": 5}
                    ],
                    "guidance": "Feel the muscles over the back and hind legs"
                },
                {
                    "question": "Fat deposits",
                    "options": [
                        {"text": "No palpable fat", "score": 1},
                        {"text": "Minimal fat", "score": 2},
                        {"text": "Moderate fat coverage", "score": 3},
                        {"text": "Abundant fat deposits", "score": 4},
                        {"text": "Excessive fat throughout", "score": 5}
                    ],
                    "guidance": "Check for fat deposits around the abdomen and inguinal area"
                }
            ],
            "interpretation": [
                {"range": [3, 4], "text": "Ideal body condition", "color": "green"},
                {"range": [5, 7], "text": "Slightly overweight", "color": "orange"},
                {"range": [8, 15], "text": "Obese", "color": "red"},
                {"range": [2, 2], "text": "Slightly underweight", "color": "orange"},
                {"range": [0, 1], "text": "Emaciated", "color": "red"}
            ]
        },
        "Grimace Scale": {
            "title": "Rat Grimace Scale (RGS)",
            "description": "Assesses pain by facial expressions on a 0-2 scale for each feature",
            "questions": [
                {
                    "question": "Orbital tightening",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Evaluate partial or complete eye closure"
                },
                {
                    "question": "Nose/cheek flattening",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Look for loss of bulge above the whisker pads"
                },
                {
                    "question": "Ear changes",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Observe ear fold, tightening, and separation"
                },
                {
                    "question": "Whisker change",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Check if whiskers are clumped, forward pointing or backward swept"
                }
            ],
            "interpretation": [
                {"range": [0, 1], "text": "No pain apparent", "color": "green"},
                {"range": [2, 4], "text": "Mild pain", "color": "yellow"},
                {"range": [5, 6], "text": "Moderate pain", "color": "orange"},
                {"range": [7, 8], "text": "Severe pain", "color": "red"}
            ]
        },
        "Activity Score": {
            "title": "Rat Activity Score",
            "description": "Evaluates general activity level and behavior",
            "questions": [
                {
                    "question": "Movement in cage",
                    "options": [
                        {"text": "No movement/severely restricted", "score": 0},
                        {"text": "Limited movement", "score": 1},
                        {"text": "Normal movement", "score": 2},
                        {"text": "Hyperactive movement", "score": 1}
                    ],
                    "guidance": "Observe spontaneous movement for 3-5 minutes"
                },
                {
                    "question": "Response to handling",
                    "options": [
                        {"text": "No response/severely decreased", "score": 0},
                        {"text": "Reduced response", "score": 1},
                        {"text": "Normal response", "score": 2},
                        {"text": "Exaggerated/aggressive response", "score": 1}
                    ],
                    "guidance": "Note the animal's reaction when approached and lifted"
                },
                {
                    "question": "Grooming behavior",
                    "options": [
                        {"text": "No grooming observed", "score": 0},
                        {"text": "Minimal grooming", "score": 1},
                        {"text": "Normal grooming", "score": 2},
                        {"text": "Excessive/abnormal grooming", "score": 1}
                    ],
                    "guidance": "Watch for time spent grooming and grooming pattern"
                }
            ],
            "interpretation": [
                {"range": [0, 2], "text": "Severely reduced activity - urgent attention required", "color": "red"},
                {"range": [3, 4], "text": "Reduced activity - monitor closely", "color": "orange"},
                {"range": [5, 6], "text": "Normal activity", "color": "green"},
                {"range": [5, 6], "text": "Normal activity", "color": "green"},
                {"range": [3, 4], "text": "Abnormal activity - monitor closely", "color": "orange"}
            ]
        }
    },
    "Mouse": {
        "Mouse Grimace Scale": {
            "title": "Mouse Grimace Scale (MGS)",
            "description": "Assesses pain by facial expressions on a 0-2 scale for each feature",
            "questions": [
                {
                    "question": "Orbital tightening",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Evaluate eye closure, eyelid squeezing"
                },
                {
                    "question": "Nose bulge",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Look for bulge formation on bridge of nose"
                },
                {
                    "question": "Cheek bulge",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Observe bulge formation on cheek"
                },
                {
                    "question": "Ear position",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Check for ear rotation and separation from head"
                },
                {
                    "question": "Whisker change",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Observe whisker position and movement"
                }
            ],
            "interpretation": [
                {"range": [0, 2], "text": "No pain apparent", "color": "green"},
                {"range": [3, 5], "text": "Mild pain", "color": "yellow"},
                {"range": [6, 8], "text": "Moderate pain", "color": "orange"},
                {"range": [9, 10], "text": "Severe pain", "color": "red"}
            ]
        },
        "BCS Mouse": {
            "title": "Mouse Body Condition Score",
            "description": "Evaluates body fat and muscle mass on a 1-5 scale",
            "questions": [
                {
                    "question": "Overall body condition",
                    "options": [
                        {"text": "Emaciated - severe muscle wasting, prominent bones", "score": 1},
                        {"text": "Underweight - segmentation of vertebral column visible", "score": 2},
                        {"text": "Optimal - smooth and rounded appearance", "score": 3},
                        {"text": "Overweight - segmentation of vertebral column palpable with firm pressure", "score": 4},
                        {"text": "Obese - bones difficult to palpate, mouse has obese appearance", "score": 5}
                    ],
                    "guidance": "Evaluate by looking at mouse from behind and feeling spine and tail base"
                }
            ],
            "interpretation": [
                {"range": [3, 3], "text": "Ideal body condition", "color": "green"},
                {"range": [4, 4], "text": "Overweight", "color": "orange"},
                {"range": [5, 5], "text": "Obese", "color": "red"},
                {"range": [2, 2], "text": "Underweight", "color": "orange"},
                {"range": [1, 1], "text": "Emaciated", "color": "red"}
            ]
        },
        "Activity Level": {
            "title": "Mouse Activity Level Assessment",
            "description": "Evaluates general behavior and activity",
            "questions": [
                {
                    "question": "Activity level",
                    "options": [
                        {"text": "Inactive, unresponsive", "score": 0},
                        {"text": "Minimal movement, reduced responsiveness", "score": 1},
                        {"text": "Normal activity and responsiveness", "score": 2}
                    ],
                    "guidance": "Observe mouse for 3-5 minutes in home cage"
                },
                {
                    "question": "Posture",
                    "options": [
                        {"text": "Hunched, stationary", "score": 0},
                        {"text": "Mildly hunched, moving", "score": 1},
                        {"text": "Normal posture", "score": 2}
                    ],
                    "guidance": "Note posture during movement and rest"
                },
                {
                    "question": "Coat condition",
                    "options": [
                        {"text": "Rough, unkempt, piloerection", "score": 0},
                        {"text": "Slightly unkempt", "score": 1},
                        {"text": "Smooth, well-groomed coat", "score": 2}
                    ],
                    "guidance": "Examine fur condition and grooming status"
                }
            ],
            "interpretation": [
                {"range": [5, 6], "text": "Normal condition", "color": "green"},
                {"range": [3, 4], "text": "Mild concerns - monitor closely", "color": "yellow"},
                {"range": [1, 2], "text": "Moderate concerns - intervention advised", "color": "orange"},
                {"range": [0, 0], "text": "Severe concerns - immediate intervention required", "color": "red"}
            ]
        }
    },
    "Rabbit": {
        "Rabbit Grimace Scale": {
            "title": "Rabbit Grimace Scale (RbGS)",
            "description": "Assesses pain by facial expressions on a 0-2 scale for each feature",
            "questions": [
                {
                    "question": "Orbital tightening",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Evaluate partial/complete eye closure"
                },
                {
                    "question": "Cheek flattening",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Look for flattened cheeks and less defined cheek muscle"
                },
                {
                    "question": "Nostril shape",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Observe if nostrils are more tightly closed"
                },
                {
                    "question": "Whisker position",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Check if whiskers are pulled back or clumped together"
                },
                {
                    "question": "Ear position",
                    "options": [
                        {"text": "Not present", "score": 0},
                        {"text": "Moderately present", "score": 1},
                        {"text": "Obviously present", "score": 2}
                    ],
                    "guidance": "Observe if ears are folded, pressed back or rotated outwards"
                }
            ],
            "interpretation": [
                {"range": [0, 2], "text": "No pain apparent", "color": "green"},
                {"range": [3, 5], "text": "Mild pain", "color": "yellow"},
                {"range": [6, 8], "text": "Moderate pain", "color": "orange"},
                {"range": [9, 10], "text": "Severe pain", "color": "red"}
            ]
        },
        "Body Condition Score": {
            "title": "Rabbit Body Condition Score",
            "description": "Evaluates body fat and muscle mass on a 1-5 scale",
            "questions": [
                {
                    "question": "Body condition",
                    "options": [
                        {"text": "Emaciated - visible spine, ribs, and hipbones", "score": 1},
                        {"text": "Thin - easily palpable spine and ribs", "score": 2},
                        {"text": "Ideal - palpable spine and ribs with gentle pressure", "score": 3},
                        {"text": "Overweight - spine and ribs palpable with firm pressure", "score": 4},
                        {"text": "Obese - cannot feel spine or ribs even with firm pressure", "score": 5}
                    ],
                    "guidance": "Palpate the spine, ribs, and hip bones"
                }
            ],
            "interpretation": [
                {"range": [3, 3], "text": "Ideal body condition", "color": "green"},
                {"range": [4, 4], "text": "Overweight", "color": "orange"},
                {"range": [5, 5], "text": "Obese", "color": "red"},
                {"range": [2, 2], "text": "Underweight", "color": "orange"},
                {"range": [1, 1], "text": "Emaciated", "color": "red"}
            ]
        },
        "Wellness Score": {
            "title": "Rabbit Wellness Score",
            "description": "Evaluates general health and wellness",
            "questions": [
                {
                    "question": "Eating and drinking",
                    "options": [
                        {"text": "Not eating or drinking", "score": 0},
                        {"text": "Reduced eating or drinking", "score": 1},
                        {"text": "Normal eating and drinking", "score": 2}
                    ],
                    "guidance": "Check food and water consumption over 24 hours"
                },
                {
                    "question": "Fecal output",
                    "options": [
                        {"text": "No fecal pellets or diarrhea", "score": 0},
                        {"text": "Few, small or abnormal fecal pellets", "score": 1},
                        {"text": "Normal quantity and quality of fecal pellets", "score": 2}
                    ],
                    "guidance": "Evaluate quantity, size, and consistency of droppings"
                },
                {
                    "question": "Activity and mobility",
                    "options": [
                        {"text": "Immobile or reluctant to move", "score": 0},
                        {"text": "Reduced movement or abnormal gait", "score": 1},
                        {"text": "Normal movement and activity", "score": 2}
                    ],
                    "guidance": "Observe mobility in enclosure for 5 minutes"
                },
                {
                    "question": "Grooming",
                    "options": [
                        {"text": "No grooming, unkempt appearance", "score": 0},
                        {"text": "Limited grooming, patches of unkempt fur", "score": 1},
                        {"text": "Normal grooming, clean appearance", "score": 2}
                    ],
                    "guidance": "Examine coat condition and observe grooming behavior"
                }
            ],
            "interpretation": [
                {"range": [7, 8], "text": "Excellent wellness", "color": "green"},
                {"range": [5, 6], "text": "Good wellness - monitor", "color": "yellow"},
                {"range": [3, 4], "text": "Fair wellness - intervention advised", "color": "orange"},
                {"range": [0, 2], "text": "Poor wellness - urgent intervention required", "color": "red"}
            ]
        }
    },
    "Goat": {
        "FAMACHA Score": {
            "title": "FAMACHA© Anemia Score for Goats",
            "description": "Evaluates anemia based on lower eyelid membrane color",
            "questions": [
                {
                    "question": "Conjunctival mucous membrane color",
                    "options": [
                        {"text": "Red - optimal", "score": 1},
                        {"text": "Red-pink - acceptable", "score": 2},
                        {"text": "Pink - borderline", "score": 3},
                        {"text": "Pink-white - anemic", "score": 4},
                        {"text": "White - severely anemic", "score": 5}
                    ],
                    "guidance": "Pull down lower eyelid and compare color to FAMACHA chart"
                }
            ],
            "interpretation": [
                {"range": [1, 2], "text": "Non-anemic", "color": "green"},
                {"range": [3, 3], "text": "Borderline anemic - monitor closely", "color": "yellow"},
                {"range": [4, 4], "text": "Anemic - treatment recommended", "color": "orange"},
                {"range": [5, 5], "text": "Severely anemic - immediate treatment required", "color": "red"}
            ]
        },
        "Body Condition Score": {
            "title": "Goat Body Condition Score",
            "description": "Evaluates fat cover and muscle mass on a 1-5 scale",
            "questions": [
                {
                    "question": "Body condition",
                    "options": [
                        {"text": "Emaciated - severe muscle wasting, prominent bones (1)", "score": 1},
                        {"text": "Thin - minimal fat, prominent bones (2)", "score": 2},
                        {"text": "Good - moderate fat cover, palpable bones (3)", "score": 3},
                        {"text": "Fat - bones difficult to palpate (4)", "score": 4},
                        {"text": "Obese - bones not palpable under fat layer (5)", "score": 5}
                    ],
                    "guidance": "Palpate the spine, ribs, and loin area between the last rib and hip bone"
                }
            ],
            "interpretation": [
                {"range": [3, 3], "text": "Ideal body condition", "color": "green"},
                {"range": [4, 4], "text": "Overweight", "color": "orange"},
                {"range": [5, 5], "text": "Obese", "color": "red"},
                {"range": [2, 2], "text": "Thin", "color": "orange"},
                {"range": [1, 1], "text": "Emaciated", "color": "red"}
            ]
        },
        "Pain Scale": {
            "title": "Goat Pain Scale",
            "description": "Assesses pain through behavioral indicators",
            "questions": [
                {
                    "question": "Posture",
                    "options": [
                        {"text": "Normal posture, standing naturally", "score": 0},
                        {"text": "Slightly abnormal posture", "score": 1},
                        {"text": "Hunched posture, favoring painful area", "score": 2}
                    ],
                    "guidance": "Observe standing position and weight bearing"
                },
                {
                    "question": "Movement",
                    "options": [
                        {"text": "Normal gait", "score": 0},
                        {"text": "Mild lameness or gait change", "score": 1},
                        {"text": "Severe lameness or reluctance to move", "score": 2}
                    ],
                    "guidance": "Watch movement for 1-2 minutes"
                },
                {
                    "question": "Appetite",
                    "options": [
                        {"text": "Normal appetite", "score": 0},
                        {"text": "Reduced appetite", "score": 1},
                        {"text": "No interest in food", "score": 2}
                    ],
                    "guidance": "Check feed consumption and interest in feed when offered"
                },
                {
                    "question": "Response to palpation",
                    "options": [
                        {"text": "No response", "score": 0},
                        {"text": "Mild flinching or moving away", "score": 1},
                        {"text": "Strong reaction, vocalization", "score": 2}
                    ],
                    "guidance": "Gently palpate the area of concern"
                },
                {
                    "question": "Facial expression",
                    "options": [
                        {"text": "Normal, alert expression", "score": 0},
                        {"text": "Tense facial muscles, ears back", "score": 1},
                        {"text": "Obvious grimace, teeth grinding", "score": 2}
                    ],
                    "guidance": "Observe facial features, ear position, and jaw movement"
                }
            ],
            "interpretation": [
                {"range": [0, 2], "text": "Minimal pain", "color": "green"},
                {"range": [3, 5], "text": "Mild pain - monitor", "color": "yellow"},
                {"range": [6, 8], "text": "Moderate pain - treatment advised", "color": "orange"},
                {"range": [9, 10], "text": "Severe pain - immediate intervention", "color": "red"}
            ]
        }
    },
    "Sheep": {
        "FAMACHA Score": {
            "title": "FAMACHA© Anemia Score for Sheep",
            "description": "Evaluates anemia based on lower eyelid membrane color",
            "questions": [
                {
                    "question": "Conjunctival mucous membrane color",
                    "options": [
                        {"text": "Red - optimal", "score": 1},
                        {"text": "Red-pink - acceptable", "score": 2},
                        {"text": "Pink - borderline", "score": 3},
                        {"text": "Pink-white - anemic", "score": 4},
                        {"text": "White - severely anemic", "score": 5}
                    ],
                    "guidance": "Pull down lower eyelid and compare color to FAMACHA chart"
                }
            ],
            "interpretation": [
                {"range": [1, 2], "text": "Non-anemic", "color": "green"},
                {"range": [3, 3], "text": "Borderline anemic - monitor closely", "color": "yellow"},
                {"range": [4, 4], "text": "Anemic - treatment recommended", "color": "orange"},
                {"range": [5, 5], "text": "Severely anemic - immediate treatment required", "color": "red"}
            ]
        },
        "Body Condition Score": {
            "title": "Sheep Body Condition Score",
            "description": "Evaluates fat cover and muscle mass on a 1-5 scale",
            "questions": [
                {
                    "question": "Body condition",
                    "options": [
                        {"text": "Emaciated - vertebrae prominent and sharp (1)", "score": 1},
                        {"text": "Thin - vertebral processes can be felt (2)", "score": 2},
                        {"text": "Good - moderate fat cover, processes smooth (3)", "score": 3},
                        {"text": "Fat - processes difficult to feel (4)", "score": 4},
                        {"text": "Obese - processes cannot be felt (5)", "score": 5}
                    ],
                    "guidance": "Feel the spine (especially the lumbar region) and assess fat cover"
                }
            ],
            "interpretation": [
                {"range": [3, 3], "text": "Ideal body condition", "color": "green"},
                {"range": [4, 4], "text": "Overweight", "color": "orange"},
                {"range": [5, 5], "text": "Obese", "color": "red"},
                {"range": [2, 2], "text": "Thin", "color": "orange"},
                {"range": [1, 1], "text": "Emaciated", "color": "red"}
            ]
        },
        "Lameness Score": {
            "title": "Sheep Lameness Score",
            "description": "Evaluates degree of lameness on a 0-3 scale",
            "questions": [
                {
                    "question": "Gait assessment",
                    "options": [
                        {"text": "Normal gait (0)", "score": 0},
                        {"text": "Mildly lame, slightly abnormal gait (1)", "score": 1},
                        {"text": "Moderately lame, favoring one or more limbs (2)", "score": 2},
                        {"text": "Severely lame, minimal weight-bearing (3)", "score": 3}
                    ],
                    "guidance": "Observe the sheep walking on a flat surface for at least 10 steps"
                }
            ],
            "interpretation": [
                {"range": [0, 0], "text": "Not lame", "color": "green"},
                {"range": [1, 1], "text": "Mildly lame - monitor", "color": "yellow"},
                {"range": [2, 2], "text": "Moderately lame - treatment advised", "color": "orange"},
                {"range": [3, 3], "text": "Severely lame - immediate treatment required", "color": "red"}
            ]
        }
    },
    "Pig": {
        "Body Condition Score": {
            "title": "Pig Body Condition Score",
            "description": "Evaluates fat cover and condition on a 1-5 scale",
            "questions": [
                {
                    "question": "Body condition",
                    "options": [
                        {"text": "Emaciated - prominent backbone and hip bones (1)", "score": 1},
                        {"text": "Thin - easily felt bones with minimal pressure (2)", "score": 2},
                        {"text": "Ideal - bones felt with firm pressure (3)", "score": 3},
                        {"text": "Fat - cannot feel bones without very firm pressure (4)", "score": 4},
                        {"text": "Obese - cannot feel bones even with firm pressure (5)", "score": 5}
                    ],
                    "guidance": "Feel the backbone, ribs, and hip bones"
                }
            ],
            "interpretation": [
                {"range": [3, 3], "text": "Ideal body condition", "color": "green"},
                {"range": [4, 4], "text": "Overweight", "color": "orange"},
                {"range": [5, 5], "text": "Obese", "color": "red"},
                {"range": [2, 2], "text": "Thin", "color": "orange"},
                {"range": [1, 1], "text": "Emaciated", "color": "red"}
            ]
        },
        "Lameness Score": {
            "title": "Pig Lameness Score",
            "description": "Evaluates mobility on a 0-5 scale",
            "questions": [
                {
                    "question": "Gait and mobility assessment",
                    "options": [
                        {"text": "Normal gait (0)", "score": 0},
                        {"text": "Stiffness, slight abnormality (1)", "score": 1},
                        {"text": "Limping, lameness affecting one limb (2)", "score": 2},
                        {"text": "Severely lame, minimal weight-bearing on affected limb (3)", "score": 3},
                        {"text": "Very reluctant to move despite encouragement (4)", "score": 4},
                        {"text": "Does not move at all (5)", "score": 5}
                    ],
                    "guidance": "Observe the pig walking on a flat surface for at least 10 steps"
                }
            ],
            "interpretation": [
                {"range": [0, 0], "text": "Not lame", "color": "green"},
                {"range": [1, 1], "text": "Mildly lame - monitor", "color": "yellow"},
                {"range": [2, 2], "text": "Moderately lame - treatment advised", "color": "orange"},
                {"range": [3, 5], "text": "Severely lame - immediate treatment required", "color": "red"}
            ]
        },
        "Welfare Assessment": {
            "title": "Pig Welfare Assessment",
            "description": "Evaluates overall welfare status",
            "questions": [
                {
                    "question": "Body condition",
                    "options": [
                        {"text": "Poor body condition", "score": 0},
                        {"text": "Moderate body condition", "score": 1},
                        {"text": "Good body condition", "score": 2}
                    ],
                    "guidance": "Assess overall body condition score"
                },
                {
                    "question": "Skin lesions/wounds",
                    "options": [
                        {"text": "Multiple or severe wounds/lesions", "score": 0},
                        {"text": "Few minor lesions", "score": 1},
                        {"text": "No lesions", "score": 2}
                    ],
                    "guidance": "Check entire body for injuries, scratches, and wounds"
                },
                {
                    "question": "Cleanliness",
                    "options": [
                        {"text": "Very dirty (>50% of body)", "score": 0},
                        {"text": "Moderately dirty (10-50% of body)", "score": 1},
                        {"text": "Clean (<10% of body dirty)", "score": 2}
                    ],
                    "guidance": "Assess overall cleanliness of the animal"
                },
                {
                    "question": "Respiratory condition",
                    "options": [
                        {"text": "Labored breathing or coughing", "score": 0},
                        {"text": "Slight respiratory abnormality", "score": 1},
                        {"text": "Normal breathing", "score": 2}
                    ],
                    "guidance": "Observe breathing pattern and listen for coughing"
                },
                {
                    "question": "Behavior",
                    "options": [
                        {"text": "Abnormal/stereotypic behavior", "score": 0},
                        {"text": "Slightly abnormal behavior", "score": 1},
                        {"text": "Normal, species-typical behavior", "score": 2}
                    ],
                    "guidance": "Watch for tail/ear biting, aggression, apathy, or stereotypies"
                }
            ],
            "interpretation": [
                {"range": [8, 10], "text": "Good welfare", "color": "green"},
                {"range": [5, 7], "text": "Moderate welfare concerns - monitor", "color": "yellow"},
                {"range": [3, 4], "text": "Significant welfare concerns - intervention needed", "color": "orange"},
                {"range": [0, 2], "text": "Severe welfare concerns - immediate action required", "color": "red"}
            ]
        }
    }
}