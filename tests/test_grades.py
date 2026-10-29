from voucher_growth_model.data_cleaning.extract_esa import GRADES, parse

COLS = [c for c, _ in GRADES]

TABLE = """Grade level Number of students
Preschool—disability 849
Kindergarten 5,497
1st 6,965
2nd 7,780
3rd 7,377
4th 7,047
5th 6,965
6th 6,797
7th 6,370
8th 6,096
9th 5,017
10th 4,600
11th 3,850
12th 4,383
Total 79,593
"""

MULTI_QUARTER = """Grade Level Count of Students
 Q2 Q3 Q4
Preschool 278 296 289
Kindergarten 725 754 741
1st 830 832 804
12th 542 532 529
Total 9,718 9,831 9,669
"""

CHART = (
    "Total 61,689\n"
    + "\n".join(["771", "7,757", "5,780", "5,478", "5,422", "5,215", "5,192", "5,109", "4,655", "4,148", "3,898", "3,237", "2,698", "2,329"])
    + "\n0 1000 2000\nPreschool w/Disability\nKindergarten\n1st\n2nd\n"
)


def test_column_names():
    assert COLS == ["kinder"] + [f"grade_{n}" for n in range(1, 13)]


def test_single_column_table():
    r = parse(TABLE)
    assert r["kinder"] == 5497
    assert r["grade_1"] == 6965
    assert r["grade_10"] == 4600
    assert r["grade_12"] == 4383


def test_preschool_prefers_grade_table():
    text = "Preschool—disability 1,346\nOther\n" + TABLE.replace("849", "1,340")
    assert parse(text)["Preschool Count"] == 1340


def test_multi_quarter_takes_last_column():
    r = parse(MULTI_QUARTER)
    assert (r["kinder"], r["grade_1"], r["grade_12"]) == (741, 804, 529)
    assert r["grade_2"] is None


def test_chart_fallback_requires_total_match():
    r = parse(CHART)
    assert (r["kinder"], r["grade_1"], r["grade_12"]) == (7757, 5780, 2329)
    assert parse(CHART.replace("61,689", "61,000"))["kinder"] is None
