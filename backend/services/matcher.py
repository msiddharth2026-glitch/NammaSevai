from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from ..models.scheme import Scheme
from ..models.condition import EligibilityCondition
from ..schemas.assistant import ExtractedUserProfile, PotentialSchemeMatch
from ..schemas.document import RequiredDocumentResponse
from ..schemas.step import ApplicationStepResponse

class SchemeMatcherService:
    """
    Evaluates structured eligibility conditions for government schemes
    against an extracted citizen profile without making unfounded assumptions.
    """

    def evaluate_condition(
        self, 
        condition: EligibilityCondition, 
        profile: ExtractedUserProfile
    ) -> Tuple[bool, bool, str, str]:
        """
        Returns:
            (is_known, is_passed, explanation_en, explanation_ta)
        """
        f = condition.field_name
        op = condition.operator
        val = condition.expected_value

        # Age evaluation
        if f in ("age", "age_min", "age_max"):
            if profile.age is None:
                return False, False, f"Age requirement ({op} {val}) needs verification", f"வயது நிபந்தனை ({val}) சரிபார்க்கப்பட வேண்டும்"
            try:
                req_age = int(val)
                if op == "gte" or f == "age_min":
                    passed = profile.age >= req_age
                elif op == "lte" or f == "age_max":
                    passed = profile.age <= req_age
                elif op == "gt":
                    passed = profile.age > req_age
                elif op == "lt":
                    passed = profile.age < req_age
                else:
                    passed = profile.age == req_age
                return True, passed, f"Age {profile.age} meets {val} condition", f"வயது {profile.age} நிபந்தனை பூர்த்தி செய்கிறது"
            except (ValueError, TypeError):
                pass

        # Gender evaluation
        if f == "gender":
            if not profile.gender:
                return False, False, f"Gender ({val}) condition needs verification", f"பாலின நிபந்தனை ({val}) சரிபார்க்கப்பட வேண்டும்"
            passed = profile.gender.lower() == str(val).lower()
            return True, passed, f"Gender matches ({val})", f"பாலினம் ({val}) பொருந்துகிறது"

        # Income ceiling / annual income
        if f in ("income_max", "annual_income"):
            if profile.annual_income is None:
                return False, False, f"Family annual income ceiling of ₹{float(val):,.0f} needs confirmation", f"குடும்ப ஆண்டு வருமான வரம்பு ₹{float(val):,.0f} சரிபார்க்கப்பட வேண்டும்"
            try:
                req_inc = float(val)
                if op in ("lte", "le") or f == "income_max":
                    passed = profile.annual_income <= req_inc
                elif op in ("gte", "ge"):
                    passed = profile.annual_income >= req_inc
                elif op == "lt":
                    passed = profile.annual_income < req_inc
                else:
                    passed = profile.annual_income <= req_inc
                return True, passed, f"Annual income ₹{profile.annual_income:,.0f} is within ₹{req_inc:,.0f} ceiling", f"ஆண்டு வருமானம் ₹{profile.annual_income:,.0f} அனுமதிக்கப்பட்ட வரம்பான ₹{req_inc:,.0f}-க்குள் உள்ளது"
            except (ValueError, TypeError):
                pass

        # Government school education requirement
        if f == "school_type":
            if not profile.school_type:
                return False, False, "Government school study (Classes 6-12) status needs confirmation", "அரசுப் பள்ளியில் (6-12 வகுப்பு) படித்த விவரம் சரிபார்க்கப்பட வேண்டும்"
            passed = profile.school_type.lower() == "government"
            return True, passed, "Studied in Government School", "அரசுப் பள்ளியில் பயின்ற விவரம் பொருந்துகிறது"

        # Occupation requirement
        if f == "occupation":
            if not profile.occupation:
                return False, False, f"Occupation ({val}) needs verification", f"தொழில் ({val}) சரிபார்க்கப்பட வேண்டும்"
            if op == "in" or "," in str(val):
                allowed = [x.strip().lower() for x in str(val).split(",")]
                passed = any(a in profile.occupation.lower() or profile.occupation.lower() in a for a in allowed)
            else:
                passed = profile.occupation.lower() == str(val).lower()
            return True, passed, f"Occupation matches ({val})", f"தொழில் ({val}) பொருந்துகிறது"

        # Landholding max acres
        if f == "land_max_acres":
            req_acres = float(val)
            if profile.landholding_acres is None:
                return False, False, f"Landholding size (under {req_acres} acres) needs confirmation", f"நில அளவு ({req_acres} ஏக்கருக்குள்) சரிபார்க்கப்பட வேண்டும்"
            passed = profile.landholding_acres <= req_acres
            return True, passed, f"Landholding of {profile.landholding_acres} acres is within limit", f"நில அளவு {profile.landholding_acres} ஏக்கர் வரம்பிற்குள் உள்ளது"

        # Tailoring training
        if f == "has_tailoring_training":
            if profile.has_tailoring_training is None:
                return False, False, "Tailoring certificate status needs verification", "தையல் பயிற்சி சான்றிதழ் விவரம் தேவைப்படுகிறது"
            passed = bool(profile.has_tailoring_training)
            return True, passed, "Has tailoring training", "தையல் பயிற்சி சான்றிதழ் உள்ளது"

        # Community category (SC/ST)
        if f in ("community", "community_category"):
            if not profile.community_category:
                return False, False, f"Community category ({val}) needs voluntary verification", f"சமூகப் பிரிவு ({val}) சரிபார்க்கப்பட வேண்டும்"
            passed = str(val).lower() in profile.community_category.lower()
            return True, passed, f"Community matches {val}", f"சமூகப் பிரிவு {val} பொருந்துகிறது"

        # Disability status
        if f == "disability":
            if profile.disability_status is None:
                return False, False, "Disability / UDID status needs voluntary verification", "மாற்றுத்திறனாளி / UDID சான்றிதழ் சரிபார்க்கப்பட வேண்டும்"
            passed = bool(profile.disability_status)
            return True, passed, "Disability criteria met", "மாற்றுத்திறனாளி தகுதி பொருந்துகிறது"

        # Default fallback for custom flags
        return False, False, f"{condition.description_en} requires manual verification", f"{condition.description_ta} சரிபார்க்கப்பட வேண்டும்"

    def match_schemes(
        self, 
        db: Session, 
        profile: ExtractedUserProfile, 
        category: str = None
    ) -> Tuple[List[PotentialSchemeMatch], List[str], List[str]]:
        query = db.query(Scheme).filter(Scheme.is_active == True)
        if category and category != "all":
            query = query.filter(Scheme.category == category)
        
        all_schemes = query.all()
        potential_matches: List[PotentialSchemeMatch] = []
        follow_ups_en = set()
        follow_ups_ta = set()

        for scheme in all_schemes:
            conditions = scheme.conditions or []
            fulfilled = []
            unverified = []
            violated = []

            for cond in conditions:
                is_known, is_passed, msg_en, msg_ta = self.evaluate_condition(cond, profile)
                if is_known:
                    if is_passed:
                        fulfilled.append(msg_en)
                    else:
                        violated.append(cond.description_en)
                else:
                    unverified.append(cond.description_en)
                    if cond.prompt_question_en:
                        follow_ups_en.add(cond.prompt_question_en)
                    if cond.prompt_question_ta:
                        follow_ups_ta.add(cond.prompt_question_ta)

            # If any mandatory condition is explicitly violated, citizen is not eligible
            if len(violated) > 0:
                continue

            total_conds = len(conditions)
            if total_conds == 0:
                confidence = 50.0
                status = "potential_match"
            else:
                passed_ratio = len(fulfilled) / total_conds
                confidence = round(passed_ratio * 60.0 + 35.0, 1)  # between 35% and 95%
                if len(unverified) == 0:
                    status = "high_potential"
                    confidence = 96.0
                elif len(fulfilled) > 0:
                    status = "potential_match"
                else:
                    status = "conditional"

            # Formulate clear explanations
            if len(fulfilled) > 0:
                explanation_en = f"Potential match based on: {'; '.join(fulfilled)}. Note: {len(unverified)} condition(s) still require official verification."
                explanation_ta = f"பொருந்தும் தகுதிகள்: {'; '.join(fulfilled)}. கவனிக்க: {len(unverified)} நிபந்தனைகள் அதிகாரப்பூர்வமாக சரிபார்க்கப்பட வேண்டும்."
                explanation_hi = f"संभावित पात्रता आधार: {'; '.join(fulfilled)}। ध्यान दें: {len(unverified)} शर्तों का आधिकारिक सत्यापन आवश्यक है।"
                explanation_ml = f"സാധ്യതയുള്ള യോഗ്യതാ മാനദണ്ഡങ്ങൾ: {'; '.join(fulfilled)}. ശ്രദ്ധിക്കുക: {len(unverified)} വ്യവസ്ഥകൾ ഔദ്യോഗികമായി പരിശോധിക്കേണ്ടതുണ്ട്."
            else:
                explanation_en = f"Potential scheme in your area of interest. Mandatory criteria ({len(unverified)}) need verification."
                explanation_ta = f"உங்கள் துறைக்கு சாத்தியமான திட்டம். இதற்குரிய {len(unverified)} தகுதி நிபந்தனைகள் சரிபார்க்கப்பட வேண்டும்."
                explanation_hi = f"आपकी रुचि से संबंधित संभावित योजना। अनिवार्य पात्रता शर्तें ({len(unverified)}) सत्यापित की जानी चाहिए।"
                explanation_ml = f"നിങ്ങളുടെ മേഖലയിലെ സാധ്യതയുള്ള പദ്ധതി. ഇതിലെ {len(unverified)} യോഗ്യതാ മാനദണ്ഡങ്ങൾ പരിശോധിക്കേണ്ടതുണ്ട്."

            # Source & coverage details
            src = scheme.source
            source_url = src.portal_url if src else "https://www.tn.gov.in"
            source_name = src.source_name if src else "Government Portal"
            verified_date = src.verified_date if src else "2026-10-15"
            coverage = "Central Government / Centrally Sponsored" if any(k in scheme.id for k in ["pm-", "pmegp", "nsp-"]) else "State Government (Tamil Nadu)"

            # Serialize documents and steps
            docs_res = [RequiredDocumentResponse.model_validate(d) for d in (scheme.documents or [])]
            steps_res = [ApplicationStepResponse.model_validate(s) for s in (scheme.steps or [])]

            potential_matches.append(PotentialSchemeMatch(
                scheme_id=scheme.id,
                scheme_name_en=scheme.name,
                scheme_name_ta=scheme.name_ta,
                scheme_name_hi=getattr(scheme, "name_hi", None) or scheme.name_ta,
                scheme_name_ml=getattr(scheme, "name_ml", None) or scheme.name_ta,
                department_en=scheme.department,
                department_ta=scheme.department_ta,
                department_hi=getattr(scheme, "department_hi", None) or scheme.department,
                department_ml=getattr(scheme, "department_ml", None) or scheme.department,
                category=scheme.category,
                coverage_type=coverage,
                application_url=source_url,
                benefit_amount=scheme.benefit_amount,
                benefit_summary_en=scheme.benefit_summary,
                benefit_summary_ta=scheme.benefit_summary_ta,
                benefit_summary_hi=getattr(scheme, "benefit_summary_hi", None) or scheme.benefit_summary,
                benefit_summary_ml=getattr(scheme, "benefit_summary_ml", None) or scheme.benefit_summary,
                match_status=status,
                match_confidence=confidence,
                eligibility_explanation_en=explanation_en,
                eligibility_explanation_ta=explanation_ta,
                eligibility_explanation_hi=explanation_hi,
                eligibility_explanation_ml=explanation_ml,
                fulfilled_conditions=fulfilled,
                unverified_conditions=unverified,
                required_documents=docs_res,
                application_steps=steps_res,
                official_portal_url=source_url,
                official_source_name=source_name,
                verified_date=verified_date
            ))

        # Sort matches by high potential status then confidence descending
        potential_matches.sort(key=lambda x: (x.match_status == "high_potential", x.match_confidence), reverse=True)

        return potential_matches, list(follow_ups_en), list(follow_ups_ta)
