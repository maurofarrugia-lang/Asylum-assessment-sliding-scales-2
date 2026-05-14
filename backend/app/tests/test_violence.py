from app.services.narrative import vulnerability_score
from app.services.violence import classify_risk, detect_trend, rate_per_100k


class DummyThreshold:
    def __init__(self, label, incidents, fatalities, warning, order):
        self.label = label
        self.min_incidents_per_100k = incidents
        self.min_fatalities_per_100k = fatalities
        self.warning_text = warning
        self.sort_order = order


def test_rate_per_100k():
    assert rate_per_100k(50, 100000) == 50.0
    assert rate_per_100k(1, None) is None


def test_detect_trend():
    assert detect_trend(10, 15) == "increasing"
    assert detect_trend(20, 10) == "decreasing"
    assert detect_trend(10, 11) == "stable"


def test_classify_risk():
    thresholds = [
        DummyThreshold("low", 0, 0, "low", 1),
        DummyThreshold("moderate", 10, 2, "moderate", 2),
        DummyThreshold("high", 25, 5, "high", 3),
    ]
    label, warning = classify_risk(26, 1, thresholds)
    assert label == "high"
    assert warning == "high"


def test_vulnerability_score():
    applicant = {
        "age": 17,
        "medical_vulnerabilities": "chronic illness",
        "minority_profile": "minority",
        "support_network": "limited",
    }
    assert vulnerability_score(applicant) >= 4
