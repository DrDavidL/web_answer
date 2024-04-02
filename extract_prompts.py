prefix = """You generate realistic and complex progress notes for patients with cancer. You include made up names, ages, and MRNs for patients. 
You include made up dates for the notes. You include made up names for the providers. You include made up names for the hospitals. You include details
about the patient's cancer diagnosis, treatment, and response to treatment. You include details about the patient's symptoms and side effects. You include
details about the patient's other medical diagnoses, medications, and allergies. You include details about the patient's family history. You include details
about the patient's social history. You include details about the patient's physical exam. You include details about the patient's vital signs. You include
details about the patient's lab results. You include details about the patient's imaging results. You include details about the patient's procedures. You include
details about the patient's hospital course. You include details about the patient's discharge plan. You include details about the patient's follow up plan. You
include details about the patient's prognosis. You include details about the patient's goals of care. You include details about the patient's advance directives.
You include details about the patient's code status. You include details about the patient's mental status. You include details about the patient's functional
status. You include details about the patient's social support."""

sample_prompt = "Generate a progress note for a patient with lung cancer."

sample_response = """Patient Name: John Doe

MRN: 123456

Date of Visit: 01/15/2023

Provider Name: Dr. Jane Smith

Hospital: St. Mary's Hospital

Chief Complaint: Fatigue and shortness of breath.

History of Present Illness: Mr. Doe is a 65-year-old male with a known diagnosis of stage IIIA non-small cell lung cancer. He has been undergoing treatment with carboplatin and paclitaxel. He reports increased fatigue and shortness of breath over the past week. He also reports occasional bouts of nausea and vomiting, likely side effects of the chemotherapy. His last CT scan showed a partial response to the treatment.

Past Medical History: Hypertension, type 2 diabetes.

Medications: Lisinopril 10mg daily, Metformin 500mg twice daily, Ondansetron as needed for nausea.

Allergies: No known drug allergies.

Family History: Father died of lung cancer at age 75. Mother has hypertension.

Social History: Retired engineer. Smoked 1 pack of cigarettes daily for 30 years, quit 10 years ago. Drinks alcohol socially.

Physical Examination:

General: Alert and oriented, appears fatigued.
Cardiovascular: Regular rhythm, no murmurs.
Respiratory: Decreased breath sounds in the right lower lobe.
Abdomen: Soft, non-tender.
Vital Signs: BP 130/80, HR 80, RR 18, Temp 98.6°F, SpO2 92% on room air.

Lab Results: CBC shows mild anemia, likely due to chemotherapy. Liver function tests are within normal limits.

Imaging Results: Last CT scan showed a 30% reduction in the size of the primary lung tumor.

Procedures: Patient underwent bronchoscopy for biopsy, which confirmed the diagnosis of non-small cell lung cancer.

Hospital Course: Patient was admitted for shortness of breath. He was treated with supplemental oxygen and his symptoms improved.

Discharge Plan: Patient to continue with the current chemotherapy regimen. Prescribe oral iron supplement for anemia.

Follow Up Plan: Follow up in the clinic in 2 weeks. Repeat CT scan in 6 weeks to assess response to therapy.

Prognosis: Given the partial response to treatment, the prognosis is cautiously optimistic.

Goals of Care: The patient's goal is to control symptoms and prolong life. He understands the side effects of chemotherapy and is willing to continue treatment.

Advance Directives: Patient has a living will and has appointed his daughter as his healthcare proxy.

Code Status: Full code.

Mental Status: Patient is alert and oriented to person, place, and time. No signs of depression or anxiety.

Functional Status: Patient is independent in activities of daily living.

Social Support: Patient lives with his wife and has a supportive family."""

complex = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "patientInformation": {
      "type": "object",
      "properties": {
        "patientID": {
          "type": "string"
        },
        "dateOfBirth": {
          "type": "string",
          "format": "date"
        },
        "gender": {
          "type": "string"
        },
        "ethnicity": {
          "type": "string"
        },
        "smokingStatus": {
          "type": "string"
        },
        "familyHistory": {
          "type": "string"
        }
      },
      "required": ["patientID", "dateOfBirth", "gender"]
    },
    "cancerDiagnosis": {
      "type": "object",
      "properties": {
        "diagnosisDate": {
          "type": "string",
          "format": "date"
        },
        "cancerType": {
          "type": "string"
        },
        "cancerStage": {
          "type": "string"
        },
        "histology": {
          "type": "string"
        },
        "primarySite": {
          "type": "string"
        },
        "metastasisSites": {
          "type": "string"
        },
        "biomarkers": {
          "type": "string"
        },
        "geneticMutations": {
          "type": "string"
        }
      },
      "required": ["diagnosisDate", "cancerType", "cancerStage", "histology", "primarySite"]
    },
    "treatmentInformation": {
      "type": "object",
      "properties": {
        "treatmentType": {
          "type": "string"
        },
        "treatmentStartDate": {
          "type": "string",
          "format": "date"
        },
        "treatmentEndDate": {
          "type": "string",
          "format": "date"
        },
        "treatmentResponse": {
          "type": "string"
        },
        "sideEffects": {
          "type": "string"
        }
      },
      "required": ["treatmentType", "treatmentStartDate", "treatmentEndDate", "treatmentResponse"]
    },
    "followUpInformation": {
      "type": "object",
      "properties": {
        "lastFollowUpDate": {
          "type": "string",
          "format": "date"
        },
        "currentStatus": {
          "type": "string"
        },
        "recurrenceInformation": {
          "type": "string"
        },
        "survivalInformation": {
          "type": "string"
        }
      },
      "required": ["lastFollowUpDate", "currentStatus"]
    }
  },
  "required": ["patientInformation", "cancerDiagnosis", "treatmentInformation", "followUpInformation"]
}
"""

system_prompt = """
**# Comprehensive Oncology History and Physical Exam Note Information Extraction 🩺**
Engage Oncological Entity and Finding Identification Procedures and initiate Structured Data Extraction Techniques.
Activate JSON Structure Generation Strategies for clear and consistent representation of oncology history and exam findings.
[Comprehensive Oncology History and Physical Exam Note Information Extraction 🩺
  {
     Oncological Entity and Finding Identification Procedures 🔍 [🩺, 📝] ∴
     Structured Data Extraction Techniques 🗃️ [🧬, 📊] ∴
     JSON Structure Generation Strategies 🚀 [🏗️, 📈]
  }
  ≈>
  [Data Accuracy Assurance 🎯 ∴ Proper Medical Terminology and Value Enforcement ⚕️]
  ⊃
  Clear and Consistent Oncology History and Exam Findings Representation 📊
     {
        **Oncology Note Preprocessing and Segmentation**
           [Preprocess the oncology note, removing noise and segmenting it into relevant sections (e.g., history, physical exam, assessment, and plan)]
        **Oncological Entity and Finding Recognition**
           [Identify the main oncological entities, findings, and assessments mentioned in the note using medical NLP techniques]
        **Structured Data Extraction**
           [Extract the relevant information for each identified oncological entity and finding, such as cancer type, stage, histology, treatment, and response]
        **JSON Object Population**
           [Populate the predefined JSON structure with the extracted oncological data, ensuring proper data type formatting and consistency]
        **Data Accuracy Verification**
           [Verify the accuracy and completeness of the populated JSON object against the original oncology note]
        **Missing Data Handling**
           [Handle missing or optional data by using default values, null placeholders, or omitting the corresponding JSON properties]
        **JSON Structure Validation**
           [Validate the populated JSON object against the predefined JSON schema to ensure consistency and adherence to the expected structure]
        **Output Generation**
           [Generate the final JSON output representing the extracted oncology history and exam findings, adhering to the predefined structure and schema]
     }]

**# Predefined JSON Schema**

json 

{
  "patientInfo": {
    "name": "string",
    "age": "number",
    "gender": "string",
    "dateOfVisit": "string"
  },
  "chiefComplaint": "string",
  "historyOfPresentIllness": {
    "onset": "string",
    "duration": "string",
    "severity": "string",
    "linkedSymptoms": [
      "string"
    ],
    "aggravatingFactors": [
      "string"
    ],
    "alleviatingFactors": [
      "string"
    ]
  },
  "pastMedicalHistory": [
    "string"
  ],
  "medications": [
    "string"
  ],
  "allergies": [
    "string"
  ],
  "familyHistory": [
    "string"
  ],
  "socialHistory": {
    "smoking": "string",
    "alcohol": "string",
    "occupation": "string"
  },
  "reviewOfSystems": {
    "constitutional": [
      "string"
    ],
    "heent": [
      "string"
    ],
    "cardiovascular": [
      "string"
    ],
    "respiratory": [
      "string"
    ],
    "gastrointestinal": [
      "string"
    ],
    "genitourinary": [
      "string"
    ],
    "musculoskeletal": [
      "string"
    ],
    "integumentary": [
      "string"
    ],
    "neurological": [
      "string"
    ],
    "psychiatric": [
      "string"
    ],
    "endocrine": [
      "string"
    ],
    "hematologic": [
      "string"
    ],
    "immunologic": [
      "string"
    ]
  },
  "physicalExam": {
    "vitalSigns": {
      "bloodPressure": {
        "value": "string",
        "unit": "string"
      },
      "heartRate": {
        "value": "number",
        "unit": "string"
      },
      "respiratoryRate": {
        "value": "number",
        "unit": "string"
      },
      "temperature": {
        "value": "number",
        "unit": "string"
      }
    },
    "generalAppearance": "string",
    "heent": {
      "head": "string",
      "eyes": "string",
      "ears": "string",
      "nose": "string",
      "throat": "string"
    },
    "neck": "string",
    "cardiovascular": "string",
    "respiratory": "string",
    "gastrointestinal": "string",
    "genitourinary": "string",
    "musculoskeletal": "string",
    "integumentary": "string",
    "lymphNodes": "string",
    "neurological": "string",
    "psychiatric": "string"
  },
  "cancerDiagnosis": {
    "cancerType": "string",
    "cancerStage": "string",
    "histology": "string",
    "primarySite": "string",
    "metastasisSites": [
      "string"
    ],
    "biomarkers": [
      "string"
    ],
    "geneticMutations": [
      "string"
    ]
  },
  "treatment": {
    "surgeries": [
      "string"
    ],
    "chemotherapy": [
      "string"
    ],
    "radiationTherapy": [
      "string"
    ],
    "targetedTherapy": [
      "string"
    ],
    "immunotherapy": [
      "string"
    ],
    "hormonalTherapy": [
      "string"
    ],
    "clinicalTrials": [
      "string"
    ]
  },
  "assessment": [
    "string"
  ],
  "plan": [
    "string"
  ]
}

"""

oncology_note = """Generate a comprehensive oncology H&P note with the diagnosis supplied. Include pseudonyms and use content that matches that an experienced oncologist can understand and prefer to use. Be sure to include a comprehensive assessment and plan that addresses the diagnosis and any results."""