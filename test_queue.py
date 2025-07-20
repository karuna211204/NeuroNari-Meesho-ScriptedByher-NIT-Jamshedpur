import logging
from mcp_server import (
    AppointmentRequest, save_appointment_to_excel,
    SmsNotifyRequest, send_sms_notification,
    HealthRecordRequest, generate_pdf_record
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🧪 Test patient data
patients = [
    {
        "name": "Rajesh Mehta",
        "id": "P004",
        "age": 72,
        "gender": "Male",
        "phone": "+919812345678",
        "issue": "Chest discomfort and fatigue",
        "time": "10:30 AM",
        "symptoms": "Chest tightness, shortness of breath",
        "duration": "3 days",
        "chronic": "Hypertension, Diabetes",
        "family": "Father had heart disease",
        "diagnosis": "Angina",
        "prescriptions": "Nitroglycerin, Aspirin, Atorvastatin"
    },
    {
        "name": "Aarav Nair",
        "id": "P005",
        "age": 8,
        "gender": "Male",
        "phone": "+919898765432",
        "issue": "Fever and sore throat",
        "time": "11:00 AM",
        "symptoms": "High fever, sore throat, mild cough",
        "duration": "2 days",
        "chronic": "None",
        "family": "Allergies in family",
        "diagnosis": "Viral Pharyngitis",
        "prescriptions": "Paracetamol syrup, Warm saline gargles"
    },
    {
        "name": "Nisha Verma",
        "id": "P006",
        "age": 29,
        "gender": "Female",
        "phone": "+919933221100",
        "issue": "Severe headache and light sensitivity",
        "time": "03:45 PM",
        "symptoms": "Pulsating headache, photophobia",
        "duration": "6 hours",
        "chronic": "History of migraines",
        "family": "Mother has migraines",
        "diagnosis": "Migraine without aura",
        "prescriptions": "Sumatriptan 50mg, Rest in dark room"
    },
    {
        "name": "Ankita Sharma",
        "id": "P007",
        "age": 32,
        "gender": "Female",
        "phone": "+919977889900",
        "issue": "Routine prenatal check-up",
        "time": "09:00 AM",
        "symptoms": "No major symptoms",
        "duration": "N/A",
        "chronic": "None",
        "family": "No genetic disorders",
        "diagnosis": "Normal pregnancy - 2nd trimester",
        "prescriptions": "Iron and folic acid supplements"
    },
    {
        "name": "Mohammed Iqbal",
        "id": "P008",
        "age": 41,
        "gender": "Male",
        "phone": "+919900112233",
        "issue": "Fever after returning from travel",
        "time": "06:15 PM",
        "symptoms": "Fever, fatigue, mild chills",
        "duration": "4 days",
        "chronic": "None",
        "family": "No relevant history",
        "diagnosis": "Suspected Dengue",
        "prescriptions": "Paracetamol, Hydration, Blood test recommended"
    }
]

# 🔧 Run all tools for a patient
def run_all_tools(patient):
    logger.info(f"\n--- 🧪 Testing Tools for: {patient['name']} ---")

    # Tool 1: Appointment
    appointment_req = AppointmentRequest(
        patient_name=patient["name"],
        patient_id=patient["id"],
        age=patient["age"],
        gender=patient["gender"],
        phone_number=patient["phone"],
        issue=patient["issue"],
        appointment_time=patient["time"]
    )
    appt_result = save_appointment_to_excel(appointment_req)
    logger.info(f"📅 Appointment Saved: {appt_result}")

    # Tool 2: SMS Notification
    sms_req = SmsNotifyRequest(
        phone_number=patient["phone"],
        patient_name=patient["name"],
        appointment_time=patient["time"]
    )
    sms_result = send_sms_notification(sms_req)
    logger.info(f"📲 SMS Sent: {sms_result}")

    # Tool 3: Health Report PDF
    pdf_req = HealthRecordRequest(
        patient_name=patient["name"],
        age=patient["age"],
        gender=patient["gender"],
        phone_number=patient["phone"],
        symptoms=patient["symptoms"],
        duration=patient["duration"],
        chronic_conditions=patient["chronic"],
        family_history=patient["family"],
        diagnosis=patient["diagnosis"],
        prescriptions=patient["prescriptions"]
    )
    pdf_result = generate_pdf_record(pdf_req)
    logger.info(f"📄 PDF Generated: {pdf_result}")

# 🚀 Run all tests
if __name__ == "__main__":
    logger.info("🔁 Starting tool tests for multiple patients...\n")
    for p in patients:
        run_all_tools(p)
    logger.info("\n✅ All patient test cases completed.")
