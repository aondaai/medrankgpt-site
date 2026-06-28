from visibility.names import tokens, same_person, mentioned_names


def test_same_person_distinct_surnames_is_false():
    # #3 false-positive guard: same first name, different surname → different person
    assert same_person({"ana", "silva"}, {"ana", "costa"}) is False


def test_same_person_superset_is_true():
    assert same_person({"fulana", "tal"}, {"fulana", "tal", "dermatologia"}) is True


def test_mentioned_names_captures_full_span_with_connective():
    out = mentioned_names("Recomendo a Dra. Fulana de Tal e o Dr. João Silva.")
    assert out == ["Dra. Fulana de Tal", "Dr. João Silva"]


def test_tokens_drops_titles_and_connectives():
    assert tokens("Dra. Fulana de Tal") == {"fulana", "tal"}
