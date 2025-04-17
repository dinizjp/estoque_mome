# estoque_mome

Este projeto fornece um sistema de controle de estoque para lojas, permitindo gerenciar produtos, atualizar quantidades, registrar entradas, sair do estoque e monitorar alertas de validade.

## Sumário

- [Dependências e Instalação](#dependências-e-instalação)
- [Como Rodar e Testar](#como-rodar-e-testar)
- [Estrutura de Arquivos e Pastas](#estrutura-de-arquivos-e-pastas)

## Dependências e Instalação

Para executar o projeto, instale as dependências listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Certifique-se de configurar as credenciais do banco de dados PostgreSQL no arquivo `secrets.toml` ou por variáveis de ambiente.

## Como Rodar e Testar

1. Clone ou copie os arquivos do projeto.
2. Configure o arquivo `secrets.toml` com as credenciais de acesso ao banco.
3. Execute a aplicação Streamlit na página de acesso à loja:

```bash
streamlit run Acesso_a_Loja.py
```

Após acessar, navegue pelas páginas disponíveis para:
- Gerenciar o estoque atual (`pages_1_Estoque_Atual.py`)
- Registrar alertas de validade (`pages_2_Alerta_de_Validade.py`)
- Registrar entradas externas (`pages_3_Entrada_Externa.py`)

## Estrutura de Arquivos e Pastas

```
estoque_mome/
│
├── utils.py                     # Arquivo com funções de conexão e manipulação do banco
├── requirements.txt             # Dependências necessárias
├── README.md                    # Este arquivo
├── Acesso_a_Loja.py             # Página para selecionar a loja
└── pages/
    ├── 1_Estoque_Atual.py       # Controle de estoque atualizado e ajuste manual
    ├── 2_Alerta_de_Validade.py  # Registro de alertas de validade
    └── 3_Entrada_Externa.py     # Registro de entrada de produtos ao estoque
```

---

Este README oferece uma visão clara e objetiva do projeto, suas funcionalidades e como utilizá-lo. Para suporte ou dúvidas adicionais, consulte a documentação ou entre em contato com a equipe de desenvolvimento.