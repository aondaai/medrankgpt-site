from visibility.study.classify import classify_response, ResponseClassification

def test_medico_nominal_quando_cita_dr():
    c = classify_response("Recomendo a Dra. Ana Lima e o Dr. Bruno Souza.")
    assert isinstance(c, ResponseClassification)
    assert c.tipo_resposta == "medico_nominal"
    assert "Dra. Ana Lima" in c.medicos and "Dr. Bruno Souza" in c.medicos

def test_marketplace_quando_so_cita_plataforma():
    c = classify_response("Busque no Doctoralia ou no BoaConsulta por dermatologistas.")
    assert c.tipo_resposta == "marketplace"
    assert "doctoralia" in c.marketplaces and "boaconsulta" in c.marketplaces
    assert c.medicos == []

def test_hospital_tem_prioridade_sobre_clinica_quando_sem_medico_e_sem_marketplace():
    c = classify_response("Procure o Hospital Albert Einstein, que tem ótima clínica.")
    assert c.tipo_resposta == "hospital"
    assert c.tem_hospital is True and c.tem_clinica is True

def test_clinica_quando_so_clinica():
    c = classify_response("Procure uma boa clínica de dermatologia na sua região.")
    assert c.tipo_resposta == "clinica"

def test_nenhum_quando_recusa():
    c = classify_response("Não tenho informações suficientes para recomendar um profissional.")
    assert c.tipo_resposta == "nenhum"
    assert c.medicos == [] and c.marketplaces == []

def test_conteudo_generico_quando_so_orienta():
    c = classify_response("Verifique o registro no CRM e leia avaliações antes de escolher.")
    assert c.tipo_resposta == "conteudo_generico"

def test_medico_tem_prioridade_mesmo_com_marketplace():
    c = classify_response("A Dra. Ana Lima é ótima; o perfil dela está no Doctoralia.")
    assert c.tipo_resposta == "medico_nominal"
    assert "doctoralia" in c.marketplaces   # ainda registrado para share of voice

from visibility.study.classify import cfm_risk

def test_cfm_flag_resultado_garantido():
    achados = cfm_risk("Esse procedimento tem resultado garantido e é 100% indolor.")
    assert any("garantido" in a for a in achados)
    assert any("indolor" in a or "100%" in a for a in achados)

def test_cfm_flag_superlativo_com_escopo():
    achados = cfm_risk("É o melhor dermatologista do Brasil, sem dúvida.")
    assert achados   # "melhor ... do brasil" é superlativo vedado

def test_cfm_sem_flag_em_texto_neutro():
    assert cfm_risk("Verifique o CRM e leia avaliações de pacientes.") == []

def test_classify_preenche_cfm_risco():
    c = classify_response("A Dra. Ana garante cura total e resultado garantido.")
    assert c.tipo_resposta == "medico_nominal"
    assert c.cfm_risco   # não-vazio
