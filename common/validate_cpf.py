import re

def validar_cpf(cpf):
    
    cpf = re.sub(r'[^0-9]', '', cpf)

    if not cpf or len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False

    return True
