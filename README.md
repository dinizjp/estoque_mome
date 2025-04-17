Aqui está o README.md revisado para o projeto `estoque_mome`, agora incluí as informações adicionais sobre os arquivos que você forneceu. 

```markdown
# estoque_mome

Este projeto tem como objetivo fornecer um sistema de controle de estoque para lojas, permitindo gerenciar produtos, atualizar quantidades, registrar entradas e saídas, além de monitorar alertas de validade.

## Dependências e Instalação

Para rodar o projeto, é necessário instalar as seguintes dependências:

- streamlit==1.42.2
- pandas==2.2.2
- psycopg2-binary==2.9.10
- openpyxl==3.1.5 

Instale as dependências executando:

```bash
pip install -r requirements.txt
```

Certifique-se de configurar as variáveis de ambiente ou o arquivo `secrets.toml` com as credenciais do seu banco de dados PostgreSQL.

## Como Rodar e Testar

1. Clone o repositório ou copie os arquivos do projeto.
2. Configure o arquivo `secrets.toml` ou as variáveis de ambiente com as credenciais do banco de dados.
3. Execute o aplicativo Streamlit para uma das páginas:
```bash
streamlit run Acesso_a_Loja.py
```

Após o acesso à loja, você poderá navegar pelas diferentes páginas para gerenciar o estoque:

- Estoque Atual (`pages_1_Estoque_Atual.py`)
- Alerta de Validade (`pages_2_Alerta_de_Validade.py`)
- Entrada Externa (`pages_3_Entrada_Externa.py`)

## Estrutura e Arquivos Principais

```
estoque_mome/
│
├── utils.py                 # Funções auxiliares para conexão e manipulação do banco de dados
├── requirements.txt         # Dependências do projeto
├── README.md                # Este arquivo
├── Acesso_a_Loja.py         # Página de acesso à loja
└── pages/
    ├── 1_Estoque_Atual.py   # Controle de estoque atualizado, permitindo atualizações manuais e via planilha
    ├── 2_Alerta_de_Validade.py  # Registro de alertas de validade dos produtos
    └── 3_Entrada_Externa.py  # Registro de entrada de novos produtos ao estoque
```

Navegue pelo menu do Streamlit após rodar para interagir com as funcionalidades do sistema.

---

Caso tenha dúvidas ou precise de suporte, consulte a documentação ou entre em contato com a equipe de desenvolvimento.
```

Esse README atualizado reflete a estrutura completa do projeto e descreve brevemente o propósito de cada arquivo relevante. Se precisar de mais informações ou alterações, estou à disposição!