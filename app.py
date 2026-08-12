"""PHASE2-BUILD AI AGENT"""

LOG_PATH = "risk_assessment_log.csv"
CRISIS_LINE = "US: 988 (call/text) | Intl directory: https://www.iasp.info/resources/Crisis_Centres/"

def risk_tier(prob):
    if prob >= 0.75:
        return "High"
    elif prob >= 0.40:
        return "Medium"
    else:
        return "Low"

def recommendation(tier):
    if tier == "High":
        return ("Strong linguistic risk indicators detected. Flag for immediate human review "
                "by a counselor/crisis-response team. Do not rely on automated response alone.")
    elif tier == "Medium":
        return ("Some risk indicators present. Recommend follow-up check-in from a trained "
                "moderator/counselor and continued monitoring.")
    else:
        return "No strong risk indicators detected in this text. Routine monitoring only."

def _log_columns():
    return ["timestamp", "user_id", "text_snippet", "risk_probability", "risk_tier", "alert_generated"]

def _append_log(record):
    row = pd.DataFrame([record], columns=_log_columns())
    try:
        existing = pd.read_csv(LOG_PATH)
        pd.concat([existing, row], ignore_index=True).to_csv(LOG_PATH, index=False)
    except FileNotFoundError:
        row.to_csv(LOG_PATH, index=False)

class SuicideRiskAgent:
    def __init__(self, model, vectorizer):
        self.model = model
        self.vectorizer = vectorizer

    def _predict_proba(self, cleaned_text):
        X = self.vectorizer.transform([cleaned_text])
        if hasattr(self.model, "predict_proba"):
            return float(self.model.predict_proba(X)[0][1])
        return float(self.model.predict(X)[0])

    def analyze(self, text, user_id="anonymous", log=True):
        cleaned = clean_text(text)
        prob = self._predict_proba(cleaned)
        tier = risk_tier(prob)
        alert = tier in ("Medium", "High")

        result = {
            "user_id": user_id, "text": text,
            "risk_probability": round(prob, 4),
            "risk_tier": tier, "alert_generated": alert,
        }

        if log:
            _append_log({
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "text_snippet": text[:120],
                "risk_probability": result["risk_probability"],
                "risk_tier": tier,
                "alert_generated": alert,
            })
        return result

    def report(self, text, user_id="anonymous", log=True):
        res = self.analyze(text, user_id=user_id, log=log)
        print("=" * 50)
        print("SUICIDE RISK ASSESSMENT REPORT")
        print("=" * 50)
        print("Inputs:")
        print(f"  - User ID: {res['user_id']}")
        print(f"  - Timestamp: {datetime.utcnow().isoformat()}")
        print(f"  - Text: \"{res['text'][:100]}{'...' if len(res['text']) > 100 else ''}\"")
        print()
        print("Predictions:")
        print(f"  - Risk Probability: {res['risk_probability']*100:.2f}%")
        print(f"  - Risk Tier: {res['risk_tier']}")
        print(f"  - Alert Generated: {'YES' if res['alert_generated'] else 'No'}")
        print()
        print("Recommendation:")
        print(f"  {recommendation(res['risk_tier'])}")
        if res['alert_generated']:
            print()
            print(f"  Crisis resources: {CRISIS_LINE}")
        print("=" * 50)
        return res

agent = SuicideRiskAgent(best_model, tfidf)

agent.report(
    "I feel so alone lately, nothing seems to matter anymore and I don't see the point in continuing.",
    user_id="user_042"
)

sample_texts = [
    "I got promoted at work today and I'm celebrating with friends tonight!",
    "Just finished a great workout, feeling energized for the week ahead.",
    "i need helpjust help me im crying so hard",
]
for t in sample_texts:
    agent.report(t, user_id="demo_user")
    print()

records = pd.read_csv(LOG_PATH)
records

user_text = input("Enter the text to assess: ")
user_id = input("Enter user ID (or press Enter for 'anonymous'): ") or "anonymous"

agent.report(user_text, user_id=user_id)

#@title Suicide Risk Assessment { run: "auto" }
User_ID = "user_069" #@param {type:"string"}
Text_to_Assess = "breakup,loverfailure,my lover is reject mee " #@param {type:"string"}

agent.report(Text_to_Assess, user_id=User_ID)

while True:
    user_text = input("\nEnter text to assess (or type 'exit' to stop): ")
    if user_text.strip().lower() == "exit":
        break
    user_id = input("User ID (Enter for 'anonymous'): ") or "anonymous"
    agent.report(user_text, user_id=user_id)
