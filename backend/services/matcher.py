from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session, joinedload, selectinload
from ..models.scheme import Scheme
from ..models.condition import EligibilityCondition
from ..schemas.assistant import ExtractedUserProfile, PotentialSchemeMatch
from ..schemas.document import RequiredDocumentResponse
from ..schemas.step import ApplicationStepResponse

class SchemeMatcherService:
    """
    Evaluates structured eligibility conditions for government schemes
    against an extracted citizen profile without making unfounded assumptions.
    Guarantees:
      - 100% State isolation (No cross-state recommendation leakage)
      - Mandatory criteria compliance (Income ceilings, age boundaries, gender, landholding)
      - Transparent explainability and categorization
      - Zero AI hallucination dependence (Rule engine is authoritative)
    """

    OFFICIAL_DISCLAIMER = (
        "Official Disclaimer: Matching indicates potential eligibility based on verified rules. "
        "It does not constitute government approval. Final eligibility and benefit disbursement "
        "are subject to verification of original documents by the implementing department."
    )

    def evaluate_condition(
        self, 
        condition: EligibilityCondition, 
        profile: ExtractedUserProfile
    ) -> Tuple[bool, bool, str, str]:
        """
        Returns:
            (is_known, is_passed, explanation_en, explanation_ta)
        """
        f = (condition.field_name or "").strip()
        op = (condition.operator or "eq").strip()
        val = str(condition.expected_value or "").strip()

        # 1. Age evaluation
        if f in ("age", "age_min", "age_max"):
            if profile.age is None:
                return False, False, f"Age requirement ({op} {val}) needs verification", f"வயது நிபந்தனை ({val}) சரிபார்க்கப்பட வேண்டும்"
            try:
                # Validate realistic age bounds
                if profile.age < 0 or profile.age > 120:
                    return True, False, f"Age {profile.age} is outside realistic boundaries", f"வயது {profile.age} சாத்தியமற்றது"

                req_age = int(val)
                if op in ("gte", "ge") or f == "age_min":
                    passed = profile.age >= req_age
                elif op in ("lte", "le") or f == "age_max":
                    passed = profile.age <= req_age
                elif op == "gt":
                    passed = profile.age > req_age
                elif op == "lt":
                    passed = profile.age < req_age
                else:
                    passed = profile.age == req_age
                
                if passed:
                    return True, True, f"Age {profile.age} meets requirement ({op} {val})", f"வயது {profile.age} நிபந்தனை பூர்த்தி செய்கிறது"
                else:
                    return True, False, f"Age {profile.age} does not satisfy required {op} {val}", f"வயது {profile.age} தேவையான {val} நிபந்தனையை பூர்த்தி செய்யவில்லை"
            except (ValueError, TypeError):
                pass

        # 2. Gender evaluation
        if f == "gender":
            if not profile.gender:
                return False, False, f"Gender ({val}) condition needs verification", f"பாலின நிபந்தனை ({val}) சரிபார்க்கப்பட வேண்டும்"
            if op == "in" or "," in val:
                allowed = [x.strip().lower() for x in val.split(",")]
                passed = profile.gender.lower() in allowed
                if not passed and profile.community_category:
                    c_com = profile.community_category.lower()
                    if any(x in allowed for x in ["sc", "st"]) and ("sc" in c_com or "st" in c_com):
                        passed = True
            else:
                passed = profile.gender.lower() == val.lower() or val.lower() in ("all", "any")
            
            if passed:
                return True, True, f"Gender / eligibility criteria matches ({val})", f"பாலினம் / தகுதிப் பிரிவு ({val}) பொருந்துகிறது"
            else:
                return True, False, f"Gender mismatch: Scheme requires {val}, profile is {profile.gender}", f"பாலின முரண்பாடு: தேவை {val}, விவரம் {profile.gender}"

        # 3. Income ceiling / annual income (covers income, annual_income, income_max, family_income)
        if f in ("income_max", "annual_income", "income", "family_income"):
            if profile.annual_income is None:
                return False, False, f"Family annual income ceiling of ₹{float(val):,.0f} needs confirmation", f"குடும்ப ஆண்டு வருமான வரம்பு ₹{float(val):,.0f} சரிபார்க்கப்பட வேண்டும்"
            try:
                if profile.annual_income < 0:
                    return True, False, "Negative income declared (invalid input)", "தவறான வருமான விவரம்"

                req_inc = float(val)
                if op in ("gte", "ge"):
                    passed = profile.annual_income >= req_inc
                elif op == "lt":
                    passed = profile.annual_income < req_inc
                elif op in ("gt"):
                    passed = profile.annual_income > req_inc
                else:  # default for income ceilings is <= req_inc
                    passed = profile.annual_income <= req_inc

                if passed:
                    return True, True, f"Annual income ₹{profile.annual_income:,.0f} satisfies limit ₹{req_inc:,.0f}", f"ஆண்டு வருமானம் ₹{profile.annual_income:,.0f} அனுமதிக்கப்பட்ட வரம்பான ₹{req_inc:,.0f}-க்குள் உள்ளது"
                else:
                    return True, False, f"Annual income ₹{profile.annual_income:,.0f} exceeds ceiling of ₹{req_inc:,.0f}", f"ஆண்டு வருமானம் ₹{profile.annual_income:,.0f} அனுமதிக்கப்பட்ட வரம்பைவிட அதிகம்"
            except (ValueError, TypeError):
                pass

        # 4. Education level
        if f in ("education", "education_level"):
            if not profile.education_level:
                return False, False, f"Educational qualification ({val}) requires verification", f"கல்வித் தகுதி ({val}) சரிபார்க்கப்பட வேண்டும்"
            
            allowed = [x.strip().lower() for x in val.split(",")]
            c_edu = profile.education_level.lower()
            
            # Semantic aliases
            edu_synonyms = {
                "graduate": ["college", "college_ug", "degree", "graduate", "bachelor"],
                "college": ["college", "college_ug", "degree", "graduate"],
                "12th": ["12th", "school_12th", "intermediate", "10+2", "+2", "plus_two"],
                "10th": ["10th", "school_10th", "matric", "sslc"],
                "iti": ["iti", "industrial_training"],
                "diploma": ["diploma", "polytechnic"],
                "5th": ["5th", "primary", "class_5"]
            }
            
            passed = any(c_edu == a for a in allowed)
            if not passed:
                for base_key, synonyms in edu_synonyms.items():
                    if any(s in c_edu for s in synonyms) and any(a in synonyms or a == base_key for a in allowed):
                        passed = True
                        break

            if passed:
                return True, True, f"Education qualification matches requirement ({c_edu})", f"கல்வித் தகுதி ({c_edu}) பொருந்துகிறது"
            else:
                return True, False, f"Education qualification {c_edu} does not meet scheme requirements ({val})", f"கல்வித் தகுதி ({c_edu}) திட்ட நிபந்தனையுடன் பொருந்தவில்லை"

        # 5. Government school education requirement
        if f == "school_type":
            if not profile.school_type:
                return False, False, "Government school study (Classes 6-12) status needs confirmation", "அரசுப் பள்ளியில் (6-12 வகுப்பு) படித்த விவரம் சரிபார்க்கப்பட வேண்டும்"
            passed = profile.school_type.lower() == val.lower() or (val.lower() == "government" and profile.school_type.lower() == "government")
            if passed:
                return True, True, "Studied in Government School", "அரசுப் பள்ளியில் பயின்ற விவரம் பொருந்துகிறது"
            else:
                return True, False, f"School type is {profile.school_type}, scheme requires {val}", f"பள்ளி வகை: {profile.school_type}, தேவை {val}"

        # 6. Occupation requirement
        if f == "occupation":
            if not profile.occupation:
                return False, False, f"Occupation ({val}) needs verification", f"தொழில் ({val}) சரிபார்க்கப்பட வேண்டும்"
            if op == "in" or "," in val:
                allowed = [x.strip().lower() for x in val.split(",")]
                passed = any(a in profile.occupation.lower() or profile.occupation.lower() in a for a in allowed)
            else:
                passed = profile.occupation.lower() == val.lower() or val.lower() in profile.occupation.lower()
            
            if passed:
                return True, True, f"Occupation matches ({val})", f"தொழில் ({val}) பொருந்துகிறது"
            else:
                return True, False, f"Occupation {profile.occupation} does not match required {val}", f"தொழில் {profile.occupation} தேவையான {val} உடன் பொருந்தவில்லை"

        # 7. Student status
        if f in ("is_student", "student_status"):
            if profile.is_student is None and profile.occupation != "student":
                return False, False, "Student enrollment needs verification", "மாணவர் சேர்க்கை சரிபார்க்கப்பட வேண்டும்"
            passed = (profile.is_student is True) or (profile.occupation == "student")
            if passed:
                return True, True, "Student enrollment verified", "மாணவர் சேர்க்கை தகுதி பொருந்துகிறது"
            else:
                return True, False, "Not enrolled as student", "மாணவர் சேர்க்கை இல்லை"

        # 8. Farmer status
        if f in ("is_farmer", "farmer_status"):
            if profile.is_farmer is None and profile.occupation != "farmer":
                return False, False, "Farmer status needs verification", "விவசாயி தகுதி சரிபார்க்கப்பட வேண்டும்"
            passed = (profile.is_farmer is True) or (profile.occupation == "farmer")
            if passed:
                return True, True, "Farmer status verified", "விவசாயி தகுதி பொருந்துகிறது"
            else:
                return True, False, "Not a farmer", "விவசாயி தகுதி பொருந்தவில்லை"

        # 9. Landholding max acres
        if f in ("land_max_acres", "land_acres", "landholding_acres"):
            try:
                req_acres = float(val)
                if profile.landholding_acres is None:
                    return False, False, f"Landholding size (under {req_acres} acres) needs confirmation", f"நில அளவு ({req_acres} ஏக்கருக்குள்) சரிபார்க்கப்பட வேண்டும்"
                passed = profile.landholding_acres <= req_acres
                if passed:
                    return True, True, f"Landholding of {profile.landholding_acres} acres is within limit ({req_acres} acres)", f"நில அளவு {profile.landholding_acres} ஏக்கர் வரம்பிற்குள் உள்ளது"
                else:
                    return True, False, f"Landholding {profile.landholding_acres} acres exceeds maximum limit of {req_acres} acres", f"நில அளவு {profile.landholding_acres} ஏக்கர் வரம்பைவிட அதிகம்"
            except (ValueError, TypeError):
                pass

        # 10. Tailoring training
        if f == "has_tailoring_training":
            if profile.has_tailoring_training is None:
                return False, False, "Tailoring certificate status needs verification", "தையல் பயிற்சி சான்றிதழ் விவரம் தேவைப்படுகிறது"
            passed = bool(profile.has_tailoring_training)
            if passed:
                return True, True, "Has tailoring training certification", "தையல் பயிற்சி சான்றிதழ் உள்ளது"
            else:
                return True, False, "Tailoring training certificate required", "தையல் பயிற்சி சான்றிதழ் இல்லை"

        # 11. Community category (SC/ST/OBC/BC)
        if f in ("community", "community_category"):
            if not profile.community_category:
                return False, False, f"Community category ({val}) needs voluntary verification", f"சமூகப் பிரிவு ({val}) சரிபார்க்கப்பட வேண்டும்"
            allowed = [x.strip().lower() for x in val.split(",")]
            passed = any(a in profile.community_category.lower() or profile.community_category.lower() in a for a in allowed)
            if passed:
                return True, True, f"Community matches ({val})", f"சமூகப் பிரிவு ({val}) பொருந்துகிறது"
            else:
                return True, False, f"Community category {profile.community_category} does not match {val}", f"சமூகப் பிரிவு {profile.community_category} திட்டத்துடன் பொருந்தவில்லை"

        # 12. Disability status
        if f == "disability":
            if profile.disability_status is None:
                return False, False, "Disability / UDID status needs voluntary verification", "மாற்றுத்திறனாளி / UDID சான்றிதழ் சரிபார்க்கப்பட வேண்டும்"
            passed = bool(profile.disability_status)
            if passed:
                return True, True, "Disability criteria met (UDID)", "மாற்றுத்திறனாளி தகுதி பொருந்துகிறது"
            else:
                return True, False, "Scheme requires verified disability / UDID", "மாற்றுத்திறனாளி சான்றிதழ் தேவை"

        # 13. State / Domicile requirement
        if f in ("state", "residence_state", "domicile"):
            if not profile.state:
                return False, False, f"Residency in {val} needs verification", f"{val} மாநில குடியுரிமை சரிபார்க்கப்பட வேண்டும்"
            passed = profile.state.strip().lower() == val.strip().lower()
            if passed:
                return True, True, f"Resident of {val}", f"{val} குடியுரிமை பொருந்துகிறது"
            else:
                return True, False, f"State mismatch: Resident of {profile.state}, scheme exclusive to {val}", f"மாநில முரண்பாடு: இருப்பிடம் {profile.state}, தேவை {val}"

        # 14. Residence / Housing type (e.g. solar rooftop, pucca, rural)
        if f in ("residence_type", "housing_type", "residence"):
            if not profile.residence_type:
                return False, False, f"Residential property / roof ownership ({val}) needs verification", f"குடியிருப்பு நிலை ({val}) சரிபார்க்கப்பட வேண்டும்"
            allowed = [x.strip().lower() for x in val.split(",")]
            c_res = profile.residence_type.strip().lower()
            passed = any(a in c_res or c_res in a for a in allowed)
            if passed:
                return True, True, f"Residence type matches ({c_res})", f"குடியிருப்பு நிலை பொருந்துகிறது ({c_res})"
            else:
                return True, False, f"Residence type {c_res} does not meet scheme conditions ({val})", f"குடியிருப்பு நிலை {c_res} திட்ட நிபந்தனையை பூர்த்தி செய்யவில்லை"

        # 15. Ration card type (BPL, PHH, AAY)
        if f in ("ration_card_type", "ration_card"):
            if not profile.ration_card_type:
                return False, False, f"Ration card category ({val}) needs verification", f"ரேஷன் அட்டை வகை ({val}) சரிபார்க்கப்பட வேண்டும்"
            allowed = [x.strip().lower() for x in val.split(",")]
            c_rc = profile.ration_card_type.strip().lower()
            passed = any(a in c_rc or c_rc in a for a in allowed)
            if passed:
                return True, True, f"Ration card matches ({c_rc})", f"ரேஷன் அட்டை பொருந்துகிறது ({c_rc})"
            else:
                return True, False, f"Ration card {c_rc} does not meet scheme criteria ({val})", f"ரேஷன் அட்டை {c_rc} திட்டத்திற்கு பொருந்தவில்லை"

        # 16. Maternity / Pregnancy
        if f == "is_pregnant_or_lactating":
            if profile.is_pregnant_or_lactating is None:
                return False, False, "Maternity / pregnancy status needs verification", "கர்ப்பிணி / பாலூட்டும் தாய் நிலை சரிபார்க்கப்பட வேண்டும்"
            expected_bool = (val.lower() == "true")
            passed = bool(profile.is_pregnant_or_lactating) == expected_bool
            if passed:
                return True, True, "Maternity criteria met", "கர்ப்பிணி / பாலூட்டும் தாய் நிலை பொருந்துகிறது"
            else:
                return True, False, "Scheme requires pregnant or lactating mother status", "கர்ப்பிணி நிலை தேவை"

        # 17. Marital status / Widow / Destitute
        if f in ("is_widow_or_destitute", "marital_status"):
            if profile.is_widow_or_destitute is None and not profile.marital_status:
                return False, False, f"Marital status ({val}) needs verification", f"திருமண நிலை ({val}) சரிபார்க்கப்பட வேண்டும்"
            if val.lower() == "widow":
                passed = bool(profile.is_widow_or_destitute) or (profile.marital_status and profile.marital_status.lower() in ("widow", "destitute"))
            elif val.lower() == "unmarried":
                passed = profile.marital_status and profile.marital_status.lower() == "unmarried"
            elif val.lower() == "married":
                passed = profile.marital_status and profile.marital_status.lower() == "married"
            else:
                passed = profile.marital_status and profile.marital_status.lower() == val.lower()
            
            if passed:
                return True, True, f"Marital status matches ({val})", f"திருமண நிலை பொருந்துகிறது ({val})"
            else:
                return True, False, f"Marital status does not match {val}", f"திருமண நிலை பொருந்தவில்லை"

        # Default fallback for custom flags
        return False, False, f"{condition.description_en} requires manual verification", f"{condition.description_ta} சரிபார்க்கப்பட வேண்டும்"

    def evaluate_scheme_for_profile(
        self, 
        scheme: Scheme, 
        profile: ExtractedUserProfile
    ) -> PotentialSchemeMatch:
        """
        Evaluates a single scheme against a citizen profile.
        Returns a complete PotentialSchemeMatch including match status,
        recommendation category, satisfied conditions, unverified conditions,
        and unfulfilled (violated) conditions.
        """
        citizen_state = (profile.state.strip()) if (profile.state and profile.state.strip()) else None
        scheme_level = getattr(scheme, "level", None) or "State"
        scheme_state = (getattr(scheme, "state", None) or "All India").strip()

        is_central = (scheme_level == "Central") or (scheme_state.lower() == "all india") or any(k in scheme.id for k in ["pm-", "pmegp", "nsp-"])
        is_state_unconfirmed = False
        state_violation = None

        if not is_central:
            if citizen_state:
                if scheme_state and citizen_state.lower() != scheme_state.lower():
                    state_violation = f"State residency mismatch: Scheme exclusive to residents of {scheme_state}, but citizen is in {citizen_state}."
            else:
                is_state_unconfirmed = True

        conditions = scheme.conditions or []
        fulfilled: List[str] = []
        unverified: List[str] = []
        violated: List[str] = []
        missing_fields: List[str] = []

        if state_violation:
            violated.append(state_violation)

        for cond in conditions:
            is_known, is_passed, msg_en, msg_ta = self.evaluate_condition(cond, profile)
            if is_known:
                if is_passed:
                    fulfilled.append(msg_en)
                else:
                    violated.append(f"{cond.description_en} ({msg_en})")
            else:
                unverified.append(cond.description_en)
                missing_fields.append(cond.field_name)

        if is_state_unconfirmed:
            missing_fields.append("state")

        # Determine Recommendation Category & Match Status
        src = scheme.source
        v_status = getattr(src, "verification_status", "verified") if src else "verified"

        total_conds = len(conditions)

        if len(violated) > 0:
            rec_category = "not_eligible"
            match_status = "not_eligible"
            confidence = 0.0
            explanation_en = f"Not eligible based on mandatory criteria: {'; '.join(violated)}."
            explanation_ta = f"கட்டாய நிபந்தனைகள் பூர்த்தி செய்யப்படாததால் தகுதி இல்லை: {'; '.join(violated)}."
            explanation_hi = f"अनिवार्य पात्रता शर्तों के आधार पर पात्र नहीं: {'; '.join(violated)}।"
            explanation_ml = f"നിർബന്ധിത മാനദണ്ഡങ്ങൾ പാലിക്കാത്തതിനാൽ യോഗ്യതയില്ല: {'; '.join(violated)}."
        elif v_status in ("needs_review", "source_unavailable"):
            rec_category = "administrative_review"
            match_status = "conditional"
            confidence = 45.0
            explanation_en = f"Scheme information requiring administrative review. Matched criteria: {'; '.join(fulfilled) if fulfilled else 'None'}."
            explanation_ta = f"நிர்வாக மறுஆய்வு தேவைப்படும் திட்டம். பொருந்தும் நிபந்தனைகள்: {'; '.join(fulfilled) if fulfilled else 'எதுவுமில்லை'}."
            explanation_hi = f"योजना की जानकारी की प्रशासनिक समीक्षा आवश्यक है। मिले मानदंड: {'; '.join(fulfilled) if fulfilled else 'कोई नहीं'}।"
            explanation_ml = f"പദ്ധതി വിവരങ്ങൾക്ക് ഭരണപരമായ പുനരവലോകനം ആവശ്യമാണ്. പൊരുത്തപ്പെടുന്ന മാനദണ്ഡങ്ങൾ: {'; '.join(fulfilled) if fulfilled else 'ഒന്നുമില്ല'}."
        elif len(unverified) == 0 and len(fulfilled) > 0:
            rec_category = "eligibility_confirmed" if not is_state_unconfirmed else "potentially_eligible"
            match_status = "high_potential"
            confidence = 96.0
            explanation_en = f"Eligibility confirmed by available rules: {'; '.join(fulfilled)}."
            explanation_ta = f"அனைத்து விதிமுறைகளின்படி தகுதி உறுதிசெய்யப்பட்டது: {'; '.join(fulfilled)}."
            explanation_hi = f"उपलब्ध नियमों के अनुसार पात्रता की पुष्टि हुई: {'; '.join(fulfilled)}।"
            explanation_ml = f"ലഭ്യമായ നിയമങ്ങൾ അനുസരിച്ച് യോഗ്യത സ്ഥിരീകരിച്ചു: {'; '.join(fulfilled)}."
        elif len(fulfilled) > 0:
            rec_category = "potentially_eligible"
            match_status = "potential_match"
            ratio = len(fulfilled) / total_conds if total_conds > 0 else 0.5
            confidence = round(ratio * 50.0 + 45.0, 1)
            explanation_en = f"Potentially eligible based on: {'; '.join(fulfilled)}. Note: {len(unverified)} condition(s) require official verification."
            explanation_ta = f"சாத்தியமான தகுதி: {'; '.join(fulfilled)}. கவனிக்க: {len(unverified)} நிபந்தனைகள் அதிகாரப்பூர்வமாக சரிபார்க்கப்பட வேண்டும்."
            explanation_hi = f"संभावित पात्रता आधार: {'; '.join(fulfilled)}। ध्यान दें: {len(unverified)} शर्तों का आधिकारिक सत्यापन आवश्यक है।"
            explanation_ml = f"സാധ്യതയുള്ള യോഗ്യതാ മാനദണ്ഡങ്ങൾ: {'; '.join(fulfilled)}. ശ്രദ്ധിക്കുക: {len(unverified)} വ്യവസ്ഥകൾ ഔദ്യോഗികമായി പരിശോധിക്കേണ്ടതുണ്ട്."
        else:
            rec_category = "more_info_required"
            match_status = "conditional"
            confidence = 40.0
            explanation_en = f"More information required to confirm eligibility. Mandatory criteria ({len(unverified)}) need verification."
            explanation_ta = f"தகுதியை உறுதிப்படுத்த கூடுதல் தகவல்கள் தேவைப்படுகின்றன. {len(unverified)} நிபந்தனைகள் சரிபார்க்கப்பட வேண்டும்."
            explanation_hi = f"पात्रता की पुष्टि के लिए अतिरिक्त जानकारी आवश्यक है। {len(unverified)} अनिवार्य शर्तों का सत्यापन आवश्यक है।"
            explanation_ml = f"യോഗ്യത സ്ഥിരീകരിക്കുന്നതിന് കൂടുതൽ വിവരങ്ങൾ ആവശ്യമാണ്. {len(unverified)} നിബന്ധനകൾ പരിശോധിക്കേണ്ടതുണ്ട്."

        if is_state_unconfirmed:
            explanation_en += f" (Note: Exclusive to residents of {scheme_state}; location confirmation required)"
            explanation_ta += f" (கவனிக்க: இது {scheme_state} மாநில வாசகர்களுக்கானது; இருப்பிட உறுதிப்படுத்தல் தேவை)"
            explanation_hi += f" (ध्यान दें: यह {scheme_state} निवासियों के लिए है; राज्य पुष्टि आवश्यक है)"
            explanation_ml += f" (ശ്രദ്ധിക്കുക: ഇത് {scheme_state} നിവാസികൾക്കുള്ളതാണ്; സ്ഥിരീകരണം ആവശ്യമാണ്)"

        # Source & coverage details
        source_url = src.portal_url if src else "https://www.india.gov.in"
        source_name = src.source_name if src else "Government Portal"
        verified_date = src.verified_date if src else "2026-10-15"
        
        if is_central or scheme_level == "Central":
            coverage = "Central Government of India"
        elif is_state_unconfirmed:
            coverage = f"State Government ({scheme_state}) - State Confirmation Needed"
        elif scheme_level == "Union Territory":
            coverage = f"Union Territory ({scheme_state})"
        elif scheme_level == "State":
            coverage = f"State Government ({scheme_state})"
        else:
            coverage = f"State Government ({scheme_state or 'State'})"

        docs_res = [RequiredDocumentResponse.model_validate(d) for d in (scheme.documents or [])]
        steps_res = [ApplicationStepResponse.model_validate(s) for s in (scheme.steps or [])]

        return PotentialSchemeMatch(
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
            match_status=match_status,
            match_confidence=confidence,
            recommendation_category=rec_category,
            eligibility_explanation_en=explanation_en,
            eligibility_explanation_ta=explanation_ta,
            eligibility_explanation_hi=explanation_hi,
            eligibility_explanation_ml=explanation_ml,
            fulfilled_conditions=fulfilled,
            unverified_conditions=unverified,
            unfulfilled_conditions=violated,
            missing_information_fields=missing_fields,
            required_documents=docs_res,
            application_steps=steps_res,
            official_portal_url=source_url,
            official_source_name=source_name,
            verified_date=verified_date,
            official_disclaimer=self.OFFICIAL_DISCLAIMER
        )

    def match_schemes(
        self, 
        db: Session, 
        profile: ExtractedUserProfile, 
        category: str = None,
        include_ineligible: bool = False
    ) -> Tuple[List[PotentialSchemeMatch], List[str], List[str]]:
        """
        Evaluates candidate schemes against citizen profile using structured rules.
        Guarantees strict state residency isolation and mandatory constraint enforcement.
        """
        query = (
            db.query(Scheme)
            .options(
                joinedload(Scheme.source),
                selectinload(Scheme.conditions),
                selectinload(Scheme.documents),
                selectinload(Scheme.steps)
            )
            .filter(Scheme.is_active == True)
        )
        if category and category != "all":
            query = query.filter(Scheme.category == category)
        
        all_schemes = query.all()
        potential_matches: List[PotentialSchemeMatch] = []
        follow_ups_en = set()
        follow_ups_ta = set()

        citizen_state = (profile.state.strip()) if (profile.state and profile.state.strip()) else None

        for scheme in all_schemes:
            match_result = self.evaluate_scheme_for_profile(scheme, profile)

            # If ineligible, discard unless include_ineligible is explicitly requested
            if match_result.recommendation_category == "not_eligible" and not include_ineligible:
                continue

            # Populate follow-ups from unverified conditions
            for cond in (scheme.conditions or []):
                if cond.description_en in match_result.unverified_conditions:
                    if cond.prompt_question_en:
                        follow_ups_en.add(cond.prompt_question_en)
                    if cond.prompt_question_ta:
                        follow_ups_ta.add(cond.prompt_question_ta)

            # If state unconfirmed on exclusive scheme, prompt location
            if "State Confirmation Needed" in (match_result.coverage_type or ""):
                follow_ups_en.add("Which State or Union Territory do you currently reside in?")
                follow_ups_ta.add("நீங்கள் எந்த மாநிலம் அல்லது யூனியன் பிரதேசத்தில் வசிக்கிறீர்கள்?")

            potential_matches.append(match_result)

        # Sort matches by high potential status, specificity (fulfilled count), then confidence descending
        potential_matches.sort(
            key=lambda x: (
                x.match_status == "high_potential",
                len(x.fulfilled_conditions),
                x.match_confidence
            ), 
            reverse=True
        )

        return potential_matches, list(follow_ups_en), list(follow_ups_ta)

matcher = SchemeMatcherService()
