import json
import os

# The script reads the JSON files from the "Input" folder next to it.
SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(SCRIPT_FOLDER, "Input")
JSON_FILE_NAMES = ["tech-jobs.json", "non-tech-jobs.json"]
OUTPUT_FOLDER = os.path.join(SCRIPT_FOLDER, "output")

# Main result: the short list of final rejection reasons (one per line).
FINAL_REASONS_FILE_PATH = os.path.join(OUTPUT_FOLDER, "unique_rejection_reasons.txt")
# Final reasons with how many original wordings were merged into each.
REASON_COUNTS_FILE_PATH = os.path.join(OUTPUT_FOLDER, "rejection_reason_counts.txt")
# Every final reason followed by the original wordings that were merged into it.
GROUPED_REASONS_FILE_PATH = os.path.join(OUTPUT_FOLDER, "rejection_reasons_grouped.txt")

OVERRIDES_FILE_PATH = os.path.join(SCRIPT_FOLDER, "manual_reason_overrides.txt")

OTHER_REASON_NAME = "Other (no reason matched)"

# When a wording is split into parts, these two general reasons are dropped
# if a more specific reason was also found. They match too many words.
GENERAL_REASON_NAMES = [
    "Not enough or not relevant experience",
    "Overall profile does not fit the role",
]

# Each final reason has a list of keywords.
# An original reason goes into the FIRST final reason (top to bottom) that has a keyword inside it.
# So the order matters: put the more specific reasons above the general ones.
REASON_RULES = [
    ("Candidate accepted another offer", [
        "accepted another", "accepted other", "accepted an offer", "accepted a ",
        "accepted offer", "has accepted", "had accepted", "already accepted",
        "another offer", "other offer", "external offer",
        "got another", "got an offer", "received another", "received an offer",
        "has another offer", "have another offer", "had another offer",
        "took another", "taken another", "took a different", "chose another",
        "pursuing another", "pursuing other",
    ]),
    ("Candidate declined the offer", [
        "declined", "decline ", "turned down", "refused", "rejected the offer",
        "rejected our offer",
    ]),
    ("Job position closed, on hold or already filled", [
        "role closed", "position closed", "role is closed", "role was closed",
        "position was closed", "job closed", "already filled", "role filled",
        "position filled", "role has been filled", "position has been filled",
        "on hold", "paused", "role changed", "hiring freeze", "no longer hiring",
        "no longer being filled", "no longer being hired", "not being filled",
        "no longer open", "position is no longer", "role is no longer",
    ]),
    ("Candidate did not respond or could not be reached", [
        "respond", "response", "unresponsive", "nonresponsive", "non-responsive",
        "ghost", "unreachable", "not reachable", "no reply", "did not reply",
        "did not answer", "not answer", "pick up", "voicemail", "could not be contacted",
        "cannot be contacted", "cannot be reached", "could not be reached",
        "unable to reach", "not able to reach", "stopped responding", "stopped communicating",
        "communication stalled", "did not engage", "not engaged", "follow up", "follow-up",
    ]),
    ("Candidate showed no interest", [
        "interest", "enthusias", "excited",
    ]),
    ("Candidate withdrew from the hiring process", [
        "withdr", "not actively", "not looking", "not open", "left the hiring process",
        "own business", "opted out", "dropped out", "pulled out", "different role",
    ]),
    ("Duplicate application or removed from the system", [
        "duplicate", "deleted", "removed", "administrative", "application error",
        "application problem", "application issue", "application process",
        "test application", "submitted in error", "resubmitted", "re-submitted",
        "archived", "internal flag", "system error", "process or logistical",
    ]),
    ("Fake profile, fraud or dishonest information", [
        "fraud", "fake", "misrepresent", "inflated", "falsif", "ai-generated",
        "authentic", "not genuine", "suspicious", "fabricat", "not real",
        "unverif", "cannot be verified", "inaccurate", "misleading", "dishonest",
        "not transparent", "criminal", "conviction", "character", "reputation",
        "unprofessional",
    ]),
    ("Candidate already in the hiring pipeline or rejected before", [
        "already", "previously", "prior process", "in pipeline", "in our pipeline",
        "recently applied", "presented to the team", "stale", "candidate considered",
    ]),
    ("Hiring process problem or no feedback from the hiring side", [
        "no longer active", "no longer in the process", "moving too slowly",
        "awaiting feedback", "no feedback", "feedback was not", "invalid feedback",
        "rejected by the hiring manager", "contacted hiring team", "submitted before",
        "ineligible", "no suitable opening", "source is not", "process issue",
        "hiring restriction",
    ]),
    ("Other candidates chosen, or no specific reason given", [
        "another candidate", "other candidates", "similar candidates", "competition",
        "stronger candidate", "better candidate", "not selected", "not moved forward",
        "not moving forward", "will not move forward", "no specific reason",
        "without specific reason", "without a specific reason", "generic",
        "general pass", "no further action", "saved for future", "future consideration",
        "not exceptional", "exceptional", "standout", "stand out", "not impressed",
        "overall impression", "decided not to", "not to proceed", "more qualified",
        "other applicants",
    ]),
    ("Salary expectation does not match the budget", [
        "salary", "compensation", "budget", "pay ", "hourly rate", "day rate",
        "billing rate", "rate expectation", "expensive", "equity", "comp ",
    ]),
    ("Needs visa sponsorship or lacks work authorization", [
        "visa", "sponsor", "authorization", "authorisation", "work permit",
        "right to work", "work eligib", "clearance", "h1b", "h-1b", "citizen",
        "u.s. person", "us person", "not authorized", "opt ", "green card",
    ]),
    ("Wrong location or unwilling to relocate", [
        "location", "relocat", "timezone", "time zone", "remote", "in-office",
        "in office", "office", "commute", "based in", "geograph", "hybrid",
        "located", "region", "country", "overseas", "in-person", "in person",
        "far from", "us-based", "us based", "u.s.-based", "u.s. based", "nyc",
        "san francisco", "bay area", "new york",
    ]),
    ("Candidate not available or start date too late", [
        "availability", "unavailable", "not available", "scheduling conflict", "work schedule",
        "schedule mismatch", "schedule requirement", "schedule constraint", "scheduling problem",
        "timing", "start date", "cannot start", "notice period", "starts too late",
        "timeline",
    ]),
    ("Frequent job changes or short time in past jobs", [
        "tenure", "job hop", "job-hop", "hopping", "hopper", "stint", "frequent",
        "job change", "short-term", "short term", "short job", "short stay",
        "short-lived", "stability", "unstable", "jumpy", "employment gap",
        "career gap", "turnover", "may not stay", "not stay long", "longevity",
        "too many short", "too many jobs", "too many roles", "too many companies",
        "recently started", "recently joined", "just started", "prefers long",
        "short recent jobs", "many short",
    ]),
    ("Contractor, part-time or currently unemployed", [
        "contract", "consultant", "freelance", "part-time", "solo practi",
        "employment type", "not currently employed", "unemployed", "between jobs",
        "employment status",
    ]),
    ("Candidate is overqualified or too senior", [
        "overqualif", "over-qualif", "over qualif", "over- or under-qualified",
        "too senior", "overleveled", "over-leveled", "too experienced",
        "too much experience", "more senior than", "above the level", "beyond the level",
    ]),
    ("Poor communication", [
        "communicat", "articulat", "verbal", "english", "soft skill", "presentation",
        "personality", "attitude", "professionalism", "demeanor", "polish",
        "storytelling", "presence", "interpersonal", "likab", "overconfident",
        "curiosity", "coachab", "ego", "vague",
    ]),
    ("Not a good culture or values fit", [
        "culture", "cultural", "values", "mission", "team fit", "collaborat",
        "work style", "working style", "team player", "teamwork", "adapt",
    ]),
    ("Candidate failed or did not complete an interview or test", [
        "no show", "no-show", "missed", "did not show", "did not attend",
        "failed to attend", "skipped", "late to", "did not schedule", "failed to schedule",
        "not scheduled", "did not complete", "not completed", "failed to complete",
        "did not submit", "not submitted", "unprepared",
        "interview", "assessment", "take-home", "take home", "coding challenge",
        "assignment", "exercise", "failed", "did not pass", "case study",
        "screening", "technical screen", "phone screen",
        "performance bar", "hiring bar", "talent bar", "signal bar",
    ]),
    ("No startup experience, or only large-company background", [
        "startup", "start-up", "early-stage", "early stage", "large compan",
        "larger compan", "larger firm", "larger team", "large structured",
        "large organization", "big tech", "big compan", "corporate",
        "enterprise environment", "small company", "0-to-1", "0 to 1",
        "zero-to-one", "scrappy", "hyper-growth", "hypergrowth", "high-growth",
        "high growth", "fast-paced", "fast-growing",
    ]),
    ("Education or past companies not strong enough", [
        "pedigree", "education", "degree", "academic", "universit", "school",
        "credential", "gpa", "alma", "college", "brand", "caliber", "calibre",
        "prestig", "top compan", "top-tier", "top tier", "tier-1", "tier 1",
        "reputable", "name recognition", "phd", "masters", "master's", "bar exam",
        "licensed", "admitted", "j.d.", "certif", "previous companies",
        "past companies", "prior companies", "previous employers", "prior employers",
        "notable", "impressive", "low-quality", "lower-quality", "low quality",
        "target compan", "not a target", "excluded company", "disallowed",
        "current employer", "current firm", "marquee", "elite", "frontier",
        "previous company", "prior company", "prior employer", "low-complexity",
    ]),
    ("Lacks ownership, drive or leadership", [
        "ownership", "initiative", "drive", "passion", "energy", "hustle",
        "proactive", "autonom", "self-starter", "motivat", "ambition",
        "entrepreneur", "intensity", "grit", "hunger", "leadership",
        "people management", "people-management", "team-building", "mentor",
    ]),
    ("Too junior, or seniority level does not match", [
        "seniority", "junior", "senior", "level", "too early", "early in career",
        "early-career", "early career", "entry-level", "intern", "principal",
        "too low", "mid-level",
    ]),
    ("Industry or domain experience does not match", [
        "domain", "industry", "vertical", "sector", "b2b", "b2c", "fintech",
        "healthcare", "saas", "consumer", "customer", "market", "sales",
        "marketing", "finance", "legal", "recruit", "enterprise", "gtm",
        "go-to-market", "ecommerce", "e-commerce", "crypto", "devtools",
        "developer-facing", "regulated", "niche",
    ]),
    ("Missing required skills or technical depth", [
        "skill", "technical", "tech stack", "stack", "expertise", "proficien",
        "knowledge", "coding", "engineering", "ml ", "ai ", "ai-", "infrastructure",
        "backend", "back-end", "frontend", "front-end", "full-stack", "fullstack",
        "hands-on", "hands on", "depth", "qualification", "requirement", "competenc",
        "capabilit", "tooling", "framework", "architecture", "devops", "algorithm",
        "models", "llm", "programming", "python", "hardware", "portfolio", "craft",
        " ui ", " ux ", "shipped", "side projects", "public code", "judgment",
        "design decisions", "logo design", "work quality", "solving difficult",
    ]),
    ("Unclear career goals, growth or work history", [
        "career trajectory", "career goals", "career progression", "career path",
        "promotion history", "work history", "employment history", "expectations are unclear",
    ]),
    ("No clear results or achievements shown", [
        "impact", "metrics", "achievement", "measurable", "concrete results",
        "quota", "book of business", "performance spikes", "excellence",
        "outcome-focused", "extraordinary", "business development",
    ]),
    ("Concerns about behavior, trust or commitment", [
        "commitment", "divided focus", "double-dipping", "behavior", "credibility",
        "red-flag", "disciplinary", "reference check", "performance is declining",
    ]),
    ("Job role or focus does not match the candidate", [
        "focus", "scope", "specializ", "generalist", "wrong role", "wrong product",
        "not a pure", "not a product", "client constraints", "account-management",
        "better fit for",
    ]),
    ("Position is still active", []),
    ("Recruiter or hiring manager did not respond", []),
    ("Lacks required security clearance or ITAR eligibility", []),
    ("Missing required license or bar exam", []),
    ("Missing required language skills", []),
    ("Does not have the required book of business (client base)", []),
    ("Has not closed a funding round (fundraising experience)", []),
    ("Has not sold to our target buyer (customer type)", []),
    ("Consulting or agency background not a fit", []),
    ("Company changed the hiring requirements or focus", []),
    ("Team suggests multiple tech candidates", []),
    ("Resume has errors or is poorly formatted", []),
    ("Insufficient information", []),
    ("Not enough or not relevant experience", [
        "experience", "years of", "yoe", "exposure", "track record", "not enough",
        "insufficient", "limited", "lacks", "lack of", "missing", "underqualif",
        "stated criteria",
    ]),
    ("Overall profile does not fit the role", [
        "background", "profile", "resume", "not a fit", "overall fit", "fit is marginal",
        "good match", "strong fit", "better fit", "fit not", "not a good fit", "poor fit",
        "mismatch", "not suitable", "not the right", "does not match", "do not match",
        "not aligned", "does not align", "role fit", "wrong fit",
    ]),
]


def load_json_file(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    return json_data


def get_rejection_reasons_from_role(role):
    role_details = role.get("details")
    if role_details is None:
        return []

    rejection_reasons = role_details.get("rejection_categories")
    if rejection_reasons is None:
        return []

    return rejection_reasons


def clean_rejection_reason(rejection_reason):
    # The data uses special hyphens and apostrophes (like the non-breaking hyphen).
    # We turn them into normal ones, so "job-hopping" and "job<special hyphen>hopping" match.
    cleaned_reason = rejection_reason
    cleaned_reason = cleaned_reason.replace("‑", "-")
    cleaned_reason = cleaned_reason.replace("‐", "-")
    cleaned_reason = cleaned_reason.replace("–", "-")
    cleaned_reason = cleaned_reason.replace("’", "'")

    # Remove extra spaces and the trailing full stop,
    # so "Application was deleted." and "Application was deleted" match.
    cleaned_reason = cleaned_reason.strip()
    cleaned_reason = cleaned_reason.rstrip(".")
    cleaned_reason = cleaned_reason.strip()
    return cleaned_reason


def collect_rejection_reasons_from_file(json_file_path, unique_reasons_by_lowercase):
    json_data = load_json_file(json_file_path)
    all_roles = json_data["roles"]

    for role in all_roles:
        rejection_reasons = get_rejection_reasons_from_role(role)

        for rejection_reason in rejection_reasons:
            cleaned_reason = clean_rejection_reason(rejection_reason)
            if cleaned_reason == "":
                continue

            # Lowercase is the key, so "Not a fit" and "not a fit" count as one.
            # The first spelling we see is the one we keep.
            lowercase_reason = cleaned_reason.lower()
            if lowercase_reason not in unique_reasons_by_lowercase:
                unique_reasons_by_lowercase[lowercase_reason] = cleaned_reason


def load_manual_overrides():
    # Each line is:  original reason | final reason name
    # Lines starting with # and empty lines are ignored.
    manual_overrides = {}

    if not os.path.exists(OVERRIDES_FILE_PATH):
        return manual_overrides

    with open(OVERRIDES_FILE_PATH, "r", encoding="utf-8") as overrides_file:
        for line in overrides_file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue

            original_reason, final_reason_name = line.rsplit("|", 1)
            lowercase_reason = original_reason.strip().lower()
            manual_overrides[lowercase_reason] = final_reason_name.strip()

    return manual_overrides


def find_reason_by_keywords(text):
    # Add spaces around the text so keywords like "pay " or " ui " also match at the edges.
    lowercase_text = " " + text.lower() + " "

    for final_reason_name, keywords in REASON_RULES:
        for keyword in keywords:
            if keyword in lowercase_text:
                return final_reason_name

    return None


def split_into_parts(original_reason):
    # "Candidate withdrew, accepted another offer, or was unresponsive"
    # becomes three parts, so each part can get its own reason.
    text = original_reason
    text = text.replace(", or ", "|")
    text = text.replace(" or ", "|")
    text = text.replace(", and ", "|")
    text = text.replace(" and ", "|")
    text = text.replace(", ", "|")
    text = text.replace("; ", "|")
    return text.split("|")


def find_final_reasons(original_reason, manual_overrides):
    # A manual override always wins, and it gives exactly one reason.
    lowercase_original_reason = original_reason.lower()
    if lowercase_original_reason in manual_overrides:
        return [manual_overrides[lowercase_original_reason]]

    # Check every part of the wording on its own.
    reasons_found = []
    for part in split_into_parts(original_reason):
        reason_for_part = find_reason_by_keywords(part)
        if reason_for_part is not None and reason_for_part not in reasons_found:
            reasons_found.append(reason_for_part)

    # Drop the general reasons from the split, so they only count when nothing else matched.
    specific_reasons_found = []
    for reason in reasons_found:
        if reason not in GENERAL_REASON_NAMES:
            specific_reasons_found.append(reason)
    reasons_found = specific_reasons_found

    # Two or more different reasons means the wording is split between them.
    if len(reasons_found) >= 2:
        return reasons_found

    # Otherwise look at the whole wording, like before.
    reason_for_whole_wording = find_reason_by_keywords(original_reason)
    if reason_for_whole_wording is not None:
        return [reason_for_whole_wording]

    return [OTHER_REASON_NAME]


def group_original_reasons_by_final_reason(original_reasons, manual_overrides):
    original_reasons_by_final_reason = {}

    for original_reason in original_reasons:
        # One wording can belong to more than one final reason.
        final_reason_names = find_final_reasons(original_reason, manual_overrides)

        for final_reason_name in final_reason_names:
            if final_reason_name not in original_reasons_by_final_reason:
                original_reasons_by_final_reason[final_reason_name] = []
            original_reasons_by_final_reason[final_reason_name].append(original_reason)

    return original_reasons_by_final_reason


def count_split_wordings(original_reasons_by_final_reason):
    # A wording is "split" when it shows up under more than one final reason.
    times_each_wording_is_listed = {}

    for original_reasons in original_reasons_by_final_reason.values():
        for original_reason in original_reasons:
            times_each_wording_is_listed[original_reason] = (
                times_each_wording_is_listed.get(original_reason, 0) + 1
            )

    split_wording_count = 0
    for times_listed in times_each_wording_is_listed.values():
        if times_listed >= 2:
            split_wording_count += 1
    return split_wording_count


def check_manual_overrides(manual_overrides, unique_reasons_by_lowercase):
    # Tell the user about override lines that point to a reason or list that does not exist.
    valid_final_reason_names = get_final_reason_names_in_order()

    for lowercase_reason, final_reason_name in manual_overrides.items():
        if lowercase_reason not in unique_reasons_by_lowercase:
            print("Warning: override reason not found in data:", lowercase_reason)
        if final_reason_name not in valid_final_reason_names:
            print("Warning: override list does not exist:", final_reason_name)


def get_final_reason_names_in_order():
    final_reason_names = []
    for final_reason_name, keywords in REASON_RULES:
        final_reason_names.append(final_reason_name)
    final_reason_names.append(OTHER_REASON_NAME)
    return final_reason_names


def save_final_reasons_to_file(original_reasons_by_final_reason):
    with open(FINAL_REASONS_FILE_PATH, "w", encoding="utf-8") as output_file:
        for final_reason_name in get_final_reason_names_in_order():
            if final_reason_name in original_reasons_by_final_reason:
                output_file.write(final_reason_name + "\n")


def save_reason_counts_to_file(original_reasons_by_final_reason):
    with open(REASON_COUNTS_FILE_PATH, "w", encoding="utf-8") as output_file:
        for final_reason_name in get_final_reason_names_in_order():
            original_reasons = original_reasons_by_final_reason.get(final_reason_name, [])
            if len(original_reasons) > 0:
                output_file.write(final_reason_name + ": " + str(len(original_reasons)) + "\n")


def save_grouped_reasons_to_file(original_reasons_by_final_reason):
    with open(GROUPED_REASONS_FILE_PATH, "w", encoding="utf-8") as output_file:
        for final_reason_name in get_final_reason_names_in_order():
            original_reasons = original_reasons_by_final_reason.get(final_reason_name, [])
            if len(original_reasons) == 0:
                continue

            output_file.write("## " + final_reason_name + " (" + str(len(original_reasons)) + ")\n")

            for original_reason in sorted(original_reasons, key=str.lower):
                output_file.write("- " + original_reason + "\n")

            output_file.write("\n")


def main():
    unique_reasons_by_lowercase = {}

    for json_file_name in JSON_FILE_NAMES:
        json_file_path = os.path.join(INPUT_FOLDER, json_file_name)
        collect_rejection_reasons_from_file(json_file_path, unique_reasons_by_lowercase)

    original_reasons = list(unique_reasons_by_lowercase.values())
    manual_overrides = load_manual_overrides()
    check_manual_overrides(manual_overrides, unique_reasons_by_lowercase)
    original_reasons_by_final_reason = group_original_reasons_by_final_reason(
        original_reasons, manual_overrides
    )

    # Create the output folder if it does not exist yet.
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    save_final_reasons_to_file(original_reasons_by_final_reason)
    save_reason_counts_to_file(original_reasons_by_final_reason)
    save_grouped_reasons_to_file(original_reasons_by_final_reason)

    print("Original wordings found:", len(original_reasons))
    print("Final rejection reasons:", len(original_reasons_by_final_reason))
    print("Wordings split across several reasons:", count_split_wordings(original_reasons_by_final_reason))
    print("Saved to folder:", OUTPUT_FOLDER)


main()
