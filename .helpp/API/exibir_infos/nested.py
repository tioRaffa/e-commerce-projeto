from rest_framework import serializers


class Exemplo(serializers.ModelSerializer):

    iformação = Outro_Serializer(many=True, read_only=True)                 # type: ignore

    # or

    iformação = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='review-detail'
    )             #  |-> nome da view  


    class Meta:
        extra_kwargs = {
            'email': {
                'write_only': True,
            }}
        
        model = ...
        fields = [
            'blabla',
            'informação'   # RELAÇÃO NESTED
        ]