from visibility.study.roster import (parse_doctoralia_names, doctoralia_url,
                                      build_roster_entries)
from visibility.models import DoctorMeta

HTML = '''
<html><body>
<script type="application/ld+json">{"@type":"Physician","name":"Dra. Ana Cristina Dantas"}</script>
<script>{"name":"Dr. Marcelo Oliveira Nunes","specialty":"x"}</script>
junk {"name":"Dra. Ana Cristina Dantas"} duplicada
{"name":"Clínica XYZ"}  // não é Dr./Dra.
{"name":"Dr. João"}
</body></html>
'''

def test_parse_extrai_nomes_dr_dra_unicos():
    nomes = parse_doctoralia_names(HTML)
    assert "Dra. Ana Cristina Dantas" in nomes
    assert "Dr. Marcelo Oliveira Nunes" in nomes
    assert "Dr. João" in nomes
    # dedup
    assert nomes.count("Dra. Ana Cristina Dantas") == 1
    # ignora não-médico
    assert "Clínica XYZ" not in nomes

def test_parse_respeita_max():
    nomes = parse_doctoralia_names(HTML, max_n=2)
    assert len(nomes) == 2

def test_doctoralia_url():
    assert doctoralia_url("dermatologista", "sao-paulo") == \
        "https://www.doctoralia.com.br/dermatologista/sao-paulo"

def test_build_roster_entries_vira_doctormeta_dicts():
    entries = build_roster_entries(["Dra. Ana Cristina Dantas", "Dr. João"],
                                   especialidade="Dermatologia", cidade="São Paulo", uf="SP")
    assert len(entries) == 2
    # cada entry deve validar como DoctorMeta
    d = DoctorMeta.model_validate(entries[0])
    assert d.nome == "Dra. Ana Cristina Dantas"
    assert d.especialidade_principal == "Dermatologia"
    assert d.cidade == "São Paulo" and d.uf == "SP"
