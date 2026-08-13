import pandas as pd


class DemoTrib:
    def __init__(self):
        self.df_anexos = self._get_anexos_data()
        self.aliq_cbs = 0.0921
        self.aliq_pis_cofins = 0.0365

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

    def calcular_aliq_efetiva(self,rbt12, anexo):
        if rbt12 == 0:
            return 0, self.df_anexos.iloc[0:0]
        if rbt12 > 4800000:
            raise ValueError("Empresa não se enquadra no Simples Nacional")
        df_efetivo = self.df_anexos[self.df_anexos['anexo'] == anexo]
        df_efetivo = df_efetivo[(rbt12 >= df_efetivo['r12_min']) & (rbt12<= df_efetivo['r12_max'])]

        return (rbt12 * df_efetivo['aliq_nom'].item() - df_efetivo['vlr_ded'].item())/ rbt12 , df_efetivo

    def das_mensal(self, rbt12, fat_mes, anexo):

        aliq_efe, df_filtrado = self.calcular_aliq_efetiva(rbt12, anexo)
        das_total = aliq_efe * fat_mes
        df_partilha = das_total * df_filtrado[['irpj', 'csll', 'cofins', 'pis/pasep', 'cpp', 'ipi', 'icms', 'iss']]
        return das_total, df_partilha


    def calcular_cbs_debito(self, vendas_mes):
        return vendas_mes * self.aliq_cbs

    def calcular_cbs_credito(self, compras_mes):
        return compras_mes * self.aliq_cbs

    def cenario_hibrido(self, rbt12, fat_mes, anexo, compras):

        das_total , df = self.das_mensal(rbt12, fat_mes, anexo)

        pis = df['pis/pasep'].item()
        cofins = df['cofins'].item()

        simples_sem_cbs = das_total - pis - cofins

        cbs_debito = self.calcular_cbs_debito(fat_mes)
        cbs_credito = self.calcular_cbs_credito(compras)
        cbs_liquida = cbs_debito - cbs_credito

        total_hibrido = simples_sem_cbs + cbs_liquida

        return total_hibrido, simples_sem_cbs, cbs_liquida

    def comparar_cenarios(self, rbt12, fat_mes, anexo, compras):
        das_total, _ = self.das_mensal(rbt12, fat_mes, anexo)
        total_hibrido, simples_sem_cbs, cbs_liquida = self.cenario_hibrido(rbt12, fat_mes, anexo, compras)
        
        diferenca = total_hibrido - das_total
        variacao_pct = (diferenca / das_total) * 100 if das_total > 0 else 0
        
        return {
            'das_atual': das_total,
            'simples_sem_cbs': simples_sem_cbs,
            'cbs_liquida': cbs_liquida,
            'total_hibrido': total_hibrido,
            'diferenca': diferenca,
            'variacao_pct': variacao_pct
        }

    def gross_down(self, valor_produto):
        valor_sem_pis_cofins = valor_produto / (1 + self.aliq_pis_cofins)
        valor_pis_cofins = valor_produto - valor_sem_pis_cofins
        return valor_sem_pis_cofins, valor_pis_cofins

    def gross_up(self, valor_sem_pis_cofins):
        valor_cbs = valor_sem_pis_cofins * self.aliq_cbs
        valor_final = valor_sem_pis_cofins + valor_cbs
        return valor_final, valor_cbs



