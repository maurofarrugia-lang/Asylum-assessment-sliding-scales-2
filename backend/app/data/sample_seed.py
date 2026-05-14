SAMPLE_DATA = {
    "sources": [
        {
            "name": "ACLED",
            "dataset_name": "Sudan conflict incidents",
            "url": "https://acleddata.com/",
            "publication_date": "2026-04-30",
            "accessed_at": "2026-05-14",
            "reporting_period_start": "2025-11-01",
            "reporting_period_end": "2026-04-30",
            "reliability_note": "Event-level conflict data used for incident and fatality aggregation."
        },
        {
            "name": "World Bank",
            "dataset_name": "Population estimates and projections",
            "url": "https://data.worldbank.org/",
            "publication_date": "2025-12-31",
            "accessed_at": "2026-05-14",
            "reporting_period_start": "2025-01-01",
            "reporting_period_end": "2025-12-31",
            "reliability_note": "Population denominator reference."
        },
        {
            "name": "EUAA Country Guidance",
            "dataset_name": "Sudan country guidance",
            "url": "https://euaa.europa.eu/",
            "publication_date": "2026-02-15",
            "accessed_at": "2026-05-14",
            "reporting_period_start": "2025-01-01",
            "reporting_period_end": "2026-02-15",
            "reliability_note": "Used for narrative context and country guidance reference."
        }
    ],
    "countries": [
        {
            "name": "Sudan",
            "iso_code": "SDN",
            "regions": [
                {
                    "name": "North Darfur",
                    "districts": [
                        {"name": "El Fasher", "population_estimate": 550000},
                        {"name": "Kutum", "population_estimate": 180000}
                    ]
                },
                {
                    "name": "Khartoum State",
                    "districts": [
                        {"name": "Khartoum", "population_estimate": 1200000},
                        {"name": "Omdurman", "population_estimate": 900000}
                    ]
                }
            ]
        },
        {
            "name": "Syria",
            "iso_code": "SYR",
            "regions": [
                {
                    "name": "Aleppo Governorate",
                    "districts": [
                        {"name": "Aleppo", "population_estimate": 2100000}
                    ]
                }
            ]
        },
        {
            "name": "Afghanistan",
            "iso_code": "AFG",
            "regions": [
                {
                    "name": "Kabul Province",
                    "districts": [
                        {"name": "Kabul", "population_estimate": 4600000}
                    ]
                }
            ]
        }
    ]
}
