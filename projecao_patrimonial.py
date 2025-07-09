import streamlit as st
import pandas as pd
import numpy_financial as nf
import plotly.graph_objects as go

# Configuração da página Streamlit
st.set_page_config(layout="wide", page_title="Projeção Patrimonial")

st.title("💰 Projeção Patrimonial Interativa")
st.write("Utilize esta ferramenta para criar cenários de projeção patrimonial para seus clientes, considerando o patrimônio inicial, aportes mensais e taxas de rentabilidade e inflação.")

# --- Barra Lateral para Entradas (Premissas) ---
st.sidebar.header("Defina as Premissas")

patrimonio_inicial = st.sidebar.number_input(
    "Patrimônio Inicial (R\$)",
    min_value=0.0,
    value=1_500_000.0,
    step=10_000.0,
    format="%.2f",
    help="O valor atual do patrimônio do cliente."
)
aportes_mensais = st.sidebar.number_input(
    "Aportes Mensais (R\$)",
    min_value=0.0,
    value=5_000.0,
    step=100.0,
    format="%.2f",
    help="Valor que o cliente pretende aportar mensalmente."
)
taxa_dividendos_anual = st.sidebar.slider(
     "Percentual de Dividendos Anual Esperado (%)",
    min_value=0.0,
    max_value=100.0, # Um maximo razoavel para dividendos anuais
    value=2.0,
    step=0.1,
    help="Percentual do patrimônio que será distribuído como dividendos anualmente."
    ) / 100 # Converte para decimal
taxa_rentabilidade_anual = st.sidebar.slider(
    "Taxa de Rentabilidade Anual Esperada (%)",
    min_value=0.0,
    max_value=100.0,
    value=8.0,
    step=0.1,
    help="Taxa de retorno anual líquida esperada dos investimentos."
) / 100  # Converte para decimal
taxa_inflacao_anual = st.sidebar.slider(
    "Taxa de Inflação Anual Esperada (%)",
    min_value=0.0,
    max_value=100.0,
    value=4.0,
    step=0.1,
    help="Taxa de inflação anual esperada para ajustar o poder de compra."
) / 100  # Converte para decimal
prazo_projecao_anos = st.sidebar.slider(
    "Prazo da Projeção (anos)",
    min_value=1,
    max_value=60,
    value=20,
    step=1,
    help="Número de anos para a projeção."
)
idade_atual = st.sidebar.number_input(
    "Idade Atual do Cliente",
    min_value=1,
    max_value=120,
    value=40,
    step=1,
    help="Idade atual do cliente para contexto da projeção."
)

# --- Função de Projeção Financeira ---
def realizar_projecao(
    patrimonio_inicial,
    aportes_mensais,
    taxa_rentabilidade_anual,
    taxa_inflacao_anual,
    taxa_dividendos_anual,
    prazo_projecao_anos,
    idade_atual
):
    data = []
    current_patrimony_nominal = patrimonio_inicial
    current_patrimony_nominal_sem_div = patrimonio_inicial # Adicione esta linha: Para simular cenário sem reinvestimento de dividendos

    for ano_projecao in range(1, prazo_projecao_anos + 1):
        idade_cliente = idade_atual + ano_projecao - 1

        # Aportes anuais
        aportes_anuais = aportes_mensais * 12

        # Calcular taxa mensal efetiva a partir da taxa anual (importante para aportes mensais)
        taxa_mensal_efetiva = (1 + taxa_rentabilidade_anual)**(1/12) - 1

        # 1. Rentabilidade do patrimônio inicial do período
        rentabilidade_patrimonio_inicial = current_patrimony_nominal * taxa_rentabilidade_anual

        # 2. Valor Futuro dos aportes mensais no ano
        # nf.fv(rate, nper, pmt, pv, when='end')
        # pmt é negativo porque é uma saída de caixa (investimento)
        # when='end' significa que os aportes são feitos no final de cada mês
        fv_aportes_ano = nf.fv(taxa_mensal_efetiva, 12, -aportes_mensais, 0, when='end')

        # 3. Juros gerados pelos aportes mensais no ano
        # É o Valor Futuro dos aportes menos o principal total aportado
        # Se a taxa de rentabilidade for 0, ensure rentabilidade_aportes_ano is 0 to avoid minor floating point inaccuracies
        if taxa_rentabilidade_anual == 0:
            rentabilidade_aportes_ano = 0
        else:
            rentabilidade_aportes_ano = fv_aportes_ano - aportes_anuais


        # Rentabilidade Bruta Total para o ano
        rentabilidade_bruta_anual = rentabilidade_patrimonio_inicial + rentabilidade_aportes_ano

        # Cálculo dos Dividendos e Reinvestimento
        dividendos_recebidos = current_patrimony_nominal * taxa_dividendos_anual

            # O valor dos dividendos é adicionado ao patrimônio atual antes do cálculo do próximo ano
            # Eles são considerados como parte da rentabilidade total para o cálculo nominal
            # Mas vamos adicioná-los separadamente aqui para fins de demonstração e para garantir que o patrimônio nominal
            # já inclua esse valor para a próxima iteração.

            # --- Cálculo para o cenário "sem dividendos reinvestidos" ---
            # Rentabilidade do patrimônio inicial do período para o cenário SEM DIVIDENDOS
        rentabilidade_patrimonio_inicial_sem_div = current_patrimony_nominal_sem_div * taxa_rentabilidade_anual
            # A rentabilidade dos aportes é a mesma, pois independe dos dividendos do patrimônio existente
        rentabilidade_bruta_anual_sem_div = rentabilidade_patrimonio_inicial_sem_div + rentabilidade_aportes_ano

            # Patrimônio Nominal no final do período para o cenário SEM DIVIDENDOS
        patrimonio_fim_nominal_sem_div = current_patrimony_nominal_sem_div + aportes_anuais + rentabilidade_bruta_anual_sem_div

            # --- Fim do cálculo para o cenário "sem dividendos reinvestidos" ---

            # Sua linha existente para o patrimônio COM dividendos reinvestidos:
        patrimonio_fim_nominal = current_patrimony_nominal + aportes_anuais + rentabilidade_bruta_anual + dividendos_recebidos      

        # Patrimônio Nominal no final do período
            # Atualiza o patrimônio nominal para o próximo ano (COM dividendos)
        current_patrimony_nominal = patrimonio_fim_nominal

            # Atualiza o patrimônio nominal para o próximo ano (SEM dividendos)
        current_patrimony_nominal_sem_div = patrimonio_fim_nominal_sem_div # Adicione esta linha        
        # Patrimônio Real no final do período (corrigido pela inflação acumulada)

        fator_inflacao_acumulada = (1 + taxa_inflacao_anual)**ano_projecao
        patrimonio_fim_real = patrimonio_fim_nominal / fator_inflacao_acumulada

        data.append({
            "Ano": ano_projecao,
            "Idade do Cliente": idade_cliente,
            "Patrimônio Início (R\$)": current_patrimony_nominal,
            "Aportes Anuais (R\$)": aportes_anuais,
            "Rentabilidade Bruta Anual (R\$)": rentabilidade_bruta_anual,
            "Dividendos Recebidos (R\$)": dividendos_recebidos,
            "Patrimônio Fim Nominal (c/ Div Reinvestidos) (R\$)": patrimonio_fim_nominal, # Renomeado
            "Patrimônio Fim Nominal (sem Div Reinvestidos) (R\$)": patrimonio_fim_nominal_sem_div, # NOVA LINHA
            "Patrimônio Fim Real (R\$)": patrimonio_fim_real
            })
        

        # Atualiza o patrimônio inicial para o próximo ano
        current_patrimony_nominal = patrimonio_fim_nominal

    df = pd.DataFrame(data)
    return df

# --- Área Principal de Exibição ---
st.header("Resultados da Projeção")

# Botão para gerar a projeção
if st.button("Gerar Projeção Financeira"):
    if patrimonio_inicial < 0 or aportes_mensais < 0 or prazo_projecao_anos <= 0:
        st.error("Por favor, insira valores válidos para Patrimônio Inicial, Aportes Mensais e Prazo de Projeção (devem ser não negativos).")
    else:
        projecao_df = realizar_projecao(
            patrimonio_inicial,
            aportes_mensais,
            taxa_rentabilidade_anual,
            taxa_inflacao_anual,
            taxa_dividendos_anual,
            prazo_projecao_anos,
            idade_atual
        )

        st.subheader("Tabela Detalhada da Projeção")
        # Exibe o DataFrame formatado
        st.dataframe(projecao_df.style.format({
            "Patrimônio Início (R\$)": "R\$ {:,.2f}",
            "Aportes Anuais (R\$)": "R\$ {:,.2f}",
            "Rentabilidade Bruta Anual (R\$)": "R\$ {:,.2f}",
            "Dividendos Recebidos (R\$)": "R\$ {:,.2f}",
            "Patrimônio Fim Nominal (c/ Div Reinvestidos) (R\$)": "R\$ {:,.2f}", # Renomeado
            "Patrimônio Fim Nominal (sem Div Reinvestidos) (R\$)": "R\$ {:,.2f}", # NOVA LINHA
            "Patrimônio Fim Real (R\$)": "R\$ {:,.2f}"
            }), use_container_width=True)

        st.subheader("Gráfico da Projeção Patrimonial")
            # Cria o gráfico interativo com Plotly
        fig = go.Figure()

            # Trace para Patrimônio Nominal (COM Dividendos Reinvestidos) - Antigo Patrimônio Nominal
        fig.add_trace(go.Scatter(
            x=projecao_df["Ano"],
            y=projecao_df["Patrimônio Fim Nominal (c/ Div Reinvestidos) (R\$)"], # Coluna renomeada
            mode="lines+markers",
            name="Patrimônio Nominal (c/ Div Reinvestidos)", # Nome do trace atualizado
            line=dict(color='gold') # Sugestão de cor para diferenciar
            ))

            # NOVO TRACE: Patrimônio Nominal (SEM Dividendos Reinvestidos)
        fig.add_trace(go.Scatter(
            x=projecao_df["Ano"],
            y=projecao_df["Patrimônio Fim Nominal (sem Div Reinvestidos) (R\$)"], # Nova coluna
            mode="lines+markers",
            name="Patrimônio Nominal (sem Div Reinvestidos)", # Novo nome
            line=dict(dash='dash', color='red') # Sugestão para linha tracejada e cor diferente
            ))

            # Trace para Patrimônio Real (já existente)
        fig.add_trace(go.Scatter(
            x=projecao_df["Ano"],
            y=projecao_df["Patrimônio Fim Real (R\$)"],
            mode="lines+markers",
            name="Patrimônio Real (corrigido pela inflação)",
            line=dict(color='green') # Sugestão de cor para diferenciar
            ))

        fig.update_layout(
            title="Evolução do Patrimônio ao Longo dos Anos",
            xaxis_title="Ano da Projeção",
            yaxis_title="Patrimônio (R\$)",
            hovermode="x unified",
            height=500,
            legend_title_text="Tipo de Patrimônio"
            )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sumário da Projeção")

        # Patrimônio final com dividendos reinvestidos
        final_nominal_com_div = projecao_df["Patrimônio Fim Nominal (c/ Div Reinvestidos) (R\$)"].iloc[-1]
        # Patrimônio final sem dividendos reinvestidos
        final_nominal_sem_div = projecao_df["Patrimônio Fim Nominal (sem Div Reinvestidos) (R\$)"].iloc[-1]
        # Patrimônio final real
        final_real = projecao_df["Patrimônio Fim Real (R\$)"].iloc[-1]

        st.write(f"**Patrimônio Final Projetado (Nominal, com Div. Reinvestidos):** R\$ {final_nominal_com_div:,.2f}")
        st.write(f"**Patrimônio Final Projetado (Nominal, sem Div. Reinvestidos):** R\$ {final_nominal_sem_div:,.2f}")
        st.write(f"**Patrimônio Final Projetado (Real, corrigido pela inflação):** R\$ {final_real:,.2f}")


st.markdown("---")
st.warning("⚠️ **Disclaimer:** As projeções financeiras são estimativas e não garantias de resultados futuros. Os valores apresentados dependem das premissas informadas e podem variar significativamente com as condições de mercado e alterações nos aportes ou taxas. Esta ferramenta é para fins educacionais e de planejamento geral. Recomenda-se sempre buscar aconselhamento profissional.")
