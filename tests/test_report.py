from alignment_check.report import render_html_report, render_table


def test_render_table_basic() -> None:
    html = render_table(["id", "gc"], [["a", 0.5], ["b", 0.6]])
    assert "<th" in html
    assert "<td>a</td>" in html
    assert "<td>0.5</td>" in html


def _base_results(**overrides: object) -> dict[str, object]:
    results: dict[str, object] = {
        "input_name": "test.fasta",
        "load_error": None,
        "basic_facts": {"num_sequences": 2, "lengths": [4]},
        "errors": [
            {
                "name": "duplicate_ids",
                "failed": False,
                "summary": "No duplicate sequence IDs",
                "detail_html": "",
            }
        ],
        "anomalies": [
            {
                "name": "gc_content",
                "failed": True,
                "summary": "1 sequence flagged for GC content",
                "detail_html": "seq_a",
            }
        ],
        "per_sequence_summary": {
            "headers": ["id", "gc"],
            "rows": [["a", 0.5]],
        },
        "plots": [{"title": "Site gaps", "html": "<div>plot</div>"}],
        "notes": ["1 sequence excluded (all gaps)."],
    }
    results.update(overrides)
    return results


def test_render_html_report_success_case_includes_all_sections() -> None:
    html = render_html_report(_base_results())
    assert "Number of sequences: 2" in html
    assert "No duplicate sequence IDs" in html
    assert "1 sequence flagged for GC content" in html
    assert "<td>a</td>" in html
    assert "<div>plot</div>" in html
    assert "1 sequence excluded (all gaps)." in html
    assert 'class="badge fail"' in html
    assert 'class="badge pass"' in html


def test_render_html_report_load_error_short_circuits() -> None:
    results = _base_results(load_error={"message": "File 'x' does not exist."})
    html = render_html_report(results)
    assert "File &#x27;x&#x27; does not exist." in html
    assert "Number of sequences" not in html


def test_render_html_report_escapes_values() -> None:
    results = _base_results(input_name="<script>evil()</script>")
    html = render_html_report(results)
    assert "<script>evil()</script>" not in html
    assert "&lt;script&gt;" in html
