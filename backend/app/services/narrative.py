from __future__ import annotations

from typing import Any

from app.services.violence import SummaryBundle


def _footnote_map(sources: list[Any]) -> tuple[dict[int, int], list[str]]:
    mapping: dict[int, int] = {}
    notes: list[str] = []
    for idx, source in enumerate(sources, start=1):
        mapping[source.id] = idx
        notes.append(
            f"[{idx}] {source.name}, {source.dataset_name}, publication date: {source.publication_date or 'n/a'}, "
            f"reporting period: {source.reporting_period_start or 'n/a'} to {source.reporting_period_end or 'n/a'}, accessed: {source.accessed_at}, {source.url}"
        )
    return mapping, notes


def vulnerability_score(applicant: dict[str, Any]) -> int:
    score = 0
    if applicant.get("age") is not None and (applicant["age"] < 18 or applicant["age"] > 65):
        score += 1
    for key in [
        "disability",
        "medical_vulnerabilities",
        "minority_profile",
        "previous_harm",
        "internal_displacement_history",
        "area_specific_vulnerabilities",
        "travel_route_concerns",
    ]:
        if applicant.get(key):
            score += 1
    if (applicant.get("single_status") or "").lower().startswith("single"):
        score += 1
    if (applicant.get("support_network") or "").lower() in {"limited", "none", "absent"}:
        score += 1
    return score


def build_assessment_narrative(summary: SummaryBundle, applicant: dict[str, Any], country_info: dict[str, Any]) -> str:
    footnotes_map, footnotes = _footnote_map(summary.sources)
    source_ref = "".join(f"[{footnotes_map[s.id]}]" for s in summary.sources[:3]) if summary.sources else ""
    vuln_score = vulnerability_score(applicant)

    area_text = (
        f"1. Area Assessment\n"
        f"The selected area is {summary.area_name}. For the chosen reference period, the available conflict information indicates a {summary.risk_label} level of indiscriminate violence. "
        f"The current analytical confidence is assessed as {summary.confidence}. {summary.warning_text} {source_ref}"
    )

    indicators_text = (
        f"2. Indiscriminate Violence Analysis\n"
        f"The area recorded {summary.incident_count} conflict incidents, {summary.fatalities_total} reported fatalities, and {summary.civilian_harm_total} civilian-harm entries. "
        f"This corresponds to approximately {summary.incidents_per_100k if summary.incidents_per_100k is not None else 'n/a'} incidents per 100,000 inhabitants, "
        f"{summary.fatalities_per_100k if summary.fatalities_per_100k is not None else 'n/a'} fatalities per 100,000 inhabitants, and "
        f"{summary.civilian_harm_per_100k if summary.civilian_harm_per_100k is not None else 'n/a'} civilian-harm events per 100,000 inhabitants. "
        f"The short-term trend is assessed as {summary.trend}."
    )

    circumstances = []
    for key, value in applicant.items():
        if value not in (None, "", []):
            label = key.replace("_", " ")
            circumstances.append(f"{label}: {value}")
    circumstances_text = "; ".join(circumstances) if circumstances else "No material personal circumstances were entered beyond the baseline profile."
    personal_text = (
        f"3. Personal Circumstances Analysis\n"
        f"The applicant profile reveals the following relevant factors: {circumstances_text}. "
        f"On the structured vulnerability scale used by this MVP, the profile scores {vuln_score}. "
        f"This means that even where violence levels are not exceptional, the applicant may face an elevated risk if exposure, access constraints, or coping capacity are adversely affected."
    )

    coi_bits = [value for value in country_info.values() if value]
    coi_text = " ".join(coi_bits) if coi_bits else "No additional COI narrative was entered by the officer."
    conclusion = (
        f"4. Sliding Scale Conclusion\n"
        f"Taking the violence indicators together with the recorded personal circumstances and country information, the case requires a sliding-scale analysis. "
        f"Where violence is assessed as {summary.risk_label}, vulnerability factors such as the applicant's profile, prior harm, support limitations, and local constraints may lower the threshold at which serious harm becomes reasonably likely. "
        f"The entered country information states: {coi_text} "
        f"This tool therefore suggests that the officer consider whether the combined effect of the area conditions and the applicant's profile leads to a real risk of serious harm under the applicable legal framework."
    )

    limitations = (
        f"5. Methodological Limitations\n"
        f"This assessment is an analytical support tool and does not replace the legal assessment by the protection officer. "
        f"Data quality notes: {'; '.join(summary.data_quality_notes) if summary.data_quality_notes else 'No major quality flags were triggered.'}"
    )

    sources_text = "6. Source References\n" + "\n".join(footnotes) if footnotes else "6. Source References\nNo linked sources were available for this calculation."

    return "\n\n".join([area_text, indicators_text, personal_text, conclusion, limitations, sources_text])
