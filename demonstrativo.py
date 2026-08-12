import pandas as pd


class DemoTrib:
    def __init__(self):
        self.df_anexos = self._get_anexos_data()

    def _get_anexos_data(self):
        df_anexos = pd.read_excel('anexos.xls')
        df_anexos = df_anexos.rename(columns={
            'Anexo n .' : 'anexo',
            'Nome do Anexo' : 'nm_anexo',
            'Receita 12m\n(até) R$' : 'r12_max',
            'Limite inferior\n(R$)': 'r12_min',
            'Alíq. Nominal': 'aliq_nom',
            'Valor a Deduzir\n(R$)': 'vlr_ded'
        })

        df_anexos.columns = df_anexos.columns.str.replace('\n', ' ').str.strip().str.lower()

        return df_anexos