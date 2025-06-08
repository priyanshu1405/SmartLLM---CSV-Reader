from rest_framework import serializers
from .models import CSVFile
import pandas as pd

class CSVFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVFile
        fields = '__all__'

    def create(self, validated_data):
        uploaded_file = validated_data['file']
        print("Uploaded File:", uploaded_file)

        try:
            df = pd.read_csv(uploaded_file)
            preview = df.head().to_dict(orient='records')
            validated_data['preview_data'] = preview
            print("CSV Preview:", preview)
        except Exception as e:
            print("Error reading CSV:", str(e))
            validated_data['preview_data'] = []

        return super().create(validated_data)
