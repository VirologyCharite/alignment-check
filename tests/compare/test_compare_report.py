from alignment_check.compare.compare_report import render_compare_report


def _base_results(**overrides: object) -> dict[str, object]:
    results: dict[str, object] = {
        "name_a": "a.fasta",
        "name_b": "b.fasta",
        "load_error": None,
        "tier1_items": [
            {
                "failed": False,
                "summary": "Same sequence IDs",
                "detail_html": "",
            }
        ],
        "tier2_note": None,
        "gap_count_table": {
            "headers": ["id", "gaps_a", "gaps_b"],
            "rows": [["s1", 2, 4]],
        },
        "plots": [{"title": "Gap positions", "html": "<div>plot</div>"}],
    }
    results.update(overrides)
    return results


def test_render_compare_report_success_case() -> None:
    html = render_compare_report(_base_results())
    assert "a.fasta" in html
    assert "b.fasta" in html
    assert "Same sequence IDs" in html
    assert "<td>s1</td>" in html
    assert "<div>plot</div>" in html


def test_render_compare_report_tier2_note_shown() -> None:
    html = render_compare_report(
        _base_results(tier2_note="No common sequences.", gap_count_table=None, plots=[])
    )
    assert "No common sequences." in html
    assert "Gap-pattern comparison" not in html


def test_render_compare_report_load_error_short_circuits() -> None:
    html = render_compare_report(
        _base_results(load_error={"message": "File 'x' does not exist."})
    )
    assert "does not exist" in html
    assert "Basic comparison" not in html
