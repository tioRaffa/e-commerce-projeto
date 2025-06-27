from rest_framework import serializers
from .models import AddressModel
import requests


class AddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AddressModel
        fields = [
            'id',
            'zip_code',
            'street',
            'number',
            'complement',
            'neighborhood',
            'city',
            'state',
            'country',
            'is_primary'
        ]
       
    def validate(self, data):
        if "zip_code" not in data:
            return data

        cep = ''.join(filter(str.isdigit, data.get('zip_code', '')))

        if len(cep) != 8:
            raise serializers.ValidationError({
                "zip_code": "O CEP deve conter 8 digitos"
            })
        
        try:
            response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
            response.raise_for_status()
            viacep_data = response.json()

            if viacep_data.get('erro'):
                raise serializers.ValidationError({
                    "zip_code": 'CEP não encontrado'
                })
            
            logradouro_api = viacep_data.get('logradouro')
            if logradouro_api:
                data['street'] = logradouro_api
            data['neighborhood'] = viacep_data.get('bairro')
            data['city'] = viacep_data.get('localidade')
            data['state'] = viacep_data.get('uf')

        except requests.exceptions.RequestException:
            print(f"AVISO: Validação de CEP para {cep} falhou. Usando dados do usuário.")
            pass
        return data